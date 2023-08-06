#--
# Copyright (c) 2008, 2009 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

"""A ``WSGIApp`` object is an intermediary object between a publisher and the
root component of the application

A ``WSGIApp`` conforms to the WSGI interface and has a component factory. So,
each time the ``WSGIApp`` receives a request without a session id or with an
expired session id, it creates a new root component and a new session.
"""
from __future__ import with_statement

import webob
from webob import exc, acceptparse

from nagare import component, presentation, serializer, database, top, security
from nagare.security import dummy_manager
from nagare.callbacks import Callbacks, CallbackLookupError
from nagare.namespaces import xhtml

from nagare.sessions.common import ExpirationError

# ---------------------------------------------------------------------------

class MIMEAcceptWithoutWildcards(acceptparse.Accept):
    def _match(self, item, match):
        if '*' in item:
            return False
        return super(MIMEAcceptWithoutWildcards, self)._match(item, match)

# ---------------------------------------------------------------------------

class WSGIApp(object):
    def __init__(self, root_factory, metadatas=None):
        """Initialization

        In:
          - ``root_factory`` -- function to create the application root component
          - ``metadatas`` -- the SQLAlchemy metadata objects
        """
        self.root_factory = root_factory
        self.metadatas = metadatas or []

        self.static_url = ''
        self.static_path = ''
        self.redirect_after_post = False
        self.always_html = True

        self.security = dummy_manager.Manager()

    def set_config(self, config_filename, config, error, static_path, static_url, publisher):
        """Read the configuration parameters

        In:
          - ``config_filename`` -- the path to the configuration file
          - ``config`` -- the ``ConfigObj`` object, created from the configuration file
          - ``error`` -- the function to call in case of configuration errors
          - ``static_path`` -- the directory where the static contents of the application
            are located
          - ``static_url`` -- the url of the static contents of the application
          - ``publisher`` -- the publisher of the application
        """
        self.static_path = static_path
        self.static_url = static_url

        self.redirect_after_post = config['application']['redirect_after_post']
        self.always_html = config['application']['always_html']

    def start(self, sessions):
        """Call after each process start

        In:
          - ``sessions`` -- the sessions manager for this application
        """
        self.sessions = sessions

    # -----------------------------------------------------------------------

    def on_bad_http_method(self, request, response):
        """A HTTP request other than a GET or PUT was received

        In:
          - ``request`` -- the web request object
          - ``response`` -- the web response object

        Return:
          - raise a ``webob.exc`` object, used to generate the response to the browser
        """
        raise exc.HTTPMethodNotAllowed()

    def on_incomplete_url(self, request, response):
        """An URL without an application name was received

        In:
          - ``request`` -- the web request object
          - ``response`` -- the web response object

        Return:
          - raise a ``webob.exc`` object, used to generate the response to the browser
        """
        raise exc.HTTPMovedPermanently(add_slash=True)

    def on_session_expired(self, request, response):
        """The session id received is invalid

        In:
          - ``request`` -- the web request object
          - ``response`` -- the web response object

        Return:
          - raise a ``webob.exc`` object, used to generate the response to the browser
        """
        raise exc.HTTPMovedPermanently()

    def on_back(self, request, response, h, output):
        """The user used the back button

        In:
          - ``request`` -- the web request object
          - ``response`` -- the web response object
          - ``h`` -- the current renderer
          - ``output`` -- the tree for the refreshed page

        Return:
          - a tree
        """
        return output
    
    def on_callback_lookuperror(self, request, response, async):
        """
        In:
          - ``request`` -- the web request object
          - ``response`` -- the web response object
          - ``async`` -- is an XHR request ?
          
        """
        if not async:
            raise

        # As the XHR requests use the same continuation, a callback
        # can be not found (i.e deleted by a previous XHR)
        # In this case, do nothing                     
        return lambda h: ''
    
    def on_after_post(self, request, response, ids):
        """Generate a redirection after a POST

        In:
          - ``request`` -- the web request object
          - ``response`` -- the web response object
          - ``ids`` -- identifiers to put into the generated redirection URL

        Return:
          - a ``webob.exc`` object, used to generate the response to the browser
        """
        return exc.HTTPSeeOther(location=request.path_url + '?' + '&'.join(ids))

    # -----------------------------------------------------------------------

    def create_root(self):
        """Create the application root component

        Return:
          - the root component
        """
        return self.root_factory()

    def create_renderer(self, async, session, request, response, callbacks):
        """Create the initial renderer (the root of all the used renderers)

        In:
          - ``async`` -- is an XHR request ?
          - ``session`` -- the session
          - ``request`` -- the web request object
          - ``response`` -- the web response object
          - ``callbacks`` -- object to register the callbacks
        """
        renderer_factory = xhtml.AsyncRenderer if async else xhtml.Renderer
        return renderer_factory(
                                None,
                                session,
                                request, response,
                                callbacks,
                                self.static_url, self.static_path,
                                request.script_name
                               )

    def start_request(self, root, request, response):
        """A new request is received, setup its dedicated environment

        In:
          - ``root`` -- the application root component
          - ``request`` -- the web request object
          - ``response`` -- the web response object
        """
        security.set_manager(self.security) # Set the security manager
        security.set_user(self.security.create_user(request, response)) # Create the User object

    # Processing phase
    def _phase1(self, params, callbacks):
        """Phase 1 of the request processing:

          - The callbacks are processed
          - The objects graph can be modified

        In:
          - ``params`` -- parameters received into the request
          - ``callbacks`` -- the registered callbacks

        Return:
          - function to render the objects graph or ``None``
        """
        return callbacks.process_response(params)

    # Rendering phase
    def _phase2(self, request, response, output, is_xhr):
        """Final step of the phase 2

        Phase 2 of the request processing:

          - The object graph is rendered
          - No modification of the objects is allowed

        In:
          - ``session`` -- the session
          - ``request`` -- the web request object
          - ``output`` -- the rendered tree
          - ``is_xhr`` -- is the request a XHR request ?

        Return:
          - the content to send back to the browser
        """
        response.body = serializer.serialize(output, request, response, not is_xhr)
        response.charset = 'utf-8'

    def __call__(self, environ, start_response):
        """WSGI interface

        In:
          - ``environ`` -- dictionary of the received elements
          - ``start_response`` -- callback to send the headers to the browser

        Return:
          - the content to send back to the browser
        """
        # Create the ``WebOb`` request and response objects
        # -------------------------------------------------

        request = webob.Request(environ, charset='utf-8')
        response = webob.Response(headerlist=[])
        
        accept = MIMEAcceptWithoutWildcards('Accept', 'text/html' if self.always_html else str(request.accept))
        response.xhtml_output = accept.best_match(('text/html', 'application/xhtml+xml')) == 'application/xhtml+xml'

        xhr_request = request.is_xhr or ('_a' in request.params)

        session = None

        # Create a database transaction for each request
        with database.session.begin():
            try:
                # Phase 1
                # -------

                # Test the request validity
                if not request.path_info:
                    self.on_incomplete_url(request, response)

                try:
                    session = self.sessions.get(request, response)
                except ExpirationError:
                    self.on_session_expired(request, response)

                if session.is_new:
                    # A new session is created
                    root = self.create_root()   # Create a new application root component
                    callbacks = Callbacks()     # Create a new callbacks registry
                else:
                    # An existing session is used, retrieve the application root component
                    # and the callbacks registry
                    (root, callbacks) = session.data

                request.method = request.params.get('_method', request.method)
                if not session.is_new and request.method not in ('GET', 'POST'):
                    self.on_bad_http_method(request, response)

                self.start_request(root, request, response)

                url = request.path_info.strip('/')
                if session.is_new and url:
                    # If a URL is given, initialize the objects graph with it
                    presentation.init(root, tuple([u.decode('utf-8') for u in url.split('/')]), None, request.method, request)

                try:
                    render = self._phase1(request.params, callbacks)
                except CallbackLookupError:
                    render = self.on_callback_lookuperror(request, response, xhr_request)
            except exc.HTTPException, response:
                # When a ``webob.exc`` object is raised during phase 1, skip the
                # phase 2 and use it as the response object
                pass
            else:
                # Phase 2
                # -------

                # If the ``redirect_after_post`` parameter of the ``[application``
                # section is `True`` (the default), conform to the PRG__ pattern
                #
                # __ http://en.wikipedia.org/wiki/Post/Redirect/GetPRG

                try:
                    if (request.method == 'POST') and not xhr_request and self.redirect_after_post:
                        store_new_cont = False
                        response = self.on_after_post(request, response, session.sessionid_in_url(request, response))
                    else:
                        store_new_cont = not xhr_request

                        # Create a new renderer
                        renderer = self.create_renderer(xhr_request, session, request, response, callbacks)
                        # If the phase 1 has returned a render function, use it
                        # else, start the rendering by the application root component
                        output = render(renderer) if render else root.render(renderer)

                        if session.back_used:
                            output = self.on_back(request, response, renderer, output)

                        if not xhr_request:
                            output = top.wrap(response.content_type, renderer, output)

                        self._phase2(request, response, output, render is not None)

                        if not xhr_request:
                            callbacks.clear_not_used(renderer._rendered)

                    # Store the session
                    session.data = (root, callbacks)
                    self.sessions.set(session, store_new_cont)

                    security.get_manager().end_rendering(request, response, self.sessions, session)
                except exc.HTTPException, response:
                    # When a ``webob.exc`` object is raised during phase 2, stop immediatly
                    # use it as the response object
                    pass
            finally:
                if session:
                    session.lock.release()

        return response(environ, start_response)

# ---------------------------------------------------------------------------

def create_WSGIApp(app, metadata=None, with_component=True):
    """Helper function to create a WSGIApp

    If ``app`` is not a ``WSGIApp``, it's wrap into a ``WSGIApp``. And, if
    ``with_component`` is True, each time a new root object is created, it's
    automatically wrap into a ``component.Component``.

    In:
      - ``app`` -- the application root component factory
      - ``with_component`` -- wrap a new root object into a component
    """
    if not isinstance(app, WSGIApp):
        if with_component:
            def wrap_in_component(factory):
                o = factory()
                if not isinstance(o, component.Component):
                    o = component.Component(o)
                return o
            app = lambda app=app: wrap_in_component(app)

        app = WSGIApp(app, metadata)

    return app
