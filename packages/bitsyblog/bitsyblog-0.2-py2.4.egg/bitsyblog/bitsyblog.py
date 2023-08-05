### imports

import datetime
import dateutil.parser
import docutils
import docutils.core
import inspect
import os
import re
import shutil

from lxml import etree
from glob import glob
from StringIO import StringIO
from webob import Request, Response, exc

### exceptions

class DateStampException(Exception):
    """exception when parsing a datestamp"""

### the main course

class BitsyBlog(object):
    """
    a very tiny blog
    """

    def authenticate(self):
        pass

    ### class level variables
    defaults = { 'date_format': '%H:%M %F',
                 'file_dir': os.path.dirname(__file__),                 
                 }
    n_links = 10 # number of links for navigation
    subject = '[ %(date)s ]:'
    timestamp = '%Y%m%d%H%M%S'
    file_format = ( 'YYYY', 'MM', 'DD', 'HH', 'MM', 'SS' )

    def __init__(self, **kw):
        for key in self.defaults:
            setattr(self, key, kw.get(key, self.defaults[key]))
        self.cooker = self.restructuredText

    ### methods dealing with HTTP

    def __call__(self, environ, start_response):
        res = self.make_response(environ)
        return res(environ, start_response)

    def make_response(self, environ):
        method = environ['REQUEST_METHOD']
        response = { 'GET': self.get,
                     'POST': self.post,
                     'PUT': self.put
                     }

        return response.get(method, self.error)(environ)

    def get_response(self, text, type='text/html'):
        res = Response(content_type=type, body=text)
        res.content_length= len(res.body)
        return res

    def get(self, environ):
        """
        display the blog
        """
        req = Request(environ)

        # determine number of navigation links to display
        n_links = req.GET.get('n')
        if n_links == 'all':
            n_links = -1
        try:
            n_links = int(n_links)
        except TypeError:
            n_links = self.n_links

        path = environ['PATH_INFO'].strip('/')
        if not path: # the front page
            return self.get_response(self.index(n_links))

        # just a static site.css for now
        if path == 'css/site.css':
            css_file = os.path.join(self.file_dir, 'site.css')
            return self.get_response(file(css_file).read())

        # logo
        if path == 'bitsyblog.png':
            logo = os.path.join(self.file_dir, 'bitsyblog.png')
            return self.get_response(file(logo, 'rb').read(), type='image/png')

        path = path.split('/')
        user = path.pop(0)

        # "special" paths
        if path == [ 'post' ]:
            return self.get_response(self.form_post(user))

        if path == [ 'preferences' ]:
            return self.get_response(self.preferences(user))

        # get the blog
        try:
            blog = self.get_blog(user, path)
        except exc.HTTPException, e:
            return e.wsgi_response

        # don't display navigation for short blogs
        if len(blog) < 2:
            n_links = 0

        # reverse the blog if necessary
        if req.GET.get('sort') == 'forward':
            blog = list(reversed(blog))
            
        # write the blog
        content = self.write_blog(user, blog, environ['PATH_INFO'], n_links)

        # return the content
        return self.get_response(content)

    def post(self, environ):
        """
        write a blog entry
        """
        req = Request(environ)

        # find user + path
        user, path = self.user(environ)
        if len(path):
            return exc.HTTPMethodNotAllowed("Not sure what you're trying to do")
        directory = self.home(user)
        if not os.path.exists(directory):
            self.newuser(user)

        self.authenticate()
            
        filename = self.filename(user, datetime.datetime.now())

        body = req.body
        body = req.POST.get('form-post', body)
        body = body.strip()

        blog = file(filename, 'w')
        print >> blog, body

        return exc.HTTPOk("Post blogged by bitsy")

    def form_post(self, user):
        retval = StringIO()
        print >> retval, '<html>\n<head>'
        print >> retval, '<title>%s - bitsyblog</title>' % user
        print >> retval, '<head>\n<body>'
        print >> retval, '<form action="/%s" method="post">' % user
        print >> retval, '<textarea cols="80" rows="25" name="form-post"></textarea>'
        print >> retval, '<input type="submit" name="submit" value="Post" />'
        print >> retval, '</form>\n</body>\n</html>'
        return retval.getvalue()

    def put(self, environ):
        """
        PUT several blog entries from a file
        """

        # find user + path
        user, path = self.user()
        if len(path):
            return exc.HTTPMethodNotAllowed("Not sure what you're trying to do")
        
        directory = self.home(user)
        if not os.path.isdir(directory):
            self.newuser(user)

        # find the dates + entries in the file
        req = Request(environ)
        regex = '\[.*\]:'
        entries = re.split(regex, req.body)[1:]
        dates = [ date.strip().strip(':').strip('[]').strip()
                  for date in re.findall(regex, req.body) ]
        dates = [ dateutil.parser.parse(date) for date in dates ]
        

        for i in range(len(entries)):
            filename = self.filename(user, dates[i])
            entry = file(filename, 'w')
            print >> entry, entries[i].strip()
        
        return exc.HTTPOk("%s posts blogged by bitsy" % len(entries))


    def error(self, environ):
        return exc.HTTPMethodNotAllowed("Only GET and POST operations are allowed")

    ### user methods

    def user(self, environ):
        path = environ['PATH_INFO'].strip('/').split('/')
        name = path[0]
        path = path[1:]
        if not name:
            name = None
        return name, path

    def users(self):
        retval = []
        ignores = [ '.svn' ]
        for user in os.listdir(self.file_dir):
            # ensure integrity of user folder
            if user in ignores:
                continue
            if os.path.isdir(os.path.join(self.file_dir, user)):
                retval.append(user)
        return retval

    def newuser(self, user):
        # TODO: security
        forbidden = ' |<>./?' 
        if [ i for i in forbidden if i in user ]:
            raise HTTPForbidden("username '%s' contains forbidden characters [%s]" % (user, forbidden))
        home = self.home(user)
        os.mkdir(home)
        os.mkdir(os.path.join(home, 'entries'))
        css_dir = os.path.join(home, 'css') 
        os.mkdir(css_dir)
        shutil.copyfile(os.path.join(self.file_dir, 'site.css'),
                        os.path.join(css_dir, 'default.css'))

    def home(self, user):
        return os.path.join(self.file_dir, user)

    def filename(self, user, datetime):        
        return os.path.join(self.home(user),
                            'entries',
                            datetime.strftime(self.timestamp))

    def get_preferences(self, user):
        """returns a dictionary of user preferences from a file"""
        filename = 'preferences.txt'
        filename = os.path.join(self.home(user), filename)
        if not os.path.exists(filename):
            # XXX maybe should make the file, too?
            return {}
        prefs = file(filename).read().split('\n')
        prefs = [ i for i in prefs if i.strip() ]
        prefs = [ [ j.strip() for j in i.split(':', 1) ] for i in prefs
                  if ':' in i] # probably not necessary
        return dict(prefs)

    def css_files(self, user):
        default = self.get_preferences(user).get('CSS')
        

    ### date methods

    def date_args(self):
        return inspect.getargspec(self.get_blog_entries)[0][2:]

    def date(self, datestamp):
        datestamp = os.path.split(datestamp)[-1]
        retval = []
        for i in self.file_format:
            retval.append(int(datestamp[:len(i)]))
            datestamp = datestamp[len(i):]
        retval = datetime.datetime(*retval)
        return retval

    def datestamp(self, date):
        return date.strftime(self.timestamp)

    ### blog retrival methods

    def get_blog(self, user, path):

        # individual blog entry
        if (len(path) == 1) and (len(path[0]) == len(''.join(self.file_format))):
            date = self.date(path[0])
            entry = file(self.filename(user, date)).read()
            blog = [ (date, entry) ]
            return blog
            
        # parse the path into a date path
        n_date_vals = len(self.date_args())
        if len(path) > n_date_vals:
            # XXX probably raise an exception and/or redirect here
            path = path[:n_date_vals]

        # get the blog
        blog = self.get_blog_entries(user, *path)
        return blog

    def get_blog_entries(self, user, year=None, month=None, day=None, hour=None):

        directory = os.path.join(self.home(user), 'entries')
        if not os.path.isdir(directory):
            raise exc.HTTPNotFound("No blog found for %s" % user).exception

        flag = False
        glob_expr = StringIO()
        for index in range(len(self.file_format)):
            field_length = len(self.file_format[index])
            if index >= len(self.date_args()):
                flag = True
            else:
                value = locals()[self.date_args()[index]]
                if value is None:
                    flag = True
            if flag:
                print >> glob_expr, '[0-9]' * field_length
            else:
                # TODO should handle cast where value is not an integer
                value  = int(value)
                print >> glob_expr, '%0*d' % ( field_length, value )

        glob_expr = ''.join(glob_expr.getvalue().split())
        files = glob(os.path.join(directory, glob_expr))
                                   
        retval = [ (self.date(filename), file(filename).read())
                   for filename in files ]
        retval.sort(cmp=(lambda x, y: cmp(x[0], y[0])), reverse=True)
        return retval

    ### methods that write HTML

    def index(self, n_links):
        retval = StringIO()

        print >> retval, '<html>\n<head>'
        print >> retval, '<title>bitsyblog</title>'
        print >> retval, '<link rel="stylesheet" type="text/css" href="css/site.css" title="Default" />'
        print >> retval, '</head>'
        print >> retval, '<body>'
        print >> retval, '<h1><img src="bitsyblog.png" alt="bitsyblog"/></h1>'
        
        # get the users
        users = self.users()

        # do something with them
        for user in users:
            print >> retval, '<div id="%s" class="user">' % user
            print >> retval, '<a href="%s">%s</a>' % (user, user)
            blog = self.get_blog_entries(user)
            blog = blog[:n_links]
            print >> retval, self.navigation(blog, '/%s' % user, n_links)
            print >> retval, '</div>'
        print >> retval, '</body>\n</html>'
        return retval.getvalue()

    def navigation(self, blog, path, n_links, n_char=80):
        if n_links == 0 or not len(blog):
            return ''
        retval = StringIO()
        print >> retval, '<div class="navigation">\n<ul>'
        more = ''
        if (n_links != -1) and (len(blog) > n_links):
            more = '<a href="%s?n=all">more</a>' % path
            blog = blog[:n_links]

        for date, text in blog:
            id = self.datestamp(date)
            date = date.strftime(self.date_format)
            synopsis=''
            if n_char:
                if len(text) > n_char:
                    text = ' '.join(text[:n_char].split()[:-1])
                    if text:
                        text = '%s ...' % text
                if text:
                    synopsis = ': %s' % text
            print >> retval, '<li><a href="%s#%s">%s</a>%s</li>' % (path, id, date, synopsis)
        print >> retval, '</ul>'
        print >> retval, more
        print >> retval, '</div>'
        return retval.getvalue()

    def blog_entry(self, date, text):
        """given the content string, return a marked-up blog entry"""        
        subject = self.subject % { 'date' : date.strftime(self.date_format) }
        html = StringIO()
        id = self.datestamp(date)
        print >> html, '<div id="%s" class="blog-entry">' % id
        print >> html, '<a name="%s" />' % id
        print >> html, '<div class="date">%s</div>' % subject
        print >> html, self.cooker(text)
        print >> html, '</div>'
        return html.getvalue()
        
    def write_blog(self, user, blog, path, n_links):
        retval = StringIO()
        print >> retval, '<html>\n<head>'
        print >> retval, '<title>%s - bitsyblog</title>' % user
        print >> retval, '</head>\n<body>'
        print >> retval,  self.navigation(blog, path, n_links, 0)
        for date, text in blog:
            print >> retval, self.blog_entry(date, text)
        print >> retval, '</body>\n</html>'
        return retval.getvalue()

    def restructuredText(self, string):
        origstring = string
        settings = { 'report_level': 5 }
        parts = docutils.core.publish_parts(string.strip(),
                                            writer_name='html',
                                            settings_overrides=settings)
        retval = '<div class="blog-body">%s</div>' % parts['body']
        try:
            foo = etree.fromstring(retval)
        except etree.XMLSyntaxError:
            pass
        # should cleanup the <div class="system-message">
        for i in foo.getiterator():
            if dict(i.items()).get('class') ==  'system-message':
                i.clear()
                
        return etree.tostring(foo)

    def preferences(self, user):
        """user preferences form"""
        prefs = self.get_preferences(user)
        
        retval = StringIO()
        print >> retval, '<html>\n<head>'
        print >> retval, '<title>%s - preferences</title>' % user
        print >> retval, '<body>'
        print >> retval, '<form method="post">'

        # CSS files
        print >> retval, '<select name="css">'
        css_files = [ i for i in os.listdir(os.path.join(self.home(user),
                                                         'css'))
                      if i.endswith('.css') ]
        for i in css_files:
            print >> retval, '<option>%s</option' % i.rsplit('.css',1)[0]
        print >> retval, '</select>'

        print >> retval, '<input type="submit" value="Submit" />'
        print >> retval, '</form>'
        print >> retval, '</body>\n</html>'
        return retval.getvalue()
        
        

### stuff for paste

from paste.httpexceptions import HTTPExceptionHandler

def factory(global_conf, **app_conf):

    config = [ 'file_dir', 'date_format' ]
    key_str = 'bitsyblog.%s'
    args = dict([ (key, app_conf[ key_str % key]) for key in config
                  if app_conf.has_key(key_str % key) ])
    app =  BitsyBlog(**args)
    return HTTPExceptionHandler(app)
