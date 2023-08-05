import authkit.authenticate
from bitsyauth import BitsyAuth
from bitsyblog import BitsyBlog
from paste.auth import form, cookie
from paste.httpexceptions import HTTPExceptionHandler

def factory(global_conf, **app_conf):

    config = [ 'file_dir', 'date_format', 'subject', 'n_links' ]
    key_str = 'bitsyblog.%s'
    args = dict([ (key, app_conf[ key_str % key]) for key in config
                  if app_conf.has_key(key_str % key) ])
    app = BitsyBlog(**args)
    auth = BitsyAuth(HTTPExceptionHandler(app),
                     passwords=app.passwords,
                     newuser = app.newuser,
                     site='bitsyblog')
    return cookie.middleware(auth, cookie_name='__ac', timeout=90) # minutes

# TODO: use wsgifilter.proxyapp.DebugHeaders to debug the headers apache
# doesn't like
