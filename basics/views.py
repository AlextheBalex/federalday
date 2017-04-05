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
        "speakers": Speaker.objects.all().order_by("name"),
    }

    return render(request, "basics/speaker_index.html", ctx)


def party_index_view(request):
    ctx = {
        "title": _("party index"),
        "parties": Party.objects.all(),
    }

    return render(request, "basics/party_index.html", ctx)


def function_index_view(request):
    ctx = {
        "title": _("function index"),
        "functions": Function.objects.all().order_by("name"),
    }
    return render(request, "basics/function_index.html", ctx)


def document_view(request, id):
    try:
        doc = Document.objects.get(document_id=id)
    except Document.DoesNotExist:
        raise Http404

    stmts = RegularStatement.objects.filter(document=doc).order_by("order_id")


    l_speakers = list(set([stmt.speaker for stmt in stmts]))

    for index, speaker in enumerate(l_speakers):
        l_speakers[index] = [unicode(speaker), str(stmts.filter(speaker=speaker).count())]

    l_speakers = sorted(l_speakers)
    ctx = {
        "title": "Dokument %s / %s" % (doc.document_id, doc.date),
        "url": doc.url,
        "statements": stmts,
        "speakers": l_speakers,
    }

    return render(request, "basics/document.html", ctx)

def speaker_view(request, id):
    try:
        speaker = Speaker.objects.get(pk=id)
    except Speaker.DoesNotExist:
        raise Http404

    num_search_fields = 1
    search_fields = []
    for i in range(10):
        term = request.GET.get("word%s" % i, None)
        if term:
            num_search_fields = i+2
            search_fields.append(term)
        else:
            break

    filters = {
        "speaker": speaker,
    }

    if search_fields:
        stmts = RegularStatement.objects.all()
        for term in search_fields:
            or_set = None
            commas = term.split(',')
            for w in commas:
                filters["text__contains"] = w
                qset = stmts.filter(**filters)
                or_set = (or_set | qset) if or_set is not None else qset
            stmts = or_set
        stmts = stmts.order_by("document__date", "order_id")
    else:
        stmts = RegularStatement.objects.filter(**filters)

    stmt_group_number = 0
    last_order_id = 0
    last_date = ''
    number_of_active_dates = 0
    if stmts.exists():

        for stmt in stmts:
            date = stmt.document.date
            order_id = stmt.order_id
            if last_date == date and order_id - last_order_id == 1:
                stmt.group_number = stmt_group_number
            else:
                if last_date != date:
                    number_of_active_dates += 1
                last_date = date
                stmt_group_number += 1
                stmt.group_number = stmt_group_number
            last_order_id = order_id
        number_of_statements = stmts.count()
        first_date = stmts[0].document.date
    else:
        number_of_statements = 0
        first_date = "never"

    form = """<form name="word-search-form" method="GET">"""
    form += """<input type="submit" value="%s"/>""" % _("Suchen")
    for i in range(num_search_fields):
        val = request.GET.get("word%s" % i, "")
        form += """ <input type="text" name="word%s" placeholder="%s" value="%s"/>""" % (
            i, _("search word"), val)
    form += "</form>"

    ctx = {
        "title": "%s" % speaker,
        "form": form,
        "statements": stmts,
        "number_of_statements": number_of_statements,
        "number_of_statement_blocks": stmt_group_number,
        "first_date": first_date,
        "last_date": last_date,
        "number_of_active_dates": number_of_active_dates,
        "search_words": search_fields,
    }
    if search_fields:
        if not stmts:
            return render(request, "basics/speaker_filtered_word_not_found.html", ctx)
        return render(request, "basics/speaker_filtered.html", ctx)
    return render(request, "basics/speaker.html", ctx)

def function_view(request, id):
    try:
        function = Function.objects.get(pk=id)
    except Function.DoesNotExist:
        raise Http404

    search_word = request.GET.get("word", "")

    filters = {
        "speaker__function": function,
    }

    if search_word:
        filters["text__icontains"] = search_word
    stmts = RegularStatement.objects.filter(**filters).order_by("document__date", "order_id")
    list_stmts = list(stmts)

    stmt_group_number = 0
    last_order_id = 0
    last_date = ''
    last_speaker = ''
    first_speaker = list_stmts[0].speaker
    number_of_active_dates = 0
    l_speaker_stmts = []
    l_l_speaker_stmts = []

    if list_stmts:

        for stmt in stmts:

            date = stmt.document.date
            order_id = stmt.order_id
            if last_date == date and order_id - last_order_id == 1:

                l_speaker_stmts[1].append(stmt)
            else:

                if last_date != date:
                    number_of_active_dates += 1
                last_date = date
                stmt_group_number += 1
                l_l_speaker_stmts.append(l_speaker_stmts)
                l_speaker_stmts = [stmt.speaker, [stmt]]
            last_order_id = order_id
        number_of_statements = len(list_stmts)
        first_date = list_stmts[0].document.date
    else:
        number_of_statements = 0
        first_date = "never"

    last_speaker = ''
    l_speakers = []
    l_l_speaker_l_stmt_blocks = []
    l_speaker_l_stmt_blocks = []
    for line in l_l_speaker_stmts:
        if line:
            if line[0] != last_speaker:
                last_speaker = line[0]
                l_speakers.append(last_speaker)
                if line[0]:
                    l_l_speaker_l_stmt_blocks.append(l_speaker_l_stmt_blocks)
                    l_speaker_l_stmt_blocks = [line[0], [line[1]]]
            else:
                if line[1]:
                    l_speaker_l_stmt_blocks[1].append(line[1])

    l_l_speaker_l_stmt_blocks.pop(0)

    form = """
    <form name="word-search-form" method="GET">
        <input type="text" name="word" value="" placeholder="%s"/>
    </form>
    """ % (_("search word"))

    ctx = {
        "title": "%s" % function,
        "form": form,
        "statements": stmts,
        "number_of_statements": number_of_statements,
        "number_of_statement_blocks": stmt_group_number,
        "first_date": first_date,
        "last_date": last_date,
        "number_of_active_dates": number_of_active_dates,
        "search_word": search_word,
        "l_l_speaker_l_stmt_blocks": l_l_speaker_l_stmt_blocks,
        "l_speakers": l_speakers,
    }
    if search_word:
        if not stmts:
            return render(request, "basics/function_filtered_word_not_found.html", ctx)
        return render(request, "basics/function_filtered.html", ctx)
    return render(request, "basics/function.html", ctx)

