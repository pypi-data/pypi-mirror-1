``bitsyblog doesn't do much, but it could do less''

Why another blog?
=================

I'm a web developer so of course I can't stand to use a browser to do anything.
My ideal blog would invoke my favorite, take a bunch of text, and 
throw it on the web.  

Meet bitsyblog.  Posting is done with a POST request, so while you can use
a web form to do this, its just as easy to use curl, urllib, or anything else 
to post.


How does it work?
=================

A user URLs is like

http://bitsyblog.org/k0s

Posting to this will take the body of the post request and add a date stamp
on it.  Blog entries are thrown in files and are displayed with markup 
available with restructured text.

You can also get more specific information by narrowing down the year, month
and day in the URL:

http://bitsyblog.org/k0s/2008/2/1

Permalinks are also available in the form of the date stamp:

http://bitsyblog.biz/k0s/20080201141502

Looking at the navigation will help determine the date stamp (basically, 
replace the '#' with a '/').

If you really want to post through the web, rudimentary support is
at 

http://bitsyblog.org/k0s/post

It works, its just ugly.


What bitsyblog doesn't do
=========================

* Authentication:  this is a big one.  Ideally, this should be done
with some WSGI middleware, but currently I've just punted on this.  Anyone
can post to anyone's blog!  Oops!  To create a new user, just post to an
account that does not yet exist.  I hope to correct this soon, but please don't
wait for me.

* Commenting:  this should done with a third-party app.  I have some ideas
here, but nothing to show yet.

* Tagging:  again, this should be done with a third-party app.

* Hosting files:  Its a blog, not a file repo!  Any markup doable with 
restructured text is doable with bitsyblog, but images, videos, etc must
be held off-site.


What is next for bitsyblog?
===========================

While bitsyblog doesn't do much and could do less.  Nonetheless, I would at least
like to allow user preferences.  Users should be able to upload (verifiable) CSS.
Also, users should be able to set the subject line and date format for their blog.
For the dateformat, I plan on patching dateutil.parser to return the format string
that the date was originally in.

It might be a good idea to add in RSS/atom feeds too.  This seems like it should belong
to the app itself instead of a third party.

There is currently no help and almost non-existent UI.  Maybe I should fix this.  I
have mixed emotions about it.

I would also like to do a code review while there isn't much code.

Other than that, its a pretty small project.  No templates and currently less than 500
lines of code.

I'm guessing your blog doesn't do much...but could it do less?
