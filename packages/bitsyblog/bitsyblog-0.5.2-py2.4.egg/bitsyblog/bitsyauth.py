import markup
import re

from markup.form import Form
from paste.auth import basic, cookie, digest, form, multi
from webob import Request, Response, exc

class BitsyAuth(object):
    """note that paths must be specified in order in precedence"""

    def __init__(self, app, passwords, newuser=None, site=None, realm=None):
        """a simple reimplementation of auth
        * app: the WSGI app to be wrapped
        * passwords: callable that return a dictionary of {'user': 'password'}
        * newuser: callable to make a new user, taking name + pw
        * site: name of the site
        * realm: realm for HTTP digest authentication
        """

        self.app = app
        self.passwords = passwords
        self.site = site or ''
        self.realm = realm or self.site

        self.redirect_to = '/' # redirect to site root
        
        self.urls = { 'login': '/login', 'join': '/join', 'logout': '/logout' }

        # WSGI app securely wrapped
        self.wrapped_app = self.security_wrapper()

        if newuser:
            self.newuser = newuser
        else:
            self.urls.pop('join') # don't do joining

    ### WSGI/HTTP layer

    def __call__(self, environ, start_response):

        self.request = Request(environ)

        # URLs intrinsic to BitsyAuth
        if self.request.path_info in self.url_lookup():
            response = self.make_response()
            return response(self.request.environ, start_response)

        # digest auth
        if self.request.headers.has_key('Authorization'):
            return self.wrapped_app(self.request.environ, start_response)

        response = self.request.get_response(self.app)
        # respond to 401s
        if response.status_int == 401: # Unauthorized
            if self.request.environ.get('REMOTE_USER'):
                return exc.HTTPForbidden()
            else:
                return self.wrapped_app(self.request.environ, start_response)

        return response(self.request.environ, start_response)

    ### authentication function

    def digest_authfunc(self, environ, realm, user):
        return self.passwords()[user]
        digested = digest.digest_password(realm, user, self.passwords()[user])
        return digested

    def authfunc(self, environ, user, password):
        return self.hash(user, password) == self.passwords()[user]

    def hash(self, user, password):
        # use md5 digest for now
        return digest.digest_password(self.realm, user, password)

    def security_wrapper(self):
        """return the app securely wrapped"""

        multi_auth = multi.MultiHandler(self.app)

        # digest authentication
        multi_auth.add_method('digest', digest.middleware,
                              self.realm, self.digest_authfunc)
        multi_auth.set_query_argument('digest', key='auth')

        # form authentication
        template = self.login(wrap=True, action='%s')
        multi_auth.add_method('form', form.middleware, self.authfunc,
                              template=template)
        multi_auth.set_default('form')
        
        return multi_auth

        # might have to wrap cookie.middleware(BitsyAuth(multi(app))) ::shrug::
        return cookie.middleware(multi_auth)

                
    def url_lookup(self):
        # could cache
        return dict([ (value, key) for key, value
                      in self.urls.items() ]) # bijection

    ### methods dealing with intrinsic URLs

    def get_response(self, text, type='text/html'):
        res = Response(content_type=type, body=text)
        res.content_length = len(res.body)
        return res

    def make_response(self):
        url_lookup = self.url_lookup()
        path = self.request.path_info
        assert path in url_lookup
        if self.request.method == 'GET':
            # XXX could/should do this with decorators
            
            if path == '/logout':
                return self.logout()
                
            
            function = getattr(self, url_lookup[path])
            return self.get_response(function(wrap=True))
        if self.request.method == 'POST':
            if path == '/join':
                errors = self.join_post()
                if errors:
                    return self.get_response(self.join(errors=errors,
                                                       wrap=True))
                else:
                    return self.redirect("Welcome!")

    def redirect(self, message=''):
        """redirect from instrinsic urls"""
        return exc.HTTPSeeOther(message, location=self.redirect_to)
        

    ### logout
    def logout(self):
        """logout a user logged in via cookie"""
        keys = [ 'REMOTE_USER' ]
        for key in keys:
            self.request.environ.pop(key, None)
        return self.redirect("You are now logged out")
        
    ### forms and their display methods

    ### login

    def login_form(self, referer=None, action=None):
        if action is None:
            action = self.urls['login']
        form = Form(action=action, submit='Login')
        form.add_element('textfield', 'Name', input_name='username')
        form.add_element('password', 'Password', input_name='password')
        if referer is not None:
            form.add_element('hidden', 'referer', value=referer)
        return form

    def login(self, errors=None, wrap=False, action=None):
        """login div"""
        form = self.login_form(action=action)
        join = self.urls.get('join')
        retval = form(errors)
        if join:        
            retval += '<br/>\n' + markup.a('join', href="%s" % join)
        retval = markup.div(retval)
        if wrap:
            title = 'login'
            if self.site:
                pagetitle = '%s - %s' % (title, self.site)
            retval = markup.wrap(markup.h1(title.title()) + retval,
                                 pagetitle=pagetitle)

        return retval

    ### join

    def join_form(self):
        # XXX could add checking here....email confirmation, captcha, etc
        form = Form(action=self.urls['join'], submit='Join')
        form.add_element('textfield', 'Name')
        form.add_password_confirmation()
        return form

    def join(self, errors=None, wrap=False):
        """join div or page if wrap"""
        form = self.join_form()
        retval = markup.div(form(errors))
        if wrap:
            pagetitle = title = 'join'
            if self.site:
                pagetitle = '%s - %s' % (title, self.site)
            retval = markup.wrap(markup.h1(title.title()) + retval,
                                 pagetitle=pagetitle)
        return retval

    def join_post(self):
        """handle a join POST request"""
        form = self.join_form()
        errors = form.validate(self.request.POST)
        name = self.request.POST.get('Name', '')
        if name in self.passwords():
            if not errors.has_key('Name'):
                errors['Name'] = []
            errors['Name'].append('The name %s is already taken' % name)

        if not errors: # create a new user
            self.newuser(name,
                         self.hash(name, self.request.POST['Password']))
            self.request.environ['REMOTE_USER'] = name # login the new user
        
        return errors
