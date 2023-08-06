from django.conf.urls.defaults import *
from django.conf import settings

from softwarefabrica.django.drilldown.views import generic_drilldown

# -- URL patterns --------------------------------------------------------

urlpatterns = patterns(
    '',

    # -- generic drill-down view -----------------------------------------

    url(r'^(?P<app_label>[a-zA-Z0-9_\-\.]+)/(?P<model_name>[a-zA-Z0-9_]+)/(?P<url>.*)$',
        generic_drilldown,
        name="drilldown-generic-drilldown"),
)
