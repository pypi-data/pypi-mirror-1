from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse
from django.conf import settings

import os

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
     '',

    # Uncomment the next line to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line for to enable the admin:
    (r'^admin/(.*)', admin.site.root),

    (r'^drilldown/', include('softwarefabrica.django.drilldown.urls')),
)

#if settings.DEBUG:
#    urlpatterns += patterns(
#        '',
#
#        # static media (development only)
#        (r'^static/(?P<path>.*)$',  'django.views.static.serve', {'document_root': settings.STATIC_ROOT}), # STATIC_MEDIA_DIR
#        (r'^uploads/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}), # UPLOAD_MEDIA_DIR
#        (r'^favicon.ico$',  'django.views.static.serve', {'document_root': os.path.join(settings.STATIC_ROOT, "images")}),
#    )
