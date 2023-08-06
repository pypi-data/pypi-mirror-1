"""
a tiny tiny blog.  
this is the view class and is more bitsyblog than anything
else can claim to be
"""

### global variables

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
import PyRSS2Gen
import re
import utils

from blog import FileBlog
from user import FilespaceUsers
from lxml import etree
from markup.form import Form
from cStringIO import StringIO
from webob import Request, Response, exc

### exceptions

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
                 'site_name': 'bitsyblog',
                 'help_file': None
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

        if hasattr(self, 'help_file') and os.path.exists(self.help_file):
            help = file(self.help_file).read()
            self.help = docutils.core.publish_string(help,
                                                     writer_name='html',
                                                     settings_overrides={'report_level': 5})


        # for BitsyAuth
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

    def get_index(self):
        """returns material pertaining to the root of the site"""
        path = self.request.path_info.strip('/')

        n_links = self.number_of_links()

        ### the front page
        if not path: 
            return self.get_response(self.index(n_links))

        ### feeds

        n_posts = self.number_of_posts()

        # site rss
        if path == 'rss':
            if n_posts is None:
                n_posts = 10
            return self.get_response(self.site_rss(n_posts), content_type='text/xml')

        # site atom
        if path == 'atom':
            if n_posts is None:
                n_posts = 10
            return self.get_response(self.atom(self.blog.latest(self.users.users(), n_posts)), content_type='text/xml')

        ### help
        if path == 'help' and hasattr(self, 'help'):
            return self.get_response(self.help)

        ### static files

        # site.css 
        if path == 'css/site.css':
            css_file = os.path.join(self.file_dir, 'site.css')
            return self.get_response(file(css_file).read(), content_type='text/css')

        # logo
        if path == 'bitsyblog.png':
            logo = os.path.join(self.file_dir, 'bitsyblog.png')
            return self.get_response(file(logo, 'rb').read(), content_type='image/png')        

    def get_user_space(self, user, path):
        self.request.user = self.users[user] # user whose blog is viewed
        check = self.check_user(user) # is this the authenticated user?

        feed = None # not an rss/atom feed by default (flag)
        n_posts = self.number_of_posts(user)

        # special paths
        if path == [ 'post' ]:
            if check is not None:
                return check
            return self.get_response(self.form_post(user))

        if path == [ 'preferences' ]:
            if check is not None:
                return check
            return self.get_response(self.preferences(user))
        
        if path == [ 'rss' ]:
            feed = 'rss'
            path = []
            if n_posts is None:
                n_posts = 10 # TODO: allow to be configurable

        if path == [ 'atom' ]:
            feed = 'atom'
            path = []
            if n_posts is None:
                n_posts = 10 # TODO: allow to be configurable

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
            blog = self.get_blog(user, path, role, n_items=n_posts)
        except BlogPathException, e:
            return exc.HTTPNotFound(str(e))
        except exc.HTTPException, e:
            return e.wsgi_response

        if feed == 'rss':
            content = self.rss(user, blog) # XXX different signatures
            return self.get_response(content, content_type='text/xml')

        if feed == 'atom':
            content = self.atom(blog, user) # XXX different signatures
            return self.get_response(content, content_type='text/xml')
        
        # reverse the blog if necessary
        if self.request.GET.get('sort') == 'forward':
            blog = list(reversed(blog))

        n_links = self.number_of_links(user)
        # don't display navigation for short blogs
        if len(blog) < 2:
            n_links = 0
            
        # write the blog
        content = self.write_blog(user, blog, self.request.path_info, n_links)

        # return the content
        return self.get_response(content)        

    def get(self):
        """
        display the blog or respond to a get request
        """
        # front matter of the site
        index = self.get_index()
        if index is not None:
            return index

        ### user space
        user, path = self.userpath()
        if user not in self.users:
            return exc.HTTPNotFound("No blog found for %s" % user)
        return self.get_user_space(user, path)

    def post(self):
        """
        write a blog entry and other POST requests
        """
        # TODO: posting to '/' ?
        
        # find user + path
        user, path = self.userpath()

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
                entry = self.blog.entry(user, path[0], roles['author'])
                if entry is None:
                    return exc.HTTPNotFound("Blog entry %s not found %s" % path[0])
                privacy = self.request.POST.get('privacy')
                datestamp = entry.datestamp()
                if privacy:
                    self.blog.delete(user, datestamp)
                    self.blog.post(user, datestamp, entry.body, privacy)
                return exc.HTTPSeeOther("Settings updated", location='/%s/%s' % (user, datestamp))
            else:
                return exc.HTTPMethodNotAllowed("Not sure what you're trying to do")
        
        # get the body of the post
        body = self.request.body
        body = self.request.POST.get('form-post', body)
        body = body.strip()
        if not body:
            return exc.HTTPSeeOther("Your post has no content!  No blog for you", 
                                    location='/%s' % self.user_url(user, 'post'))

        # determine if the post is secret or private
        privacy = self.request.GET.get('privacy') or self.request.POST.get('privacy') or 'public'

        # write the file
        now = utils.datestamp(datetime.datetime.now())
        location = "/%s" % self.user_url(user, now)
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
            datestamp = utils.datestamp(dates[i])
            self.blog.post(user, datestamp, entries[i], 'public')
        
        return exc.HTTPOk("%s posts blogged by bitsy" % len(entries))


    def error(self):
        """deal with non-supported methods"""
        methods = ', '.join(self.response_functions.keys()[:1]) 
        methods += ' and %s' % self.response_functions.keys()[-1] 
        return exc.HTTPMethodNotAllowed("Only %s operations are allowed" % methods)

    ### auth functions

    def passwords(self):
        return self.users.passwords()

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

    def userpath(self):
        """user who's blog one is viewing"""        
        path = self.request.path_info.strip('/').split('/')
        name = path[0]
        path = path[1:]
        if not name:
            name = None
        return name, path

    ### date methods

    def isentry(self, string): # TODO -> blog.py
        return (len(string) == len(''.join(utils.timeformat))) and string.isdigit()

    def user_url(self, user, *args, **kw):
        permalink = kw.get('permalink')
        if permalink:
            _args = [ self.request.host_url, user ]
        else:
            _args = [ user ]
        _args.extend(args)
        return '/'.join([str(arg) for arg in _args])

    def permalink(self, blogentry):
        return self.user_url(blogentry.user, blogentry.datestamp(), permalink=True)

    def entry_subject(self, blogentry):
        if hasattr(self.request, 'user') and self.request.user.name == blogentry.user:
            prefs = self.request.user.settings
        else:
            prefs = self.users[blogentry.user].settings
        subject = prefs.get('Subject', self.subject)
        date_format = prefs.get('Date format', self.date_format)
        return subject % { 'date': blogentry.date.strftime(date_format) }

    def mangledurl(self, blogentry):
        return self.user_url(blogentry.user, 'x%x' % (int(blogentry.datestamp()) * self.users.secret(blogentry.user)), permalink=True)

    def unmangleurl(self, url, user):
        url = url.strip('x')
        try:
            value = int(url, 16)
        except ValueError:
            return None
        
        # XXX once one has a mangled url, one can obtain the secret
        value /= self.users.secret(user) 

        entry = str(value)
        if self.isentry(entry):
            return self.blog.entry(user, entry, ['public', 'secret', 'private'])
        
    ### blog retrival methods

    def number_of_posts(self, user=None):
        """return the number of blog posts to display"""
        # determine number of posts to display (None -> all)
        n_posts = self.request.GET.get('posts', None)
        if n_posts is not None:
            try:
                n_posts = int(n_posts)
                if n_links > 0 and n_links > n_posts:
                    n_links = n_posts # don't display more links than posts
            except (TypeError, ValueError):
                n_posts = None
        return n_posts

    def number_of_links(self, user=None):
        """return the number of links to display in the navigation"""
        # determine number of navigation links to display
        n_links = self.request.GET.get('n')
        if n_links == 'all':
            return -1
        try:
            n_links = int(n_links)
        except (TypeError, ValueError):
            n_links = self.n_links
        return n_links

    def get_blog(self, user, path, role='public', n_items=None):
        """retrieve the blog entry based on the path"""

        notfound = "blog entry not found"

        # get permissions
        allowed = roles[role]

        # entire blog
        if not path:
            return self.blog(user, allowed, n_items)

        # mangled urls 
        if len(path) == 1 and path[0].startswith('x'):
            entry = self.unmangleurl(path[0], user)
            if entry:
                return [ entry ]
            else:
                raise BlogPathException(notfound)
            
        # individual blog entry
        if (len(path) == 1) and self.isentry(path[0]):
            blog = self.blog.entry(user, path[0], allowed)
            if not blog:
                raise BlogPathException(notfound)
            return [ blog ]
            
        # parse the path into a date path
        n_date_vals = 3 # year, month, date
        if len(path) > n_date_vals:
            raise BlogPathException(notfound)

        # ensure the path conforms to expected values (ints):
        try:
            [ int(i) for i in path]
        except ValueError:
            raise BlogPathException(notfound)

        # get the blog
        return self.blog.entries(user, allowed, *path)

    ### methods that write HTML

    def render(self, body, title=None, feedtitle=None):
        """layout the page in a unified way"""
        stylesheets = ()
        user = getattr(self.request, 'user', None)
        _title = [ self.site_name ]
        if user:
            stylesheets = self.request.user['CSS']
            stylesheets = [ (("/%s" % self.user_url(user.name, 'css', css['filename'])),
                             css['name']) for css in stylesheets ]
            _title.insert(0, self.request.user.name)
        else:
            stylesheets = (("/css/site.css", "Default"),)
            
        if title:
            _title.insert(0, title)
            
        title = ' - '.join(_title)
        head_markup = ()
        if feedtitle:
            head_markup = ( '<link rel="alternate" type="application/atom+xml" title="%s" href="atom" />' % feedtitle, 
                            '<link rel="alternate" type="application/rss+xml" title="%s" href="rss" />' % feedtitle,)
        return markup.wrap(self.site_nav()+body, title, stylesheets, head_markup=head_markup)

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

        if hasattr(self, 'help'):
            links.append(('/help', 'help'))

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

        return self.render(retval.getvalue(), feedtitle=self.site_name)

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
            id = entry.datestamp()
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
        # XXX no need to pass user

        # user preferences
        prefs = self.request.user.settings
        format = prefs.get('Date format', self.date_format)
        subject = prefs.get('Subject', self.subject)

        role = self.role(user)
        
        subject = subject % { 'date' : entry.date.strftime(format) }
        subject = cgi.escape(subject)
        html = StringIO()
        id = entry.datestamp()
        print >> html, '<div id="%s" class="blog-entry">' % id
        print >> html, '<a name="%s" />' % id
        print >> html, '<div class="subject">'
        print >> html, '<a href="/%s">%s</a>' % (self.user_url(user, id), subject)
        if (entry.privacy == 'secret') and (role == 'friend'):
            print >> html, '<em>secret</em>'
        print >> html, '</div>'
        print >> html, self.cooker(entry.body)

        if role == 'author':
            print >> html, '<div><form action="/%s" method="post">' % self.user_url(entry.user, id)
            print >> html, self.privacy_settings(entry.privacy)
            print >> html, '<input type="submit" name="submit" value="Change Privacy" />'
            print >> html, '</form></div>'
            if entry.privacy != 'public':
                title = "You can give this URL so people may see this %s post without logging in" % entry.privacy
                print >> html, '<div>'
                print >> html, '<span title="%s">Mangled URL:</span>' % title
                print >> html, markup.link(self.mangledurl(entry))
                print >> html, '</div>'
        
        print >> html, '</div>'
        return html.getvalue()
        
    def write_blog(self, user, blog, path, n_links):
        """return the user's blog in HTML"""
        # XXX no need to pass path or user!
        retval = StringIO()
        print >> retval,  self.navigation(user, blog, path, n_links, 0)
        for entry in blog:
            print >> retval, self.blog_entry(user, entry)
        feedtitle=None
        if self.request.path_info.strip('/') == user:
            feedtitle = "%s's blog" % user
        title = None
        if len(blog) == 1:
            format = self.request.user.settings.get('Date format', self.date_format)
            title = blog[0].date.strftime(format)
        return self.render(retval.getvalue(), title=title, feedtitle=feedtitle)
                           
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

    ### feeds

    def site_rss(self, n_items=10):
        blog = self.blog.latest(list(self.users.users()), n_items)
        title = self.site_name + ' - rss'
        link = self.request.host_url # XXX should be smarter
        description = "latest scribblings on %s" % self.site_name
        lastBuildDate = datetime.datetime.now()
        items = [ self.rss_item(entry.user, entry) for entry in blog ]
        rss = PyRSS2Gen.RSS2(title=title, 
                             link=link,
                             description=description,
                             lastBuildDate=lastBuildDate,
                             items=items)
        return rss.to_xml()

    def rss(self, user, blog):
        """
        rss feed for a user's blog
        done with PyRSS2Gen:
        http://www.dalkescientific.com/Python/PyRSS2Gen.html
        """        
        title = "%s's blog" % user
        link = os.path.split(self.request.url)[0]
        description = "latest blog entries for %s on %s" % (user, self.site_name)
        lastBuildDate = datetime.datetime.now() # not sure what this means
        
        items = [ self.rss_item(user, entry) for entry in blog ]
        rss = PyRSS2Gen.RSS2(title=title, 
                             link=link,
                             description=description,
                             lastBuildDate=lastBuildDate,
                             items=items)
        return rss.to_xml()

    def rss_item(self, user, entry):
        if hasattr(self.request, 'user') and self.request.user.name == user:
            prefs = self.request.user.settings
        else:
            prefs = self.users[user].settings
        subject = prefs.get('Subject', self.subject)
        date_format = prefs.get('Date format', self.date_format)
        return PyRSS2Gen.RSSItem(title=subject % { 'date': entry.date.strftime(date_format) },
                                 link=self.permalink(entry),
                                 description=unicode(entry.snippet(), errors='replace'),
                                 author=user,
                                 guid=PyRSS2Gen.Guid(self.permalink(entry)),
                                 pubDate=entry.date)


    def atom(self, blog, author=None):
        retval = StringIO()
        print >> retval, """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/">
"""
        if author:
            title = "%s's blog" % author
            link = self.request.host_url + '/' + author
        else:
            title = self.site_name + ' - atom'
            link = self.request.host_url
            
        date = blog[0].date.isoformat()

        print >> retval, '<title>%s</title>' % title
        print >> retval, '<link href="%s" />' % link
        print >> retval, '<updated>%s</updated>' % date
        if author:
            print >> retval, """
 <author>
    <name>%s</name>
 </author>""" % author
 
        for entry in blog:
            print >> retval, '<entry>'
            print >> retval, '<title>%s</title>' % self.entry_subject(entry)
            print >> retval, '<link>%s</link>' % self.permalink(entry)
            print >> retval, '<updated>%s</updated>' % entry.date.isoformat()
            print >> retval, '<summary>%s</summary>' % cgi.escape(entry.snippet())

            print >> retval, '</entry>'
 
        print >> retval, '</feed>'
        return retval.getvalue()

    ### forms and accompanying display

    def form_post(self, user):
        retval = StringIO()
        print >> retval, '<form action="/%s" method="post">' % self.user_url(user)
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
            users.sort(key=str.lower)
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

class BitsierBlog(BitsyBlog):
    """single user version of bitsyblog"""

    def get(self):
        ### user space
        user, path = self.userpath()
        if user not in self.users:
            return exc.HTTPNotFound("No blog found for %s" % user)

        return self.get_user_space(user, path)

    def userpath(self):
        path = self.request.path_info.strip('/').split('/')
        if path == ['']:
            path = []
        return self.user, path

    def user_url(self, user, *args, **kw):
        permalink = kw.get('permalink')
        if permalink:
            _args = [ self.request.host_url ]
        else:
            _args = [ ]
        _args.extend(args)
        return '/'.join([str(arg) for arg in _args])

    def passwords(self):
        return { self.user: self.users.password(self.user) }

    def site_nav(self):
        """returns HTML for site navigation"""
        links = [('/', self.user), ]
        user = self.authenticated()
        if user:
            links.extend([
                          ('/post', 'post'),
                          ('/preferences', 'preferences'),
                          ('/logout', 'logout')])
        else:
            links.append(('/login', 'login'))

        if hasattr(self, 'help'):
            links.append(('/help', 'help'))

        links = [ markup.link(*i) for i in links ]
        return markup.listify(links, ordered=False, **{ 'class': 'site-nav'})
