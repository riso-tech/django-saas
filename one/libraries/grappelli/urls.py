from django.urls import path, re_path

from .settings import SWITCH_USER_REGEX
from .views.related import AutocompleteLookup, M2MLookup, RelatedLookup
from .views.switch import switch_user

urlpatterns = [
    # FOREIGNKEY & GENERIC LOOKUP
    path("lookup/related/", RelatedLookup.as_view(), name="grp_related_lookup"),
    path("lookup/m2m/", M2MLookup.as_view(), name="grp_m2m_lookup"),
    path("lookup/autocomplete/", AutocompleteLookup.as_view(), name="grp_autocomplete_lookup"),
    # SWITCH USER
    re_path(rf"^switch/user/(?P<object_id>{SWITCH_USER_REGEX})/$", switch_user, name="grp_switch_user"),
]
