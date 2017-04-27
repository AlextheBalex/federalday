# -*- coding: utf-8 -*
from __future__ import unicode_literals

from django.conf.urls import url
from views import *

app_name = "basics"
urlpatterns = [
    url(r'^doc_index/',                 doc_index_view, name="document_index"),
    url(r'^speaker_index/',             speaker_index_view, name="speaker_index"),
    url(r'^party_index/',               party_index_view, name="party_index"),
    url(r'^function_index/',            function_index_view, name="function_index"),
    url(r'^document/(?P<id>[0-9]+)/',   document_view, name="document"),
    url(r'^speaker/(?P<id>[0-9]+)/',    speaker_view, name="speaker"),
    url(r'^function/(?P<id>[0-9]+)/',   function_view, name="function"),
    url(r'^party/(?P<id>[0-9]+)/',      party_view, name="party"),
    url(r'^statements_search/',         statements_search_view, name="statements_search"),
]
