# -*- coding: utf-8 -*
from __future__ import unicode_literals

from django.shortcuts import render, Http404
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from models import *

def default_redirect(request):
    return HttpResponseRedirect(reverse("basics:document_index"))

def doc_index_view(request):
    ctx = {
        "title": _("document index"),
        "documents": Document.objects.all(),
    }

    return render(request, "basics/document_index.html", ctx)


def speaker_index_view(request):
    ctx = {
        "title": _("speaker index"),
        "speakers": Speaker.objects.all(),
    }

    return render(request, "basics/speaker_index.html", ctx)


def document_view(request, id):
    try:
        doc = Document.objects.get(document_id=id)
    except Document.DoesNotExist:
        raise Http404

    stmts = RegularStatement.objects.filter(document=doc).order_by("order_id")

    ctx = {
        "title": "document %s / %s" % (doc.document_id, doc.date),
        "statements": stmts,
    }

    return render(request, "basics/document.html", ctx)

def speaker_view(request, id):
    try:
        speaker = Speaker.objects.get(pk=id)
    except Speaker.DoesNotExist:
        raise Http404

    search_word = request.GET.get("word", "")

    filters = {
        "speaker": speaker,
    }
    if search_word:
        filters["text__icontains"] = search_word
    stmts = RegularStatement.objects.filter(**filters).order_by("document__date", "order_id")

    form = """
    <form name="word-search-form" method="GET">
        <input type="text" name="word" value="" placeholder="%s"/>
    </form>
    """ % (_("search word"))



    ctx = {
        "title": "%s" % speaker,
        "form": form,
        "statements": stmts,
    }

    return render(request, "basics/speaker.html", ctx)