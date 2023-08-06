### imports

import dateutil.parser  # XXX separate, for now
import parser # bitsyblog parser

import datetime
import docutils
import docutils.core
import inspect
import markup
import os
import re
import shutil
import urllib
import urllib2

from glob import glob
from lxml import etree
from markup.form import Form
from cStringIO import StringIO
from webob import Request, Response, exc

### utlity functions

def validate_css(css):
    """use a webservice to determine if the argument is valid css"""    
    url = 'http://jigsaw.w3.org/css-validator/validator?text=%s'
    url = url % urllib.quote_plus(css)
    foo = urllib2.urlopen(url)
    text = foo.read()
    return not 'We found the following errors' in text

### exceptions

class DateStampException(Exception):
    """exception when parsing a datestamp"""

class BlogPathException(Exception):
    """exception when trying to retrieve the blog"""

### the main course

class BitsyBlog(object):
    """
    a very tiny blog
    """

    ### class level variables
    defaults = { 'date_format': '%H:%M %F',
                 'file_dir': os.path.dirname(__file__),
                 'subject': '[ %(date)s ]:',
                 'n_links': 5, # number of links for navigation
                 'site_name': 'bitsyblog'
                 }

    timestamp = '%Y%m%d%H%M%S'
    file_format = ( 'YYYY', 'MM', 'DD', 'HH', 'MM', 'SS' )
    permissions = { '': 'public', 'secret': 'secret', 'private': 'private' }
    paths = dict([(value, key) for key, value in permissions.items()])
    roles = { 'public': ( 'public', ),
              'friend': ( 'public', 'secret' ),
              'author': ( 'public', 'secret', 'private' ), }

    def __init__(self, **kw):
        for key in self.defaults:
            setattr(self, key, kw.get(key, self.defaults[key]))
        self.n_links = int(self.n_links) # could be a string from the .ini
        self.cooker = self.restructuredText
        self.response_functions = { 'GET': self.get,
                                    'POST': self.post,
                                    'PUT': self.put
                                    }

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

        # just a static site.css for now
        if path == 'css/site.css':
            css_file = os.path.join(self.file_dir, 'site.css')
            return self.get_response(file(css_file).read(), content_type='text/css')

        # logo
        if path == 'bitsyblog.png':
            logo = os.path.join(self.file_dir, 'bitsyblog.png')
            return self.get_response(file(logo, 'rb').read(), content_type='image/png')

        path = path.split('/')
        user = path.pop(0)
        if user not in self.users():
            return exc.HTTPNotFound("No blog found for %s" % user)            
        check = self.check_user(user)

        # special paths
        if path == [ 'post' ]:
            if check is not None:
                return check
            return self.get_response(self.form_post(user))

        if path == [ 'preferences' ]:
            if user in self.users():
                if check is not None:
                    return check
                return self.get_response(self.preferences(user))
            else:
                return exc.HTTPNotFound("No blog found for %s" % user)

        if len(path) == 2:
            if path[0] == 'css':
                if path[1] in self.css_files(user):
                    css = file(os.path.join(self.home(user), 'css', path[1]))
                    return self.get_response(css.read(), content_type='text/css')
                else:
                    return exc.HTTPNotFound('CSS file "%s" not found' % path[1])

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
        write a blog entry
        """
        # TODO: posting to '/' ?
        
        # find user + path
        user, path = self.user()

        if user not in self.users():
            return exc.HTTPNotFound("No blog found for %s" % user)
        
        check = self.check_user(user)
        if check is not None:
            return check

        if len(path):
            if path == [ 'preferences' ] and user in self.users():
                # XXX should move to its own function
                self.request.POST.pop('submit') # don't need this key
                errors = self.preferences_form(user).validate(self.request.POST)

                # date format
                format = self.request.POST.get('Date format')
                if format:
                    res = parser.parser()._parse(format)
                    if res:
                        self.request.POST['Date format'] = res.format
                    else:
                        errors['Date format'] = 'unrecognized date format: %s' % format

                # subject
                self.request.POST['Subject'] = self.request.POST.pop('Subject-0') + '%(date)s' + self.request.POST.pop('Subject-2')

                # uploaded CSS file
                css_file = self.request.POST.pop('CSS file')
                if hasattr(css_file, 'FieldStorageClass'): # XXX hack
                    contents = css_file.file.read()
                    filename = css_file.filename
                    if validate_css(contents):
                        if not filename.endswith('.css'):
                            filename = '%s.css' % filename
                        new_css_file = file(self.home(user, 'css', filename),
                                            'w')
                        print >> new_css_file, contents
                        self.request.POST['CSS'] = filename.rsplit('.css', 1)[0]
                    else:
                        errors['CSS file'] = '%s is not valid CSS' % filename

                # friends
                friends = self.request.POST.getall('Friends')
                self.request.POST['Friends'] = ', '.join(friends)

                if errors: # re-display form with errors                    
                    return self.get_response(self.preferences(user, errors))

                # write user preferences
                filename = self.preferences_file(user)
                preferences = file(filename, 'w')
                for key, value in self.request.POST.items():
                    print >> preferences, '%s: %s' % ( key, value )
                preferences.close()
                return self.get_response(self.preferences(user, message='Changes saved'))

            return exc.HTTPMethodNotAllowed("Not sure what you're trying to do")

        directory = self.home(user)

        body = self.request.body
        body = self.request.POST.get('form-post', body)
        body = body.strip()

        # determine if the post is secret or private
        privacy = self.request.GET.get('privacy') or self.request.POST.get('privacy')
        if privacy == 'public':
            privacy = ''

        # write the file
        now = datetime.datetime.now()
        location = "/%s/%s" % (user, self.datestamp(now))
        filename = self.filename(user, now, privacy=privacy)
        blog = file(filename, 'w')
        print >> blog, body

        # XXX return to user blog home or the post itself?
        return exc.HTTPSeeOther("Post blogged by bitsy", location=location)

    def put(self):
        """
        PUT several blog entries from a file
        """

        # find user + path
        user, path = self.user()

        if user not in self.users():
            return exc.HTTPNotFound("No blog found for %s" % user)

        if len(path):
            return exc.HTTPMethodNotAllowed("Not sure what you're trying to do")
        
        directory = self.home(user)

        # find the dates + entries in the file
        regex = '\[.*\]:'
        entries = re.split(regex, self.request.body)[1:]
        dates = [ date.strip().strip(':').strip('[]').strip()
                  for date in re.findall(regex, self.request.body) ]
        dates = [ dateutil.parser.parse(date) for date in dates ]

        for i in range(len(entries)):
            filename = self.filename(user, dates[i])
            entry = file(filename, 'w')
            print >> entry, entries[i].strip()
        
        return exc.HTTPOk("%s posts blogged by bitsy" % len(entries))


    def error(self):
        methods = ', '.join(self.response_functions.keys()[:1]) 
        methods += ' and %s' % self.response_functions.keys()[-1] 
        return exc.HTTPMethodNotAllowed("Only %s operations are allowed" % methods)

    ### auth functions

    def authenticated(self):
        """return authenticated user"""
        return self.request.environ.get('REMOTE_USER')

    def check_user(self, user):
        """returns None on success"""
        # determine authenticated user
        authenticated = self.authenticated()
        if authenticated is None:
            return exc.HTTPUnauthorized('Unauthorized')
        elif user != authenticated:
            return exc.HTTPForbidden("Forbidden")        

    def role(self, user):
        auth = self.authenticated()
        if not auth:
            return 'public'
        if auth == user:
            return 'author'
        else:
            if auth in self.get_preferences(user)['Friends']:
                return 'friend'
            else:
                return 'public'

    ### user methods

    def user(self):
        """user who's blog one is viewing"""        
        path = self.request.path_info.strip('/').split('/')
        name = path[0]
        path = path[1:]
        if not name:
            name = None
        return name, path

    def users(self):
        retval = set()
        ignores = [ '.svn' ]
        for user in os.listdir(self.file_dir):
            # ensure integrity of user folder
            if user in ignores:
                continue
            if os.path.isdir(os.path.join(self.file_dir, user)):
                retval.add(user)
        return retval

    def passwords(self):
        users = self.users()
        passwords = {}
        pw_file = '.password' # name of the password file on the filesystem
        for user in users:
            password = self.home(user, pw_file)
            if os.path.exists(password):
                password = file(password).read().strip()
            else:
                password = ' ' # unspecified password
            passwords[user] = password
        return passwords

    def newuser(self, user, password):
        """create a new user account"""
        # TODO: security

        # characters forbidden in user name
        forbidden = ' |<>./?,'  
        if [ i for i in forbidden if i in user ]:
            raise HTTPForbidden("username '%s' contains forbidden characters [%s]" % (user, forbidden)).exception
        
        home = self.home(user)
        os.mkdir(home)
        pw_file = file(os.path.join(home, '.password'), 'w')
        print >> pw_file, password
        entries = os.path.join(home, 'entries') 
        os.mkdir(entries)
        os.mkdir(os.path.join(entries, 'secret'))
        os.mkdir(os.path.join(entries, 'private'))
        css_dir = os.path.join(home, 'css') 
        os.mkdir(css_dir)
        shutil.copyfile(os.path.join(self.file_dir, 'site.css'),
                        os.path.join(css_dir, 'default.css'))

    def home(self, user, *args):
        return os.path.join(self.file_dir, user, *args)

    def filename(self, user, datetime, privacy=None):
        filename = ''
        if privacy:
            filename = '%s/' % privacy
        filename = '%s%s' % ( filename, datetime.strftime(self.timestamp))
        return os.path.join(self.home(user),
                            'entries',
                            filename)

    def preferences_file(self, user):
        filename = 'preferences.txt'
        return  os.path.join(self.home(user), filename)

    def get_preferences(self, user):
        """returns a dictionary of user preferences from a file"""
        
        filename = self.preferences_file(user)
        if not os.path.exists(filename):
            # XXX maybe should make the file, too?
            return {}
        prefs = file(filename).read().split('\n')
        prefs = [ i for i in prefs if i.strip() ]
        prefs = [ [ j.strip() for j in i.split(':', 1) ] for i in prefs
                  if ':' in i] # probably not necessary
        prefs = dict(prefs)

        # assemble friends from a list
        friends = prefs.get('Friends') # can see private blog posts
        if friends:
            prefs['Friends'] = friends.split(', ')
        else:
            prefs['Friends'] = []
        
        return prefs

    def css_files(self, user):
        default = self.get_preferences(user).get('CSS')
        css_files = [ i for i in os.listdir(os.path.join(self.home(user),
                                                         'css'))
                      if i.endswith('.css') ]
        if default:
            default = '%s.css' % default
            try:
                index = css_files.index(default)
                css_files.insert(0, css_files.pop(index))
            except ValueError:
                pass
        return css_files
                
    ### date methods

    def date_args(self):
        index = 'year'
        argspec = inspect.getargspec(self.get_blog_entries)[0]
        return argspec[argspec.index(index):]

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

    def get_blog(self, user, path, role='public'):
        """auth: authorized user"""

        # get permissions
        allowed = [ self.paths[permission] for permission in self.roles[role] ]

        # individual blog entry
        if (len(path) == 1) and (len(path[0]) == len(''.join(self.file_format))):
            date = self.date(path[0])
            for privacy_setting in allowed:
                filename = self.filename(user, date, privacy_setting)
                if os.path.exists(filename):
                    entry = file(filename).read()
                    break                
            else:
                raise BlogPathException("No blog entry for %s" % path[0])
            blog = [ (date, entry, self.permissions[privacy_setting]) ]
            return blog
            
        # parse the path into a date path
        n_date_vals = len(self.date_args())
        if len(path) > n_date_vals:
            raise BlogPathException("blog entry not found")

        # ensure the path conforms to expected values (ints):
        try:
            [ int(i) for i in path]
        except ValueError:
            raise BlogPathException("blog entry not found")

        # get the blog
        blog = self.get_blog_entries(user, role, None, *path)
        return blog

    def get_blog_entries(self, user,
                         role='public',
                         n=None, # number of entries (could go in **kw)
                         year=None, month=None, day=None, hour=None):

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
        retval = []
        for r in self.roles[role]:
            files = glob(os.path.join(directory, self.paths[r], glob_expr))
            retval.extend([ (self.date(filename), filename, r)
                            for filename in files ])
        retval.sort(key=lambda x: x[0], reverse=True)
        retval = retval[:n]
        retval = [ (entry[0], file(entry[1]).read(), entry[2])
                   for entry in retval ]
        return retval

    ### methods that write HTML

    def render(self, body, title=(), stylesheets=(), head_markup=()):
        """layout the page in a unified way"""
        title = list(title)
        title.append(self.site_name)
        title = ' - '.join(title)
        return markup.wrap(self.site_nav()+body, title, stylesheets,
                           head_markup=head_markup)

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

        # TODO: display login form (maybe)
        
        # get the users
        users = self.users()

        blogs = {}
        for user in users:
            blog = self.get_blog_entries(user, 'public', n_links)
            if blog:
                blogs[user] = blog
        users = blogs.keys()

        # display latest active user first
        users.sort(key=lambda user: blogs[user][0][0], reverse=True)

        # display users' blogs
        for user in users:
            print >> retval, '<div id="%s" class="user">' % user
            print >> retval, '<a href="%s">%s</a>' % (user, user)
            blog = blogs[user]
            print >> retval, self.navigation(user, blog, '/%s' % user, n_links)
            print >> retval, '</div>'

        return self.render(retval.getvalue(), stylesheets=(("css/site.css", "Default"),))

    def navigation(self, user, blog, path, n_links, n_char=80):
        prefs = self.get_preferences(user)
        
        if n_links == 0 or not len(blog):
            return ''
        retval = StringIO()
        print >> retval, '<div class="navigation">\n<ul>'
        more = ''
        if (n_links != -1) and (len(blog) > n_links):
            more = '<a href="%s?n=all">more</a>' % path
            blog = blog[:n_links]

        for date, text, privacy_setting in blog:
            id = self.datestamp(date)
            format = prefs.get('Date format', self.date_format)
            date = date.strftime(format)
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

    def blog_entry(self, user, date, text, privacy):
        """given the content string, return a marked-up blog entry"""

        # user preferences
        prefs = self.get_preferences(user)
        format = prefs.get('Date format', self.date_format)
        subject = prefs.get('Subject', self.subject)

        role = self.role(user)
        
        subject = subject % { 'date' : date.strftime(format) }
        html = StringIO()
        id = self.datestamp(date)
        print >> html, '<div id="%s" class="blog-entry">' % id
        print >> html, '<a name="%s" />' % id
        print >> html, '<div class="subject">'
        print >> html, '<a href="/%s/%s">%s</a>' % (user, id, subject)
        if (privacy == 'secret') and (role == 'friend'):
            print >> html, '<em>secret</em>'
        print >> html, '</div>'
        print >> html, self.cooker(text)

        if role == 'author':
            print >> html, '<div><form>'
            print >> html, self.privacy_settings(privacy)
            print >> html, '</form></div>'
        
        print >> html, '</div>'
        return html.getvalue()
        
    def write_blog(self, user, blog, path, n_links):
        stylesheets = self.css_files(user)
        stylesheets = [ (("/%s/css/%s" % (user, css)),
                         css.rsplit('.css', 1)[0]) for css in stylesheets ]

        retval = StringIO()
        print >> retval,  self.navigation(user, blog, path, n_links, 0)
        for date, text, privacy_setting in blog:
            print >> retval, self.blog_entry(user, date, text, privacy_setting)
        return self.render(retval.getvalue(), title=(user,),
                           stylesheets=stylesheets)
                           
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
        return self.render(retval.getvalue(), title=(user,))

    def preferences_form(self, user):
        prefs = self.get_preferences(user)
        form = Form()

        # date format
        format = prefs.get('Date format', self.date_format)
        value = datetime.datetime.now().strftime(format)
        form.add_element('textfield', 'Date format', value=value,
                         help='format to display dates in your blog post title')

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
                          help='format to display the subject line of your blog post'
                          )
                          
        # CSS files
        css_files = [ i.rsplit('.css', 1)[0]  for i in self.css_files(user) ]
        form.add_element('menu', 'CSS', css_files,
                         help='which CSS file should be the default')
        # or upload a CSS file
        form.add_element('file_upload', 'CSS file',
                         help='upload a CSS file to theme your webpage')

        # Friends -- can see secret posts
        users = [ i for i in self.users() if i != user ]
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
        return self.render(body, title=("preferences", user))

    def privacy_settings(self, default='public'):
        """HTML snippet for privacy settings"""
        settings = (('public', 'viewable to everyone'),
                    ('secret', 'viewable only to your friends'),
                    ('private', 'viewable only to you'))
        form = Form()
        return form.radiobuttons('privacy', settings, checked=default, joiner=' ')
