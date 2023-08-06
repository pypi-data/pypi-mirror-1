from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^project/search/', 'core.views.search', {'model': 'core.Project'}),
    (r'^project/', 'core.views. handle', {'model': 'core.Project'}),
    
    (r'^folder/search/', 'core.views.search', {'model': 'core.Folder'}),
    (r'^folder/', 'core.views. handle', {'model': 'core.Folder'}),
    
    (r'^ticket/search/', 'core.views.search', {'model': 'core.Ticket'}),
    (r'^ticket/', 'core.views. handle', {'model': 'core.Ticket'}),
    
    (r'^document/search/', 'core.views.search', {'model': 'core.Document'}),
    (r'^document/', 'core.views. handle', {'model': 'core.Document'}),
    
    (r'^user/search/', 'core.views.search', {'model': 'auth.User'}),
    (r'^user/', 'core.views. handle', {'model': 'auth.User'}),
    
    (r'^group/search/', 'core.views.search', {'model': 'auth.Group'}),
    (r'^group/', 'core.views. handle', {'model': 'auth.Group'}),
    
    (r'^auth/login/', 'core.views.login'),
    (r'^auth/logout/', 'core.views.logout'),
    
    (r'^store/([\w-]*)/', 'core.views.store'),
    
    (r'^~([\w-]*)/$', 'core.views.index'),
    (r'^$', 'core.views.index'),
)

### Serve Static Pattern ###
from django.conf import settings

if getattr(settings, 'MEDIA_SERVE', False):
    urlpatterns = patterns('', 
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_PATH}),
    ) + urlpatterns
###
