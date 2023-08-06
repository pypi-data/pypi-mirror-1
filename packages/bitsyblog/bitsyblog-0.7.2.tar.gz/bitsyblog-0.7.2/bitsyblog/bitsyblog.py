"""
a tiny tiny blog.  
this is the view class and is more bitsyblog than anything
else can claim to be
"""

### global variables

# format to uniquely label blog posts
timestamp = '%Y%m%d%H%M%S' # strftime representation

# who can view which blog posts
roles = { 'public': ( 'public', ),
          'friend': ( 'public', 'secret' ),
          'author': ( 'public', 'secret', 'private' ), }

### imports

import dateutil.parser  # XXX separate, for now
import parser # bitsyblog dateutil parser

import cgi
import datetime
import docutils
import docutils.core
import inspect
import markup
import os
import re
import utils

from blog import FileBlog
from user import FilespaceUsers
from lxml import etree
from markup.form import Form
from cStringIO import StringIO
from webob import Request, Response, exc

### exceptions

class DateStampException(Exception):
    """exception when parsing a datestamp"""
    # probably don't need this anymore

class BlogPathException(Exception):
    """exception when trying to retrieve the blog"""

### the main course

class BitsyBlog(object):
    """a very tiny blog"""

    ### class level variables
    defaults = { 'date_format': '%H:%M %F',
                 'file_dir': os.path.dirname(__file__),
                 'subject': '[ %(date)s ]:',
                 'n_links': 5, # number of links for navigation
                 'site_name': 'bitsyblog'
                 }

    def __init__(self, **kw):
        for key in self.defaults:
            setattr(self, key, kw.get(key, self.defaults[key]))
        self.n_links = int(self.n_links) # could be a string from the .ini
        self.response_functions = { 'GET': self.get,
                                    'POST': self.post,
                                    'PUT': self.put
                                    }
        
        # abstract attributes
        self.users = FilespaceUsers(self.file_dir)
        self.blog = FileBlog(self.file_dir)
        self.cooker = self.restructuredText

        # for BitsyAuth (for now)
        self.passwords = self.users.passwords
        self.newuser = self.users.new

    ### methods dealing with HTTP

    def __call__(self, environ, start_response):
        self.request = Request(environ)
        res = self.make_response(self.request.method)
        return res(environ, start_response)

    def make_response(self, method):
        return self.response_functions.get(method, self.error)()

    def get_response(self, text, content_type='text/html'):
        res = Response(content_type=content_type, body=text)
        res.content_length = len(res.body)
        return res

    def get(self):
        """
        display the blog or respond to a get request
        """

        # determine number of navigation links to display
        n_links = self.request.GET.get('n')
        if n_links == 'all':
            n_links = -1
        try:
            n_links = int(n_links)
        except (TypeError, ValueError):
            n_links = self.n_links

        path = self.request.path_info.strip('/')
        if not path: # the front page
            return self.get_response(self.index(n_links))

        ### static files

        # site.css 
        if path == 'css/site.css':
            css_file = os.path.join(self.file_dir, 'site.css')
            return self.get_response(file(css_file).read(), content_type='text/css')

        # logo
        if path == 'bitsyblog.png':
            logo = os.path.join(self.file_dir, 'bitsyblog.png')
            return self.get_response(file(logo, 'rb').read(), content_type='image/png')

        ### user space

        user, path = self.user()
        if user not in self.users:
            return exc.HTTPNotFound("No blog found for %s" % user)            
        self.request.user = self.users[user]

        check = self.check_user(user)

        # special paths
        if path == [ 'post' ]:
            if check is not None:
                return check
            return self.get_response(self.form_post(user))

        if path == [ 'preferences' ]:

            if check is not None:
                return check
            return self.get_response(self.preferences(user))

        if len(path) == 2:
            if path[0] == 'css':
                for i in self.request.user.settings['CSS']:
                    # find the right CSS file
                    if i['filename'] == path[1]:
                        return self.get_response(i['css'], content_type='text/css')
                else:
                    return exc.HTTPNotFound('CSS "%s" not found' % path[1])

        role = self.role(user)

        # get the blog
        try:
            blog = self.get_blog(user, path, role)
        except BlogPathException, e:
            return exc.HTTPNotFound(str(e))
        except exc.HTTPException, e:
            return e.wsgi_response

        # don't display navigation for short blogs
        if len(blog) < 2:
            n_links = 0

        # reverse the blog if necessary
        if self.request.GET.get('sort') == 'forward':
            blog = list(reversed(blog))
            
        # write the blog
        content = self.write_blog(user, blog, self.request.path_info, n_links)

        # return the content
        return self.get_response(content)

    def post(self):
        """
        write a blog entry and other POST requests
        """
        # TODO: posting to '/' ?
        
        # find user + path
        user, path = self.user()

        if user not in self.users:
            return exc.HTTPNotFound("No blog found for %s" % user)
        self.request.user = self.users[user]

        check = self.check_user(user)
        if check is not None:
            return check

        if len(path):
            if path == [ 'preferences' ]:
            
                # make the data look like we want
                settings = {}
                settings['Date format'] = self.request.POST.get('Date format')
                settings['Subject'] = '%(date)s'.join((self.request.POST['Subject-0'], self.request.POST['Subject-2']))
                settings['Stylesheet'] = self.request.POST['Stylesheet']
                settings['CSS file'] = self.request.POST.get('CSS file')
                settings['Friends'] = ', '.join(self.request.POST.getall('Friends'))
                
                errors = self.users.write_settings(user, **settings)
                if errors: # re-display form with errors                    
                    return self.get_response(self.preferences(user, errors))
                
                return self.get_response(self.preferences(user, message='Changes saved'))
            elif len(path) == 1 and self.isentry(path[0]):
                entry = self.blog.entry(path[0])
                if entry is None:
                    return exc.HTTPNotFound("Blog entry %s not found %s" % path[0])
                
            else:
                return exc.HTTPMethodNotAllowed("Not sure what you're trying to do")
        
        # get the body of the post
        body = self.request.body
        body = self.request.POST.get('form-post', body)
        body = body.strip()
        if not body:
            pass # do something

        # determine if the post is secret or private
        privacy = self.request.GET.get('privacy') or self.request.POST.get('privacy') or 'public'

        # write the file
        now = self.datestamp(datetime.datetime.now())
        location = "/%s/%s" % ( user, now )
        self.blog.post(user, now, body, privacy)

        # point the user at the post
        return exc.HTTPSeeOther("Post blogged by bitsy", location=location)

    def put(self):
        """
        PUT several blog entries from a file
        """

        # find user + path
        user, path = self.user()

        if user not in self.users.users():
            return exc.HTTPNotFound("No blog found for %s" % user)

        if len(path):
            return exc.HTTPMethodNotAllowed("Not sure what you're trying to do")
        
        # find the dates + entries in the file
        regex = '\[.*\]:'
        entries = re.split(regex, self.request.body)[1:]
        dates = [ date.strip().strip(':').strip('[]').strip()
                  for date in re.findall(regex, self.request.body) ]
        dates = [ dateutil.parser.parse(date) for date in dates ]

        # write to the blog
        for i in range(len(entries)):
            datestamp = datetime.strftime(timestamp)
            self.blog.post(user, datestamp, 'public')
        
        return exc.HTTPOk("%s posts blogged by bitsy" % len(entries))


    def error(self):
        """deal with non-supported methods"""
        methods = ', '.join(self.response_functions.keys()[:1]) 
        methods += ' and %s' % self.response_functions.keys()[-1] 
        return exc.HTTPMethodNotAllowed("Only %s operations are allowed" % methods)

    ### auth functions

    def authenticated(self):
        """return authenticated user"""
        return self.request.environ.get('REMOTE_USER')

    def check_user(self, user):
        """
        determine authenticated user
        returns None on success
        """
        authenticated = self.authenticated()
        if authenticated is None:
            return exc.HTTPUnauthorized('Unauthorized')
        elif user != authenticated:
            return exc.HTTPForbidden("Forbidden")        

    def role(self, user):
        """
        determine what role the authenticated member has
        with respect to the user
        """
        auth = self.authenticated()
        if not auth:
            return 'public'
        if auth == user:
            return 'author'
        else:
            if auth in self.request.user.settings['Friends']:
                return 'friend'
            else:
                return 'public'

    ### user methods

    def user(self): # TODO -> def userpath(self)
        """user who's blog one is viewing"""        
        path = self.request.path_info.strip('/').split('/')
        name = path[0]
        path = path[1:]
        if not name:
            name = None
        return name, path

    ### date methods

    def datestamp(self, date):
        # TODO -> utils.py
        return date.strftime(timestamp)

    def isentry(self, string):
        return (len(string) == len(''.join(utils.timeformat))) and string.isdigit()

    ### blog retrival methods

    def get_blog(self, user, path, role='public'):
        """retrieve the blog entry based on the path"""

        # get permissions
        allowed = roles[role]

        # entire blog
        if not path:
            return self.blog(user, allowed)

        # individual blog entry
        if (len(path) == 1) and self.isentry(path[0]):
            blog = self.blog.entry(user, path[0], allowed)
            if not blog:
                raise BlogPathException("No blog entry for %s" % path[0])
            return [ blog ]
            
        # parse the path into a date path
        n_date_vals = 3 # year, month, date
        if len(path) > n_date_vals:
            raise BlogPathException("blog entry not found")

        # ensure the path conforms to expected values (ints):
        try:
            [ int(i) for i in path]
        except ValueError:
            raise BlogPathException("blog entry not found")

        # get the blog
        return self.blog.entries(user, allowed, *path)

    ### methods that write HTML

    def render(self, body, title=None):
        """layout the page in a unified way"""
        stylesheets = ()
        user = getattr(self.request, 'user', None)
        _title = [ self.site_name ]
        if user:
            stylesheets = self.request.user['CSS']
            stylesheets = [ (("/%s/css/%s" % (user.name, css['filename'])),
                             css['name']) for css in stylesheets ]
            _title.insert(0, self.request.user.name)
        else:
            stylesheets = (("/css/site.css", "Default"),)
            
        if title:
            _title.insert(0, title)
            
        title = ' - '.join(_title)
        return markup.wrap(self.site_nav()+body, title, stylesheets)

    def site_nav(self):
        """returns HTML for site navigation"""
        links = [('/',), ]
        user = self.authenticated()
        if user:
            links.extend([('/%s' % user, user),
                          ('/%s/post' % user, 'post'),
                          ('/%s/preferences' % user, 'preferences'),
                          ('/logout', 'logout')])
        else:
            links.extend([('/login', 'login'), ('/join', 'join')])
        links = [ markup.link(*i) for i in links ]
        return markup.listify(links, ordered=False, **{ 'class': 'site-nav'})

    def index(self, n_links):
        retval = StringIO()
        print >> retval, '<h1><img src="bitsyblog.png" alt="bitsyblog"/></h1>'

        # get the blogs
        blogs = {}
        for user in self.users:
            blog = self.blog(user, ('public',), n_links)
            if blog:
                blogs[user] = blog
        users = blogs.keys()

        # display latest active user first
        users.sort(key=lambda user: blogs[user][0].date, reverse=True)

        # display users' blogs
        for user in users:
            print >> retval, '<div id="%s" class="user">' % user
            print >> retval, '<a href="%s">%s</a>' % (user, user)
            blog = blogs[user]
            print >> retval, self.navigation(user, blog, '/%s' % user, n_links)
            print >> retval, '</div>'

        return self.render(retval.getvalue())

    def navigation(self, user, blog, path, n_links, n_char=80):
        prefs = self.users[user].settings
        
        if n_links == 0 or not len(blog):
            return ''
        retval = StringIO()
        print >> retval, '<div class="navigation">'
        more = ''
        if (n_links != -1) and (len(blog) > n_links):
            more = '<a href="%s?n=all">more</a>' % path
            blog = blog[:n_links]

        entries = []
        for entry in blog:
            id = self.datestamp(entry.date)
            format = prefs.get('Date format', self.date_format)
            datestamp = entry.date.strftime(format)
            synopsis = entry.snippet()
            if synopsis:
                synopsis = ': %s' % cgi.escape(synopsis)
            entries.append(markup.link("%s#%s" % (path, id), datestamp) + synopsis)

        print >> retval, markup.listify(entries)
        print >> retval, more
        print >> retval, '</div>'
        return retval.getvalue()

    def blog_entry(self, user, entry):
        """given the content string, return a marked-up blog entry"""

        # user preferences
        prefs = self.request.user.settings
        format = prefs.get('Date format', self.date_format)
        subject = prefs.get('Subject', self.subject)

        role = self.role(user)
        
        subject = subject % { 'date' : entry.date.strftime(format) }
        subject = cgi.escape(subject)
        html = StringIO()
        id = self.datestamp(entry.date)
        print >> html, '<div id="%s" class="blog-entry">' % id
        print >> html, '<a name="%s" />' % id
        print >> html, '<div class="subject">'
        print >> html, '<a href="/%s/%s">%s</a>' % (user, id, subject)
        if (entry.privacy == 'secret') and (role == 'friend'):
            print >> html, '<em>secret</em>'
        print >> html, '</div>'
        print >> html, self.cooker(entry.body)

        if role == 'author':
            print >> html, '<div><form>'
            print >> html, self.privacy_settings(entry.privacy)
            print >> html, '</form></div>'
        
        print >> html, '</div>'
        return html.getvalue()
        
    def write_blog(self, user, blog, path, n_links):
        """return the user's blog in HTML"""
        retval = StringIO()
        print >> retval,  self.navigation(user, blog, path, n_links, 0)
        for entry in blog:
            print >> retval, self.blog_entry(user, entry)
        return self.render(retval.getvalue())
                           
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

    ### forms and accompanying display

    def form_post(self, user):
        retval = StringIO()
        print >> retval, '<form action="/%s" method="post">' % user
        print >> retval, '<textarea cols="80" rows="25" name="form-post"></textarea><br/>'
        print >> retval, self.privacy_settings()
        print >> retval, '<input type="submit" name="submit" value="Post" />'
        print >> retval, '</form>'
        return self.render(retval.getvalue())

    def preferences_form(self, user):
        prefs = self.request.user.settings
        form = Form()

        # date format
        format = prefs.get('Date format', self.date_format)
        value = datetime.datetime.now().strftime(format)
        form.add_element('textfield', 'Date format', value=value,
                         help='how to display dates in your blog post subject')

        # subject
        subject = prefs.get('Subject', self.subject)
        subject = subject.split('%(date)s', 1)
        func = lambda name: value
        form.add_elements('Subject',
                          ['textfield', func, 'textfield' ],
                          [ (), (), ()], # this is horrible!
                          [ dict(value=subject[0]),
                            {},
                            dict(value=subject[1]) ],
                          help='how to display the subject line of your blog post'
                          )
                          
        # CSS files
        css_files = [ i['name'] for i in prefs['CSS'] ]
        form.add_element('menu', 'Stylesheet', css_files,
                         help='which CSS file should be the default')

        # or upload a CSS file
        form.add_element('file_upload', 'CSS file',
                         help='upload a CSS file to theme your webpage')

        # Friends -- can see secret posts
        users = [ i for i in list(self.users.users()) 
                  if i != user ]
        if users:
            users.sort()
            form.add_element('checkboxes', 'Friends',
                             users, prefs.get('Friends', set()),
                             help='friends can see your secret posts')
        
        return form

    def preferences(self, user, errors=None, message=None):
        """user preferences form"""
        body = self.preferences_form(user)(errors)
        if message:
            body = '%s\n%s' % ( markup.p(markup.strong(message)), body )
        return self.render(body, title='preferences')

    def privacy_settings(self, default='public'):
        """HTML snippet for privacy settings"""
        settings = (('public', 'viewable to everyone'),
                    ('secret', 'viewable only to your friends'),
                    ('private', 'viewable only to you'))
        form = Form()
        return form.radiobuttons('privacy', settings, checked=default, joiner=' ')
