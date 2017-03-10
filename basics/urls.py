# -*- coding: utf-8 -*
from __future__ import unicode_literals

from django.conf.urls import url
from views import *

app_name = "basics"
urlpatterns = [
    url(r'^doc_index/',                 doc_index_view, name="document_index"),
    url(r'^speaker_index/',             speaker_index_view, name="speaker_index"),
    url(r'^document/(?P<id>[0-9]*)/',   document_view, name="document"),
    url(r'^speaker/(?P<id>[0-9]*)/',    speaker_view, name="speaker"),
]
