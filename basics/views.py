# -*- coding: utf-8 -*

from __future__ import unicode_literals

import datetime

from django.http import HttpResponse
from django.shortcuts import render, Http404
from django.utils.translation import ugettext_lazy as _

from models import *

from tools import bokehplot
from views_helper import (get_l_l_part_of_speech_freqs, color_search_words,
                          filter_statements, filter_statements_cached,
                          order_stmts_by_speaker_stmt_blocks, pos_freq_dic,
                          count_speaker_party_from_statements_cached,
                          get_date_counts_from_stmts, get_l_speaker_distances)
from dal import autocomplete


class SearchAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = PickleCache.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)
        return qs


def doc_index_view(request):
    ctx = {
        "title": _("document index"),
        "documents": Document.objects.all(),
    }

    return render(request, "basics/document_index.html", ctx)


def user_handling_view(request):

    return render(request, "basics/user_handling.html")


def speaker_index_view(request):

    speakers = Speaker.objects.all().order_by("name")
    print 'got speakers'
    l_parl_secretaries = []
    l_federal_ministers = []
    l_parlamentarians = []
    l_else = []

    for speaker in speakers:
        # print speaker.function
        if u'Staatssekretär' in speaker.function.name:
            l_parl_secretaries.append(speaker)
        elif u'Bundesminister' in speaker.function.name:
            l_federal_ministers.append(speaker)
        elif 'Abgeordnet' in speaker.function.name:
            l_parlamentarians.append(speaker)
        else:
            l_else.append(speaker)

    ctx = {
        "title": _("speaker index"),
        "l_parl_secretaries": l_parl_secretaries,
        "l_federal_ministers": l_federal_ministers,
        "l_parlamentarians": l_parlamentarians,
        "l_else": l_else,
    }
    print('rendering')
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

    l_no_shared_words_speaker, l_normalized_shares_parties = get_l_speaker_distances(speaker)
    print(l_no_shared_words_speaker)

    filters = {
        "speaker": speaker,
    }

    all_search_terms = []

    stmts, no_stmts, no_stmts_filtered, l_counts_words, l_l_part_of_speech_freqs, l_year_str_l_freqs_words, l_count_date_url, l_dates, l_counts, l_counts_sorted_by_year = filter_statements_cached(
        search_fields, filters, request, all_search_terms)

    #stmts, no_stmts, no_stmts_filtered, l_counts_words = filter_statements(search_fields, filters)

    #l_l_part_of_speech_freqs, l_year_str_l_freqs_words = get_l_l_part_of_speech_freqs(stmts, request)

    all_search_terms = []
    for field in search_fields:
        for term in field.split(','):
            all_search_terms.append(term)

    stmts = color_search_words(stmts, all_search_terms)

    stmt_group_number = 0
    last_order_id = 0
    last_date = ''
    number_of_active_dates = 0
    d_leg_period_no_stmts = {}
    d_leg_period_active_dates = {}
    if stmts.exists():

        for stmt in stmts:
            date = stmt.document.date
            leg_period = stmt.document.legislative_period
            if leg_period in d_leg_period_no_stmts:
                d_leg_period_no_stmts[leg_period] += 1
            else:
                d_leg_period_no_stmts[leg_period] = 1

            order_id = stmt.order_id
            if last_date == date:

                if order_id - last_order_id == 1:
                    stmt.group_number = stmt_group_number
            else:
                if last_date != date:
                    number_of_active_dates += 1
                if leg_period in d_leg_period_active_dates:
                    d_leg_period_active_dates[leg_period] += 1
                else:
                    d_leg_period_active_dates[leg_period] = 1
                last_date = date
                stmt_group_number += 1
                stmt.group_number = stmt_group_number
            last_order_id = order_id
        number_of_statements = stmts.count()
        first_date = stmts[0].document.date
    else:
        number_of_statements = 0
        first_date = "never"
        l_year_str_l_freqs_words = []

    l_leg_period_active_dates = sorted([[k, v] for k, v in d_leg_period_active_dates.iteritems()])
    l_leg_period_no_stmts = sorted([(k, v, d_leg_period_active_dates[k]) for k, v in d_leg_period_no_stmts.iteritems()])
    l_active_dates = [v for k, v in l_leg_period_active_dates]

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
        "l_leg_period_no_stmts": l_leg_period_no_stmts,
        "l_active_dates": l_active_dates,
        "l_l_part_of_speech_freqs": l_l_part_of_speech_freqs,
        "l_counts_words": l_counts_words,
        "l_no_shared_words_speaker": l_no_shared_words_speaker,
        "l_normalized_shares_parties": l_normalized_shares_parties,
    }
    if search_fields:
        if not stmts:
            return render(request, "basics/speaker_filtered_word_not_found.html", ctx)
        return render(request, "basics/speaker_filtered.html", ctx)
    return render(request, "basics/speaker.html", ctx)


def statements_search_view(request):

    num_search_fields = 1
    search_fields = []
    for i in range(10):
        term = request.GET.get("word%s" % i, None)
        if term:
            num_search_fields = i+2
            search_fields.append(term)
        else:
            break

    filters = {}
    all_search_terms = []
    l_l_part_of_speech_freqs = []
    if search_fields:
        stmts, no_stmts, no_stmts_filtered = filter_statements(search_fields, filters)

        l_l_part_of_speech_freqs = get_l_l_part_of_speech_freqs(stmts, request)

        for field in search_fields:
            for term in field.split(','):
                all_search_terms.append(term)
        stmts = color_search_words(stmts, all_search_terms)
    else:
        stmts = None
        no_stmts_filtered = 0

    if stmts and stmts.exists():

        l_count_date = get_date_counts_from_stmts(stmts)
        print('counted dates')
        # number_of_statements = stmts.count()
        first_date = stmts[0].document.date
        last_date = stmts.reverse()[0].document.date
        speaker_ids = stmts.values_list('speaker')
        # print(speaker_ids)
        speaker_no_statements = {}

        for i in speaker_ids:
            the_id = i[0]
            speaker = Speaker.objects.get(pk=the_id)

            if speaker in speaker_no_statements:
                speaker_no_statements[speaker] += 1
            else:
                speaker_no_statements[speaker] = 1

        party_no_statements = {}
        for speaker in speaker_no_statements:
            party = speaker.party.abbrev
            if party in party_no_statements:
                party_no_statements[party] += speaker_no_statements[speaker]
            else:
                party_no_statements[party] = speaker_no_statements[speaker]

        url_search_words_add = request.get_full_path().split('/')[-1]

        d_speaker_counts = pos_freq_dic('speaker_stmt_count')
        # print d_speaker_counts

        l_stmts_no_speaker = sorted(
            [
                (
                    no_stmts, speaker.name,
                    speaker.link_decorator() + url_search_words_add,
                    speaker.function.name,
                    speaker.function.link_decorator() + url_search_words_add,
                    speaker.party.abbrev,
                    speaker.party.link_decorator() + url_search_words_add,
                    round(no_stmts / d_speaker_counts[unicode(speaker)] * 100, 1)
                ) for speaker, no_stmts in speaker_no_statements.iteritems()
            ], key=lambda x: x[:2])[::-1][:20]
        # print(l_stmts_no_speaker)

        l_party_no_statements = sorted([(no_stmts, party) for party, no_stmts in party_no_statements.iteritems()])[::-1]

    else:
        l_stmts_no_speaker = []
        first_date = "never"
        last_date = 'never'
        l_party_no_statements = []
        l_count_date = []

    form = """<form name="word-search-form" method="GET">"""
    form += """<input type="submit" value="%s"/>""" % _("Suchen")
    for i in range(num_search_fields):
        val = request.GET.get("word%s" % i, "")
        form += """ <input type="text" name="word%s" placeholder="%s" value="%s"/>""" % (
            i, _("search word"), val)
    form += "</form>"

    ctx = {
        "title": "%s" % "Statements Suche",
        "form": form,
        "statements": stmts,
        "number_of_statements": no_stmts_filtered,
        "first_date": first_date,
        "last_date": last_date,
        "l_all_search_terms": all_search_terms,
        "l_stmts_no_speaker": l_stmts_no_speaker,
        "l_party_no_statements": l_party_no_statements,
        "l_l_part_of_speech_freqs": l_l_part_of_speech_freqs,
        "l_count_date": l_count_date,
    }

    return render(request, "basics/statements_search.html", ctx)


def statements_search_view_cached(request):

    num_search_fields = 1
    search_fields = []
    year = request.GET.get("year", None)
    for i in range(10):
        term = request.GET.get("word%s" % i, None)
        if term:
            num_search_fields = i+2
            search_fields.append(term)
        else:
            break

    query_str = request.GET.urlencode()

    time = datetime.datetime.now()
    print("FILTER %s" % (datetime.datetime.now()-time))

    plot = ""
    if year:
        filters = {'document__date__year': int(year)}
        year_analysis = True
    else:
        filters = {}
        year_analysis = False

    all_search_terms = []
    l_l_part_of_speech_freqs = []

    for field in search_fields:
        for term in field.split(','):
            all_search_terms.append(term)

    if search_fields:
        stmts, no_stmts, no_stmts_filtered, l_counts_words, l_l_part_of_speech_freqs, l_year_str_l_freqs_words, l_count_date_url, l_dates, l_counts, l_counts_sorted_by_year = filter_statements_cached(search_fields, filters, request, all_search_terms)
        # print(stmts[0].document.date.year, 9)
        print("FREQ %s" % (datetime.datetime.now() - time))
        #l_l_part_of_speech_freqs, l_year_str_l_freqs_words = get_l_l_part_of_speech_freqs(stmts, request)

        print("COLOR %s" % (datetime.datetime.now() - time))


        print("COUNT DATES, YEARS %s" % (datetime.datetime.now() - time))

        #l_count_date_url, l_dates, l_counts, l_counts_sorted_by_year = get_date_counts_from_stmts(stmts, request)

        l_year_counts_str_l_freqs = []
        print 8, l_counts_sorted_by_year
        print 8, l_year_str_l_freqs_words

        if l_counts_sorted_by_year:
            for index, (year, str_l_freqs) in enumerate(l_year_str_l_freqs_words):
                l_year_counts_str_l_freqs.append((year, l_counts_sorted_by_year[index], str_l_freqs))

        if year_analysis:
            plot = bokehplot.get_plot_markup_xy("Titel", "X", "Y", l_dates, l_counts, x_axis_type="datetime")
        else:
            plot = bokehplot.get_plot_markup_xy("Titel", "X", "Y", l_dates, l_counts)

        # print(plot)
    else:
        stmts = None
        no_stmts_filtered = 0
        l_counts_words = []
        l_count_date_url, l_dates, l_counts = [], [], []

    if stmts:
        cachekey = "count_statements_%s" % [search_fields, filters]
        l_stmts_no_speaker, l_party_no_statements, \
            first_date, last_date = count_speaker_party_from_statements_cached(cachekey, stmts, request)

    else:
        l_stmts_no_speaker = []
        first_date = "never"
        last_date = 'never'
        l_party_no_statements = []
        l_year_counts_str_l_freqs = []

    form = """<form name="word-search-form" method="GET">"""
    form += """<input type="submit" value="%s"/>""" % _("Suchen")
    for i in range(num_search_fields):
        val = request.GET.get("word%s" % i, "")
        form += """ <input type="search" name="word%s" id="search_words" placeholder="%s" value="%s"/>""" % (
            i, _("search word"), val)
    form += "</form>"

    '''from dal import autocomplete
    from django import forms

    class SearchForm(forms.ModelForm):
        class Meta:
            model = PickleCache
            fields = ('__all__')
            widgets = {
                'identifier': autocomplete.ModelSelect2(url='basics/search_autocomplete')
            }'''

    #if stmts:
    #    stmts = stmts[:300]


    ctx = {
        "title": "%s" % "Statements Suche",
        "plot": plot,
        "form": form,
        "query_str": query_str,
        "statements": stmts, # [first_stmt:last_stmt],
        "number_of_statements": no_stmts_filtered,
        "first_date": first_date,
        "last_date": last_date,
        "l_all_search_terms": all_search_terms,
        "l_stmts_no_speaker": l_stmts_no_speaker,
        "l_party_no_statements": l_party_no_statements,
        "l_l_part_of_speech_freqs": l_l_part_of_speech_freqs,
        "l_counts_words": l_counts_words,
        "l_count_date_url": l_count_date_url,
        "l_year_counts_str_l_freqs": l_year_counts_str_l_freqs,
        # "l_count_year_url": l_count_year_url,
    }
    print("RENDER %s" % (datetime.datetime.now() - time))
    res = render(request, "basics/statements_search.html", ctx)
    print("DONE %s" % (datetime.datetime.now()-time))
    return res


def statements_only_search_view_cached(request):

    num_search_fields = 1
    search_fields = []
    year = request.GET.get("year", None)
    for i in range(10):
        term = request.GET.get("word%s" % i, None)
        if term:
            num_search_fields = i+2
            search_fields.append(term)
        else:
            break

    if year:
        filters = {'document__date__year': int(year)}
        year_analysis = True
    else:
        filters = {}
        year_analysis = False

    all_search_terms = []
    l_l_part_of_speech_freqs = []

    for field in search_fields:
        for term in field.split(','):
            all_search_terms.append(term)

    if search_fields:
        stmts, no_stmts, no_stmts_filtered, l_counts_words, l_l_part_of_speech_freqs, l_year_str_l_freqs_words, l_count_date_url, l_dates, l_counts, l_counts_sorted_by_year = filter_statements_cached(search_fields, filters, request, all_search_terms)

    else:
        stmts = None
        no_stmts_filtered = 0

    per_page = 10
    statements_from = int(request.GET.get("page", 0)) * per_page
    statements_to = statements_from + per_page
    if stmts:
        stmts = stmts[statements_from:statements_to]

    ctx = {
        "statements_from": statements_from,
        "statements_to": statements_to,
        "statements": stmts, # [first_stmt:last_stmt],
    }
    res = render(request, "basics/statements_only.html", ctx)
    return res


def function_view(request, id):
    try:
        function = Function.objects.get(pk=id)
    except Function.DoesNotExist:
        raise Http404

    num_search_fields = 1
    search_fields = []
    for i in range(10):
        term = request.GET.get("word%s" % i, None)
        if term:
            #print(term)
            num_search_fields = i + 2
            search_fields.append(term)
        else:
            break

    filters = {
        "speaker__function": function,
    }

    all_search_terms = []
    for field in search_fields:
        for term in field.split(','):
            all_search_terms.append(term)

    stmts, no_stmts, no_stmts_filtered, l_counts_rel_counts_words, \
    l_l_part_of_speech_freqs, l_year_str_l_freqs_words, l_count_date_url, l_dates, l_counts, l_counts_sorted_by_year = filter_statements_cached(search_fields, filters, request, all_search_terms)

    #l_l_part_of_speech_freqs = get_l_l_part_of_speech_freqs(stmts, request)

    last_date = ''
    number_of_active_dates = 0

    l_speakers_block_nos_stmts, l_speakers, no_stmt_blocks = order_stmts_by_speaker_stmt_blocks(stmts, all_search_terms)

    form = """<form name="word-search-form" method="GET">"""
    form += """<input type="submit" value="%s"/>""" % _("Suchen")
    for i in range(num_search_fields):
        val = request.GET.get("word%s" % i, "")
        form += """ <input type="text" name="word%s" placeholder="%s" value="%s"/>""" % (
            i, _("search word"), val)
    form += "</form>"

    ctx = {
        "title": "%s" % function,
        "form": form,
        "l_speakers_block_nos_stmts": l_speakers_block_nos_stmts,
        "no_of_stmts": no_stmts,
        "no_of_stmts_filtered": no_stmts_filtered,
        "number_of_statement_blocks": no_stmt_blocks,
        "last_date": last_date,
        "number_of_active_dates": number_of_active_dates,
        "search_words": search_fields,
        "l_speakers": l_speakers,
        "l_l_part_of_speech_freqs": l_l_part_of_speech_freqs,
    }
    if search_fields:
        if not stmts:
            return render(request, "basics/function_filtered_word_not_found.html", ctx)
        return render(request, "basics/function_filtered.html", ctx)
    return render(request, "basics/function.html", ctx)


def party_view(request, id):
    try:
        party = Party.objects.get(pk=id)
    except Function.DoesNotExist:
        raise Http404

    num_search_fields = 1
    search_fields = []
    for i in range(10):
        term = request.GET.get("word%s" % i, None)
        if term:
            num_search_fields = i + 2
            search_fields.append(term)
        else:
            break

    filters = {
        "speaker__party": party,
    }
    # print(type(filters["speaker__party"]))

    stmts, no_stmts, no_stmts_filtered, l_counts_rel_counts_words, \
    l_l_part_of_speech_freqs, l_year_str_l_freqs_words, l_count_date_url, l_dates, l_counts, l_counts_sorted_by_year = filter_statements_cached(search_fields, filters, request, [])

    l_l_part_of_speech_freqs = get_l_l_part_of_speech_freqs(stmts, request)

    all_search_terms = []
    for field in search_fields:
        for term in field.split(','):
            all_search_terms.append(term)

    last_date = ''
    number_of_active_dates = 0
    if search_fields or stmts.count() < 100:
        l_speakers_block_nos_stmts, l_speakers, no_stmt_blocks = order_stmts_by_speaker_stmt_blocks(stmts,
                                                                                                    all_search_terms)
        print('ordered by speaker')

    else:
        no_stmts = 0
        no_stmts_filtered = 0
        last_date = ''
        number_of_active_dates = 0
        l_speakers_block_nos_stmts = []
        l_speakers = []
        no_stmt_blocks = 0
        l_l_part_of_speech_freqs = []
        l_counts_words = []

    form = """<form name="word-search-form" method="GET">"""
    form += """<input type="submit" value="%s"/>""" % _("Suchen")
    for i in range(num_search_fields):
        val = request.GET.get("word%s" % i, "")
        form += """ <input type="text" name="word%s" placeholder="%s" value="%s"/>""" % (
            i, _("search word"), val)
    form += "</form>"

    ctx = {
        "title": "%s" % party,
        "form": form,
        "no_of_stmts": no_stmts,
        "no_of_stmts_filtered": no_stmts_filtered,
        "first_date": '',
        "last_date": last_date,
        "number_of_active_dates": number_of_active_dates,
        "l_l_part_of_speech_freqs": l_l_part_of_speech_freqs,
        "search_words": search_fields,
        "l_speakers_block_nos_stmts": l_speakers_block_nos_stmts,
        "l_speakers": list(set(l_speakers)),
        "no_stmt_blocks": no_stmt_blocks,
        "l_counts_words": l_counts_rel_counts_words,
    }

    print('sending to templates')
    if search_fields:
        if not stmts:
            return render(request, "basics/function_filtered_word_not_found.html", ctx)
        return render(request, "basics/party_filtered.html", ctx)
    return render(request, "basics/party.html", ctx)


def year_stmt_search(request):

    h = 1


def lazy_content(request):

    return HttpResponse("Voll nachgeladen, Alter!")

'''def zukunft():

    s = StatementSet()
    s.filter(speaker="", party="", words={})
    s.get_statement_list()
    s.get_speaker_list()
    s.get_frequency()'''

