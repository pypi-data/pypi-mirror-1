from bitsyauth import BitsyAuth
from bitsyblog import BitsyBlog
from paste.httpexceptions import HTTPExceptionHandler

def factory(global_conf, **app_conf):
    """make bitsyauth app and wrap it in middleware"""
    
    config = [ 'file_dir', 'date_format', 'subject', 'n_links' ]
    key_str = 'bitsyblog.%s'
    args = dict([ (key, app_conf[ key_str % key]) for key in config
                  if app_conf.has_key(key_str % key) ])

    app = BitsyBlog(**args)
    secret = app_conf.get('secret', 'secret')
    return BitsyAuth(HTTPExceptionHandler(app), global_conf, app.passwords, app.newuser, 'bitsyblog', secret)

# TODO: use wsgifilter.proxyapp.DebugHeaders to debug the headers apache
# doesn't like
