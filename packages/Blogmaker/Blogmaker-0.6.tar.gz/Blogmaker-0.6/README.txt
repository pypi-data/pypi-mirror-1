============================================
Blogmaker |(tm)| blog application for Django
============================================

Blogmaker 0.6, January 2008

Blogmaker |(tm)| is a full-featured, production-quality blogging application for Django.
It supports trackbacks, ping and comments with moderation and honeypot spam prevention. 

Blogmaker is released under a BSD license.  You may "copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software" (to borrow a phrase from the more-or-less equivalent "MIT License").

Caveat: the current release (including these docs) is for people who are already familiar with Django or willing to poke around a bit.  We developed Blogmaker for our own projects, though we hope it will help others leverage the awesome Django framework to create feature-rich blogs.  We have additional features planned, and welcome contributions from others.


.. Note: this document is written in reStructuredText (http://docutils.sourceforge.net/rst.html)
.. contents::

------------------------------------------
Features
------------------------------------------

- Create and edit blog entries with the Django admin interface or a custom interface with preview
- Blog entries may be marked up as HTML or Markdown_ text (using python-markdown_)
- Comment on blog entries (based on django.contrib.comments)
- Comment honeypot for transparent spam protection, based on ideas from http://www.nedbatchelder.com/text/stopbots.html
- Comment moderation, based on James Bennett's comment_utils_
- Ping other sites when blog entries are added (thanks to `iMalm.com <http://www.imalm.com/blog/2007/feb/10/using-django-signals-ping-sites-update/>`_)
- Post trackbacks to other blogs
- Receive trackbacks from other blogs, checking that the referring page does link to the referenced entry to reduce trackback spam
- Independent RSS feeds for posts and comments
- Archives by year, month and day; the day archive includes navigation links to every other day in the month which contains a post
- Tags, including a tag index page
- Sidebars for tags and recent posts
- Previous and next links include post titles
- Search blog entries
- Multiple authors and archive by author
- Scheduled posts
- Optionally host the blog from its own domain or subdomain


Blogmaker is production-ready; it powers our two blogs at http://blog.blogcosm.com/ and http://prefabcosm.com/blog/.

.. _Markdown: http://daringfireball.net/projects/markdown/
.. _python-markdown: http://www.freewisdom.org/projects/python-markdown/
.. _comment_utils: http://code.google.com/p/django-comment-utils/


------------------------------------------
Download and support
------------------------------------------

The latest version of this document is available from http://blogcosm.com/media/blog/release/README.html. Blogmaker can be downloaded from http://blogcosm.com/media/blog/release/ or from the Google Code project at http://code.google.com/p/blogmaker/. If you have any questions, comments or patches, please send email to the blogmaker-users_ group.

.. _blogmaker-users: http://groups.google.com/group/blogmaker-users

------------------------------------------
Credits
------------------------------------------

| Scott S. Lawton: product manager
| Peter Bernheim: primary developer
| Kent S Johnson: developer and in-house Python expert

Blogmaker is a trademark of PreFab Software, Inc.

Portions of Blogmaker are based on the blog application example at `23 excuses`_ and Copyright |(c)| 2006, Andrew Gwozdziewycz.

Portions of blogmaker.comments are based on James Bennett's comment_utils_ and Copyright |(c)| 2007, James Bennett.

Portions of blogmaker.comments are based on django.contrib.comments and are Copyright |(c)| 2005, the Lawrence Journal-World.

See the file LICENSE.txt for details.

jQuery 1.2.1 is Copyright |(c)| 2007 John Resig (jquery.com) and Dual licensed under the MIT (MIT-LICENSE.txt) and GPL (GPL-LICENSE.txt) licenses.  Blogmaker includes it under the provisions of the MIT license.

feedparser is Copyright |(c)| 2002-2006, Mark Pilgrim, All rights reserved.

.. _23 excuses: http://www.23excuses.com/2006/Jul/07/23-excuses-release-and-introduction/


------------------------------------------
Requirements
------------------------------------------

Blogmaker requires Python 2.5; earlier versions will not work. Blogmaker works with Django 0.96; it has not been tested with later releases.

To include images in blog entries, you must have `Python Imaging Library`_ installed. This is a requirement of Django's `ImageField`_.

In order to install Blogmaker, you must first set up a basic Django site with the usual settings file, base template, and primary urls.py. More information can be found at http://www.djangoproject.com/

Blogmaker requires the installation of two (included) Django applications:

1. blogmaker.comments (which can be used on the non-blog portions of a site)
2. blogmaker.util (a set of utilities shared internally with our unreleased non-blog code)

Blogmaker uses DbMigration_ to update the database.  DbMigration is required only for future schema evolution; if there are future schema changes, we plan to include migrations to update the database as required. Although DbMigration works with any database, our usage is specific to PostgreSQL; using our migrations with other databases will require some changes.

Other features of Blogmaker will work with any Django-compatible database engine.

.. _Python Imaging Library: http://www.pythonware.com/products/pil/
.. _ImageField: http://www.djangoproject.com/documentation/0.96/model-api/#imagefield
.. _DbMigration: http://www.aswmc.com/dbmigration/


------------------------------------------
Settings
------------------------------------------

Blogmaker requires a number of settings to be defined in your settings file:

``INSTALLED_APPS``
  Add ``'blogmaker.blog'``, ``'blogmaker.comments'`` and ``'blogmaker.util'`` to the list of installed applications. We also require some or all of these standard applications:
  
| django.contrib.auth
| django.contrib.contenttypes
| django.contrib.sessions
| django.contrib.humanize
| django.contrib.sites
| django.contrib.markup
| django.contrib.admin
  

``TEMPLATE_CONTEXT_PROCESSORS``
      Blogmaker's comment application requires that ``django.core.context_processors.request`` be one of your installed context processors. This puts a ``request`` object in the context. The comment honeypot uses this to access the IP address of a request.

``DEFAULT_BLOG_USER``
  The id of the primary blog user, as defined by the Django Auth/User model.
  
``LOG_DIRECTORY``
  The directory where log files will be written.
  
``COPYRIGHT``
  Your copyright text, e.g. "All contents Copyright 2007, Acme Inc."
  
``SITE_ROOT``
  Defines the root URL of your site, e.g. http://domain.com/
  
``BLOG_MEDIA_PREFIX``
  URL prefix for where you will serve the media directory contained at blogmaker.blog.media.  Make sure to use a  trailing slash.
  Examples: "/media/blog/", "http://foo.com/media/blog/"

``ADMIN_MEDIA_PREFIX``
  URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a trailing slash.
  Examples: "/media/admin/", "http://foo.com/media/admin/"
  
``BLOG_ROOT``
  Defines the root URL for the blog path, e.g. if you want the blog to live at http://domain.com/blog/, this variable would be set to '/blog/'. If you want the blog to live at a different subdomain than the rest of the site, you will need to set an absolute URL: 'http://blog.domain.com/'

If you include images in your blog entries, you should set ``MEDIA_ROOT`` and ``MEDIA_URL`` as described in the `Django documentation <http://www.djangoproject.com/documentation/0.96/settings/#media-root>`_. You must also configure your server to serve files from ``MEDIA_ROOT`` at ``MEDIA_URL``.

The following should be set if you enable email notification for comment/trackback features:

``MANAGERS``
  A list of ``('Name', 'email address')`` tuples defining the people to whom notification emails will be sent.
  
``DEFAULT_FROM_EMAIL``
  The default e-mail you would like e-mails to be sent from.


------------------------------------------
Other setup and tips
------------------------------------------

Add a reference to ``blogmaker.blog.urls`` and ``blogmaker.blog.admin_urls`` to your ``urls.py`` with any desired prefix, for example::

  (r'^blog/', include('blogmaker.blog.urls')),
  (r'^blogmaker/', include('blogmaker.blog.admin_urls')),

Comments are moderated using a version of comment_utils_. The setup is the same as for comment_utils. For example, to moderate first-time comments with email notification, include this code in your project::

  from blogmaker.comments.moderation import ModerateFirstTimers, moderator
  from blogmaker.blog.models import Entry

  class Moderator(ModerateFirstTimers):
      email_notification = True

  moderator.register(Entry, Moderator)

See the `comment_utils docs <http://django-comment-utils.googlecode.com/svn/trunk/docs/>`_ for more options. This code must run once when your server starts up. `This blog post <http://www.b-list.org/weblog/2007/nov/05/server-startup/>`_ has some suggestions of where to put startup code.

Note: Blogmaker contains forked copies of both django.contrib.comments and comment_utils. You do not need to install the standard comments and comment_utils applications to use Blogmaker.

Blog entries may be written in straight HTML or using Markdown_ markup. Blogmaker also defines a few shortcuts in the form ``%portal%``. See ``expand_shortcuts()`` in ``util/__init__.py`` for the full list.

Trackbacks to other blogs are not posted automatically. To post trackbacks, run ``blogmaker.blog.trackback_update.py``. You may want to run this from a cron job.

View, modify and post trackbacks for an individual blog entry by adding ``/postTrackbacks/`` to the public URL for the entry.

Trackbacks may be posted to a Blogmaker entry using the public URL for the entry with the suffix ``/trackback/``. To reduce trackback spam, any posted trackbacks are validated by fetching the contents of the referring page and verifying that the entry URL appears on the referring page. In addition, trackbacks are comments and may be moderated like any other comment.

------------------------------------------
Blogmaker Tools
------------------------------------------

Blogmaker Tools adds a preview option and an improved list view as an alternative to Django's built-in admin site. The tools are accessed from the ``/tools/`` URL.


------------------------------------------
Other blog applications
------------------------------------------

There are several other blogging applications for Django:

- The `23 excuses`_ application that was the start of Blogmaker (version 1.0, 2006-07-07) (download link broken at the moment)
- Banjo_ - "A Django blog with bells and whistles" from Bruce Kroeze, http://coderseye.com/. Not yet available - "nearing 0.1 release" as of 2007-11-25.
- Coltrane_ by James Bennett, http://www.b-list.org/. A bit empty as of 2007-12-05 but there is code if you look at svn.
- ibofobi_ version 0.1, 2005-12-09

.. _Banjo: https://launchpad.net/banjo
.. _Coltrane: http://code.google.com/p/coltrane-blog/
.. _ibofobi: http://code.ibofobi.dk/public/wiki/ProjectIbofobiBlog

.. Substitutions for reST:

.. |(tm)| unicode:: U+2122
   :ltrim:
.. |(c)| unicode:: 0xA9
