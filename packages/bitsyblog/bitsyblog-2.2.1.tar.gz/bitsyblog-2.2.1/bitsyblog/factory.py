from bitsyauth import BitsyAuth
from bitsyblog import BitsyBlog, BitsierBlog
from getpass import getpass 
from paste.httpexceptions import HTTPExceptionHandler

def factory(global_conf, **app_conf):
    """make bitsyauth app and wrap it in middleware"""
    
    config = [ 'file_dir', 'date_format', 'subject', 'n_links', 'help_file' ]
    key_str = 'bitsyblog.%s'
    args = dict([ (key, app_conf[ key_str % key]) for key in config
                  if app_conf.has_key(key_str % key) ])
    app = BitsyBlog(**args)
    secret = app_conf.get('secret', 'secret')
    return BitsyAuth(HTTPExceptionHandler(app), global_conf, app.passwords, app.newuser, 'bitsyblog', secret)


def bitsierfactory(global_conf, **app_conf):
    """make single-user bitsyblog"""
    config = [ 'file_dir', 'date_format', 'subject', 'n_links', 'help_file' ]
    key_str = 'bitsyblog.%s'
    args = dict([ (key, app_conf[ key_str % key]) for key in config
                  if app_conf.has_key(key_str % key) ])
    user = app_conf['bitsyblog.user']
    app = BitsierBlog(**args)
    app.user = user
    secret = app_conf.get('secret', 'secret')
    auth = BitsyAuth(HTTPExceptionHandler(app), global_conf, app.passwords, newuser=None, site='bitsyblog', secret=secret)
    if not user in app.users:
        pw = getpass('Enter password for %s: ' % user)
        app.newuser(user, auth.hash(app.user, pw))
    return auth
