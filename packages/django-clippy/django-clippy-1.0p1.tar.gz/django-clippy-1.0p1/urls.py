from django.conf.urls.defaults import *
from django.conf import settings
        
urlpatterns = patterns('',
    (r'^mymedia/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
    ('^$', 'django.views.generic.simple.direct_to_template', {'template': 'clippy/demo.html'}),
)
