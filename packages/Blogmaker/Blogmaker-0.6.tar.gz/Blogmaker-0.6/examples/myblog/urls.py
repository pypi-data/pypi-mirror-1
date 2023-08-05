from django.conf import settings
from django.http import HttpResponseRedirect
from django.conf.urls.defaults import *
import os, inspect
import blogmaker.blog
import django.contrib.admin

urlpatterns = patterns('',
    (r'^blog/', include('blogmaker.blog.urls')),
    (r'^comments/', include('blogmaker.comments.urls')),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout'),
    (r'^admin/', include('django.contrib.admin.urls')),
    (r'^$', lambda r: HttpResponseRedirect('blog/')),
)

def module_media_dir(mod):
    """returns the media dir relative to a module object"""
    initfile = inspect.getfile(mod)
    relmedia = os.path.join(os.path.dirname(initfile), 'media')
    if not os.path.exists(relmedia):
        raise OSError("Could not find media directory relative to module %s (tried %s)" % (
                                                                mod.__name__, relmedia))
    return os.path.abspath(relmedia)
    
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/custom/(.*)$', 
        'django.views.static.serve', {
            'show_indexes': True,
            'document_root': os.path.join(os.path.dirname(__file__), 'media')}),
        (r'^' + settings.BLOG_MEDIA_PREFIX[1:] + '(.*)$', 
        'django.views.static.serve', {
            'show_indexes': True,
            'document_root': module_media_dir(blogmaker.blog)}),
        (r'^' + settings.ADMIN_MEDIA_PREFIX[1:] + '(.*)$', 
        'django.views.static.serve', {
            'show_indexes': True,
            'document_root': module_media_dir(django.contrib.admin)}),
    )
