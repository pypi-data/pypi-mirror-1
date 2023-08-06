from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    (r'^gutentag/$', 'tagbase.gutentag.views.main'),
    (r'^gutentag/add/$', 'tagbase.gutentag.views.add'),
    (r'^gutentag/doblast/$', 'tagbase.gutentag.views.doblast'),
    (r'^gutentag/blastSearch/$', 'tagbase.gutentag.views.blastSearch'),
    (r'^gutentag/upload/$', 'tagbase.gutentag.views.upload'),
    (r'^gutentag/go/(?P<go_id>\d+)/$', 'tagbase.gutentag.views.go'),
    (r'^gutentag/goSeq/(?P<go_id>\d+)/$', 'tagbase.gutentag.views.goSeq'),
    (r'^gutentag/mainSearch/$', 'tagbase.gutentag.views.mainSearch'),
    (r'^gutentag/getSeq/$', 'tagbase.gutentag.views.getSeq'),
    (r'^gutentag/getTags/(?P<gene_id>\w+)/$', 'tagbase.gutentag.views.getTags'),
    (r'^gutentag/getThisSeq/(?P<seq_id>\w+)/$', 'tagbase.gutentag.views.getThisSeq'),
    (r'^gutentag/(?P<tag_name>\w.+)/(?P<tag_type>\w+)/tag/$', 'tagbase.gutentag.views.tagCloudSearch'), #\w matches letters and digits
#    (r'^admin/(.*)', admin.site.root),      # for django 1.0.3
    (r'^admin/', include(admin.site.urls)),
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.STATIC_DOC_ROOT}),

    
)
'''
 #only let dhango serve static media files in development environment
if settings.DEBUG:   
   	 urlpatterns += patterns('',
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/path/to/media'}),)
        '''
        
        
