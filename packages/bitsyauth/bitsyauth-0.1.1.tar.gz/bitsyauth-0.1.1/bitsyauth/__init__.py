import markup
import random
import re
import sys

from cStringIO import StringIO
from markup.form import Form
from paste.auth import basic, cookie, digest, form, multi, auth_tkt
from webob import Request, Response, exc

try:
    from skimpyGimpy import skimpyAPI
    CAPTCHA = True
except ImportError:
    CAPTCHA = False

dictionary_file = '/usr/share/dict/american-english'

def random_word():
    """generate a random word for CAPTCHA auth"""
    min_length = 5 # minimum word length
    if not globals().has_key('dictionary'):
        # read the dictionary -- this may be platform dependent
        # XXX could use a backup dictionary
        _dictionary = file(dictionary_file).readlines()
        _dictionary = [ i.strip() for i in _dictionary ]
        _dictionary = [ i.lower() for i in _dictionary
                        if i.isalpha() and i > min_length ]
        globals()['dictionary'] = _dictionary
    return random.Random().choice(dictionary)

class BitsyAuthInnerWare(object):
    """inner auth;  does login checking"""

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
        self.captcha = True
        self.urls = { 'login': '/login', 'join': '/join', }
        self.keys = {} # keys, words for CAPTCHA request

        self.content_type = { 'image_captcha': 'image/png',
                              'wav_captcha': 'audio/wav' }

        if newuser:
            self.newuser = newuser
        else:
            self.urls.pop('join') # don't do joining

        # WSGI app securely wrapped
        self.wrapped_app = self.security_wrapper()

        if not CAPTCHA:
            self.captcha = False
        
    ### WSGI/HTTP layer

    def __call__(self, environ, start_response):

        self.request = Request(environ)
        self.request.path_info = self.request.path_info.rstrip('/')
        self.redirect_to = self.request.script_name 

        # URLs intrinsic to BitsyAuth
        if self.request.path_info == '/logout':
            response = self.redirect()
            return response(self.request.environ, start_response)

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
                response = self.request.get_response(self.wrapped_app)

        user = self.request.environ.get('REMOTE_USER')
        if user:
            self.request.environ['paste.auth_tkt.set_user'](user)

        return response(self.request.environ, start_response)

    ### authentication function

    def digest_authfunc(self, environ, realm, user):
        return self.passwords()[user] # passwords stored in m5 digest

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

    ### methods dealing with intrinsic URLs

    def url_lookup(self):
        retval = dict([ (value, key) for key, value
                        in self.urls.items() ])
        if self.captcha:
            retval.update(dict([(('/join/%s.png' % key), 'image_captcha')
                                for key in self.keys]))
        return retval
        
    def get_response(self, text, content_type='text/html'):
        res = Response(content_type=content_type, body=text)
        res.content_length = len(res.body)
        return res

    def make_response(self):
        url_lookup = self.url_lookup()
        path = self.request.path_info
        assert path in url_lookup

        # login and join shouldn't be accessible when logged in
        if self.request.environ.get('REMOTE_USER'):
            return self.redirect("You are already logged in")

        handler = url_lookup[path]
        function = getattr(self, handler)

        if self.request.method == 'GET':
            # XXX could/should do this with decorators            
            return self.get_response(function(wrap=True),
                                     content_type=self.content_type.get(handler,'text/html'))
        if self.request.method == 'POST':
            post_func = getattr(self, handler + "_post")
            errors = post_func()
            if errors:
                return self.get_response(function(errors=errors, wrap=True))
            else:
                location = self.request.POST.get('referer')
                return self.redirect("Welcome!", location=location)

    def redirect(self, message='', location=None):
        """redirect from instrinsic urls"""
        return exc.HTTPSeeOther(message, location=location or self.redirect_to)

    def image_captcha(self, wrap=True):
        """return data for the image"""
        key = self.request.path_info.split('/join/')[-1]
        key = int(key.split('.png')[0])
        return skimpyAPI.Png(self.keys[key], scale=3.0).data()
                
    ### forms and their display methods

    ### login

    def login_form(self, referer=None, action=None):
        form = Form(action=action or '', submit='Login')
        form.add_element('textfield', 'Name', input_name='username')
        form.add_element('password', 'Password', input_name='password')
        if referer:
            form.add_element('hidden', 'referer', value=referer)
        return form

    def login(self, errors=None, wrap=False, action=None):
        """login div"""
        referer = None
        if hasattr(self, 'request'):
            referer = self.request.referer
        form = self.login_form(action=action, referer=referer)
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

    def login_post(self):
        """handle a login POST request"""
        user = self.request.POST.get('username')
        password = self.request.POST.get('password')
        passwords = self.passwords()
        error = False
        if user not in passwords:
            error = True
        else:
            error = not self.authfunc(self.request.environ, user, password)
        if error:
            return { 'Name': 'Wrong username or password' }
        self.request.environ['REMOTE_USER'] = user
        self.request.environ['paste.auth_tkt.set_user'](user)

    ### join

    def captcha_pre(self, word, key):
        """CAPTCHA with pre-formatted text"""
        return skimpyAPI.Pre(word, scale=1.2).data()

    def captcha_png(self, word, key):
        """CAPTCHA with a PNG image"""
        return markup.image('/join/%s.png' % key)

    def join_form(self):
        captcha = ''
        if self.captcha:
            # data for CAPTCHA
            key = random.Random().randint(0, sys.maxint)
            word = random_word()

            self.keys[key] = word

            captcha = StringIO()

            captcha_text = "Please type the word below so I know you're not a computer:"
            captcha_help = "(please %s if the page is unreadable)" % markup.link('/join?captcha=image', 'go here')

            print >> captcha, markup.p('%s<br/> %s' % (captcha_text, 
                                                       markup.i(captcha_help)))

            # determine type of CAPTCHA
            captchas = ' '.join(self.request.GET.getall('captcha'))
            if not captchas:
                captchas = 'pre'
                
            captcha_funcs=dict(pre=self.captcha_pre,
                               image=self.captcha_png,)
            captchas = [ captcha_funcs[i](word, key) for i in captchas.split()
                         if i in captcha_funcs ]
            captchas = '\n'.join([markup.p(i) for i in captchas])
            print >> captcha, captchas
            
            print >> captcha, markup.p(markup.input(None, **dict(name='captcha', type='text')))
            
            captcha = captcha.getvalue()

        form = Form(action=self.urls['join'], submit='Join', post_html=captcha)
        form.add_element('textfield', 'Name')
        form.add_password_confirmation()
        form.add_element('hidden', 'key', value=str(key))
        return form

    def join(self, errors=None, wrap=False):
        """join div or page if wrap"""
        form = self.join_form()
        retval = markup.div(form(errors))
        if wrap:
            pagetitle = title = 'join'
            if self.site:
                pagetitle = '%s - %s' % (title, self.site)
            if self.captcha:
                errors = errors or {}
                captcha_err = errors.get('CAPTCHA', '')
                if captcha_err:
                    captcha_err = markup.p(markup.em(captcha_err),
                                           **{'class': 'error'})
            retval = markup.wrap(markup.h1(title.title()) + captcha_err + retval,
                                 pagetitle=pagetitle)
        return retval

    def join_post(self):
        """handle a join POST request"""
        form = self.join_form()
        errors = form.validate(self.request.POST)

        # validate captcha
        if CAPTCHA:
            key = self.request.POST.get('key')
            try:
                key = int(key)
            except ValueError:
                key = None
            if not key:
                errors['CAPTCHA'] = 'Please type the funky looking word'
            word = self.keys.pop(key, None)
            if not word:
                errors['CAPTCHA'] = 'Please type the funky looking word'
            if word != self.request.POST.get('captcha','').lower():
                errors['CAPTCHA'] = 'Sorry, you typed the wrong word'
        
        name = self.request.POST.get('Name', '')
        if not name:
            if not errors.has_key('Name'):
                errors['Name'] = []
            errors['Name'].append('Please enter a user name')
        if name in self.passwords():
            if not errors.has_key('Name'):
                errors['Name'] = []
            errors['Name'].append('The name %s is already taken' % name)

        if not errors: # create a new user
            self.newuser(name,
                         self.hash(name, self.request.POST['Password']))
            self.request.environ['REMOTE_USER'] = name # login the new user
            self.request.environ['paste.auth_tkt.set_user'](name)
        
        return errors

class BitsyAuth(object):
    """outer middleware for auth;  does the cookie handling and wrapping"""
    
    def __init__(self, app, global_conf, passwords, newuser, site='', secret='secret'):
        self.app = app
        self.path = '/logout'
        self.cookie = '__ac'
        auth = BitsyAuthInnerWare(app, passwords=passwords, newuser=newuser, site=site)
        self.hash = auth.hash
        # paste.auth.cookie
        #        self.cookie_handler = cookie.middleware(auth, cookie_name=self.cookie, timeout=90) # minutes

        # paste.auth.auth_tkt
        self.cookie_handler = auth_tkt.make_auth_tkt_middleware(auth, global_conf, secret, cookie_name=self.cookie, logout_path='/logout')

    def __call__(self, environ, start_response):
        if environ['PATH_INFO'] == '/logout':
            pass        
        return self.cookie_handler(environ, start_response)

    def logout(self, environ):
        req = Request(environ)
        keys = [ 'REMOTE_USER' ]
        #        keys = [ 'REMOTE_USER', 'AUTH_TYPE', 'paste.auth.cookie', 'paste.cookies', 'HTTP_COOKIE' ]  # XXX zealous kill
        for key in keys:
            req.environ.pop(key, None)

        body = '<html><head><title>logout</title></head><body>logout</body></html>'
        res = Response(content_type='text/html', body=body)
        res.content_length = len(res.body)
        req.cookies.pop(self.cookie, None)
        res.delete_cookie(self.cookie)
        res.unset_cookie(self.cookie)
        return res(environ, start_response)
        
