from django.conf.urls.defaults import *
from django.conf import settings

from softwarefabrica.django.forms.views import ajax_cascade_select

# -- URL patterns --------------------------------------------------------

urlpatterns = patterns(
    '',

    # -- Ajax cascade select view ----------------------------------------

    url(r'^ajax_cascade_select/$',
        ajax_cascade_select,
        name="forms-ajax-cascade-select"),
)
