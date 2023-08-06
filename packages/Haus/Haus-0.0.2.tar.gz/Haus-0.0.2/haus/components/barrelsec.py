""".. _BarrelSecurityComponent:

``barrel`` -- Authentication and Authorization
==============================================

**Component name:** ``barrel``

Provides basic and form based auth.

TODO: Describe all sorts of ways to customize this.
TODO: How should this be exposed more cleanly? User object?
"""

from pkg_resources import Requirement, resource_filename

from barrel import basic, form, combo, roles, cooper

from haus.components.abstract import Component, update_wrapper
from haus.core import tack

class BarrelSecurityComponent(Component):

    consumes = ['invalidate_session', 'get_session']
    provides = ['valid_user', 'user_roles', 'get_user', 
                'login', 'logout', 'login_page', 'logout_page',
                'need_auth', 'denied']

    def __init__(self, wrk):
        """."""
        session_config = wrk.config.get('sessions', {})
        self.session_key = session_config.get('environ_key')
        config = wrk.config.get('barrel', {})
        self.user_key = config.get('user_key', wrk.package_name + ".user")
        locations = wrk.functions['get_locations']({})
        prefix = wrk.config['app']['prefix']
        self.login_location = locations.get('login', prefix + '/login/')
        self.landing_location = locations.get('landing', prefix + '/')
        self.realm = config.get('realm', wrk.package_name)
        self.secrets = wrk.config.get('user.secrets', {})
        self.roles = wrk.config.get('user.roles', {})
        wrk.functions['valid_user'] = self.valid_user
        wrk.functions['user_roles'] = self.user_roles
        wrk.functions['get_user'] = self.get_cached_username
        wrk.functions['login'] = self.cache_username
        wrk.functions['logout'] = self.logout
        wrk.functions['login_page'] = self.login_page
        wrk.functions['logout_page'] = self.logout_page
        self.init_authn(wrk)
        self.init_authz(wrk)
        self.init_templates(wrk)

    def init_templates(self, wrk):
        # TODO: These could also be tuples of package, relative_path
        #       to enable template sharing via pkg_resources?
        # For now, relative path is in this package, otherwise absolute.
        config = wrk.config.get('barrel.templates', {})
        haus_resource = wrk.haus_resource
        self.template_login = config.get(
            'login',
            resource_filename(haus_resource, 'haus/html/login.html')
        )
        self.template_logout = config.get(
            'logout',
            resource_filename(haus_resource, 'haus/html/logout.html')
        )
        self.template_denied = config.get(
            'denied',
            resource_filename(haus_resource, 'haus/html/denied.html')
        )
        self.layout = config.get(
            'layout',
            wrk.pdfilename('html/_layouts/default.html')
        )


    def __call__(self, wrk, *args, **kwargs):
        """."""
        wrk.functions['need_auth'] = wrk.stackify(self.need_auth)
        wrk.functions['denied'] = wrk.stackify(self.access_denied)

        #auth_options = copy(wrk.config['barrel'])
        # for auth options see barrel docs
        config = wrk.config.get('barrel', {})
        auth_options = dict(
            realm=config.get('realm', wrk.package_name),
        )
        auth_options.update(kwargs)
        authn = self.authn(**auth_options)
        authz = self.authz(**auth_options)

        def middleware(app):
            newapp = authn(authz(app))
            return update_wrapper(newapp, app)

        return middleware

    def valid_user(self, username, password):
        return username and password and \
            self.secrets.get(username) == password

    def security_mixin_factory(self, wrk):
        """Return a class that implements user validation."""
        outer = self

        class SecurityMixIn(object):
            """From haus.factories.BarrelSecurityFactory."""
            def valid_user(self, username, password):
                """Validate user with framework instance given to factory."""
                return wrk.functions['valid_user'](username, password)

        return SecurityMixIn

    def basic_auth_factory(self, wrk):
        """Return a custom barrel-based auth class for the factory instance."""
        outer = self

        class HausBasicAuth(outer.security_mixin, basic.BasicAuth):
            """From haus.factories.BarrelSecurityFactory."""
            pass

        return HausBasicAuth

    def form_auth_factory(self, wrk):
        """Return a custom barrel-based auth class."""
        outer = self

        class HausFormAuth(outer.security_mixin, form.FormAuth):
            """From haus.factories.BarrelSecurityComponent."""

            def username_and_passord(self, environ):
                """Always return None."""
                return None

            def not_authenticated(self, environ, start_response):
                """Use WSGI login app from factory instance's config."""
                return wrk.functions['need_auth'](environ, start_response)

            def cache_username(self, environ, username):
                """Use factory instance's cache_username method."""
                return outer.cache_username(environ, username)

            def get_cached_username(self, environ):
                """Use factory instance's get_cached_username method."""
                return outer.get_cached_username(environ)

        return HausFormAuth

    def combo_auth_factory(self, wrk):
        """Return a custom barrel-based auth class."""
        outer = self

        class HausComboAuth(combo.BasicFormAuth):
            """From haus.factories.BarrelSecurityComponent."""

            basic_auth = outer.basic_auth
            form_auth = outer.form_auth

        return HausComboAuth

    def roles_authz_factory(self, wrk):
        """Return a custom barrel-based auth class for the factory instance."""
        outer = self

        class HausRoles(roles.RolesAuthz):
            """From haus.factories.BarrelSecurityFactory."""

            def user_roles(self, username):
                """Delegate to framework instance."""
                return wrk.functions['user_roles'](username)

            def not_authorized(self, environ, start_response):
                """Use WSGI denied app from framework."""
                return wrk.functions['denied'](environ, start_response)

        return HausRoles

    def init_authn(self, wrk):
        """Set up authentication middleware using factories above."""
        self.security_mixin = self.security_mixin_factory(wrk)
        self.basic_auth = self.basic_auth_factory(wrk)
        self.form_auth = self.form_auth_factory(wrk)
        self.combo_auth = self.combo_auth_factory(wrk)
        self.authn = cooper.decorize(self.combo_auth)
        
    def init_authz(self, wrk):
        """Set up authorization middleware using factories above."""
        self.roles_authz = self.roles_authz_factory(wrk)
        self.authz = cooper.decorize(self.roles_authz)

    def cache_username(self, environ, username):
        """Store the username in a session dict if found.
        
        Also populates REMOTE_USER.
        """
        environ['REMOTE_USER'] = username
        session = environ['haus.functions']['get_session'](environ)
        if session is not None:
            session[self.user_key] = username

    def get_cached_username(self, environ):
        """Look for the username in the session if found.
        
        Also populates REMOTE_USER if it can.
        """
        session = environ['haus.functions']['get_session'](environ)
        if session is not None:
            return session.get(self.user_key)
        else:
            return None

    def user_roles(self, username):
        """Look in config for roles."""
        return self.roles.get(username, [])

    def logout(self, environ):
        """In this case just invalidate the session."""
        return environ['haus.functions']['invalidate_session'](environ)

    @tack(['sessions', 'yaro'])
    def need_auth(self, req):
        """Redirect to login with attempted URI in query string."""
        req.res.headers['Content-type'] = 'text/html'
        return req.redirect(req.uri(self.login_location)
                            +'?uri='+req.uri(with_qs=True))

    @tack(['sessions', 'yaro'])
    def login_page(self, req):
        """."""
        username = req.form.get('username', '')
        password = req.form.get('password', '')
        funcs = req.environ['haus.functions']
        valid_user = funcs['valid_user']
        login = funcs['login']
        get_user = funcs['get_user']
        if req.method == 'POST':
            if valid_user(username, password):
                message = "Login Success!"
                login(req.environ, username)
            else:
                message = "Login failed"
        else:
            message = "Please login"
        _username = get_user(req.environ)
        if _username:
            alternate = req.query.get(
                'uri', 
                req.uri(self.landing_location)
            )
            req.redirect(req.form.get('uri', alternate))
        template_vars = dict(
            message=message,
            username=username,
            layout=self.layout
        )
        render = req.environ['haus.functions']['render_view']
        req.res.headers['Content-type'] = 'text/html'
        return render(self.template_login, template_vars)

    @tack(['sessions', 'yaro'])
    def logout_page(self, req):
        template_vars = dict(
            layout=self.layout
        )
        req.ff['logout'](req.environ)
        render = req.environ['haus.functions']['render_view']
        req.res.headers['Content-type'] = 'text/html'
        return render(self.template_logout, template_vars)

    @tack(['sessions', 'yaro'])
    def access_denied(self, req):
        get_user = req.environ['haus.functions']['get_user']
        template_vars = dict(
            username=get_user(req.environ),
            layout=self.layout
        )
        render = req.environ['haus.functions']['render_view']
        req.res.headers['Content-type'] = 'text/html'
        return render(self.template_denied, template_vars)

