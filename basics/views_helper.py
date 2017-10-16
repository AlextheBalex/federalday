# -*- coding: utf-8 -*

from __future__ import unicode_literals
import datetime
from models import *
from tools.commons import pos_freq_dic


def filter_l_pos_freq(d_gen_pos_freq, l_part_of_speech_freq, new_search_field_number, active_url):
    l_filtered_pos_freq = []
    counter = 0
    for index_2, (rel_freq, abs_freq, word) in enumerate(l_part_of_speech_freq):
        gen_word_pos_freq = d_gen_pos_freq[word]

        if counter > 99:
            break

        if rel_freq > 2 * gen_word_pos_freq:
            counter += 1
            # print counter
            if new_search_field_number == '0':
                further_search_link = active_url + '?word' + new_search_field_number + '=' + word
            else:
                further_search_link = active_url + '&word' + new_search_field_number + '=' + word
            if rel_freq > 4 * gen_word_pos_freq:
                word = ''.join(['<strong>', word, '</strong>'])

            l_filtered_pos_freq.append((rel_freq, abs_freq, word, further_search_link))
    return l_filtered_pos_freq


def get_significant_year_words(l_l_part_of_speech_freqs, d_pos_year_l_pos_freq, d_pos_year_d_word_freq, oldest_year, newest_year):

    d_pos_word_yearly_freqs = {}
    for pos, l_part_of_speech_freqs in l_l_part_of_speech_freqs:
        d_pos_word_yearly_freqs[pos] = {}
        #print 77, l_part_of_speech_freqs
        for a, b, word, c in l_part_of_speech_freqs:
            word = word.replace('<strong>', '').replace('</strong>', '')
            d_pos_word_yearly_freqs[pos][word] = []
            for year in xrange(oldest_year, newest_year + 1):
                try:
                    words_years_rel_freq = d_pos_year_d_word_freq[pos][year][word]
                except KeyError:
                    words_years_rel_freq = 0
                d_pos_word_yearly_freqs[pos][word].append(words_years_rel_freq)

    d_pos_words_avg_yearly_freq = {}
    no_years = newest_year - oldest_year + 1
    for pos in d_pos_word_yearly_freqs:
        d_pos_words_avg_yearly_freq[pos] = {}
        for word, l_freqs in d_pos_word_yearly_freqs[pos].iteritems():
            d_pos_words_avg_yearly_freq[pos][word] = sum(l_freqs) / no_years



            #d_pos_word_yearly_freqs
        #for year, d_pos_freq in d_pos_year_d_word_freq[pos].iteritems():
            #print pos, year, d_pos_freq

    d_year_l_freqs_words = {}
    for year in xrange(oldest_year, newest_year + 1):
        d_year_l_freqs_words[year] = []

    for pos in d_pos_year_l_pos_freq:
        #print d_pos_year_l_pos_freq[pos], 9

        for year, l_year_pos_freq in d_pos_year_l_pos_freq[pos].iteritems():

            for year_rel_freq, word, abs_freq in l_year_pos_freq:
                # if abs_freq > 10 and  word in d_gen_pos_word_rel_freq[pos]:

                #if year == 2015 and word in d_gen_pos_word_rel_freq[pos]:

                    #print word, year_rel_freq, d_gen_pos_word_rel_freq[pos][word], 9999

                if word in d_pos_words_avg_yearly_freq[pos]:
                    gen_rel_freq = d_pos_words_avg_yearly_freq[pos][word]
                    if year_rel_freq > 2 * gen_rel_freq and abs_freq > 5:
                        if year_rel_freq > 4 * gen_rel_freq:
                            word = ''.join(['<strong>', word, '</strong>'])

                    # print word, year_rel_freq, d_gen_pos_word_rel_freq[pos][word], 9999
                        d_year_l_freqs_words[year].append(': '.join([unicode(year_rel_freq), word]))
    l_year_str_l_freqs_words = []
    for year, l_freqs_words in d_year_l_freqs_words.iteritems():
        l_year_str_l_freqs_words.append((year, ' | '.join(l_freqs_words)))

    l_year_str_l_freqs_words = sorted(l_year_str_l_freqs_words)

    return l_year_str_l_freqs_words


def get_l_l_part_of_speech_freqs(stmts, request):
    l_part_of_speech_order = ['Substantive', 'Adjektive', 'Verben', 'Partizip I', 'Andere', 'Wortpaare']

    l_d_gen_pos_freq = []
    for pos in ['str_nouns', 'str_adjectives', 'str_verbs', 'str_partizip_i', 'str_other_words', 'str_word_pairs']:
        l_d_gen_pos_freq.append(pos_freq_dic(pos))

    oldest_year = Document.objects.raw('SELECT id, date FROM basics_document LIMIT 1')[0].date.year
    newest_year = Document.objects.raw('SELECT id, date FROM basics_document ORDER BY date DESC LIMIT 1')[0].date.year
    d_part_of_speech_freqs = {'Substantive': {}, 'Adjektive': {}, 'Verben': {}, 'Partizip I': {}, 'Andere': {}, 'Wortpaare': {}}

    d_year_part_of_speech_freqs = {}
    for year in xrange(oldest_year, newest_year + 1):
        d_year_part_of_speech_freqs[year] = {'Substantive': {}, 'Adjektive': {}, 'Verben': {}, 'Partizip I': {}, 'Andere': {}, 'Wortpaare': {}}

    l_pos_no_words = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    no_stmts = float(stmts.count())
    d_year_no_stmts = {}
    for year in range(oldest_year, newest_year +1):
        d_year_no_stmts[year] = 0.0

    #print stmts.count(), 9999
    for stmt in stmts:

        l_nouns, l_adjectives, l_verbs, l_other_words, l_word_pairs, year = stmt.str_nouns.split('|'), stmt.str_adjectives.split(
            '|'), stmt.str_verbs.split('|'), stmt.str_other_words.split('|'), stmt.str_word_pairs.split('|'), stmt.document.date.year

        d_year_no_stmts[year] += 1

        if stmt.str_partizip_i:
            l_partizip_i = stmt.str_partizip_i.split('|')
        else:
            l_partizip_i = []
        d_l_words = {'Substantive': l_nouns, 'Adjektive': l_adjectives, 'Verben': l_verbs, 'Partizip I': l_partizip_i,
                     'Andere': l_other_words, 'Wortpaare': l_word_pairs}

        for index, part_of_speech in enumerate(l_part_of_speech_order):

            l_words = d_l_words[part_of_speech]
            for word in l_words:
                l_pos_no_words[index] += 1
                if word in d_part_of_speech_freqs[part_of_speech]:
                    d_part_of_speech_freqs[part_of_speech][word] += 1
                else:
                    d_part_of_speech_freqs[part_of_speech][word] = 1

                if word in d_year_part_of_speech_freqs[year][part_of_speech]:
                    d_year_part_of_speech_freqs[year][part_of_speech][word] += 1
                else:
                    d_year_part_of_speech_freqs[year][part_of_speech][word] = 1

    l_l_part_of_speech_freqs = []

    d_pos_year_l_pos_freq = {}
    d_pos_year_d_word_freq = {}
    d_gen_pos_word_rel_freq = {}

    # print d_year_no_stmts, 775

    for index, part_of_speech in enumerate(l_part_of_speech_order):
        # pos_no_words = l_pos_no_words[index]
        d_pos_year_l_pos_freq[part_of_speech] = {}
        d_pos_year_d_word_freq[part_of_speech] = {}

        d_gen_pos_freq = l_d_gen_pos_freq[index]
        #print d_gen_pos_freq
        # print(d_part_of_speech_freqs[part_of_speech])
        for year in d_year_part_of_speech_freqs:
            no_year_stmts = d_year_no_stmts[year]
            l = sorted(
                [(v, k) for k, v in d_year_part_of_speech_freqs[year][part_of_speech].iteritems()])[::-1]
            # print [(round((v/no_year_stmts)*100, 1), k, v, no_year_stmts) for v, k in l if k]

            d_pos_year_l_pos_freq[part_of_speech][year] = [(round((v/no_year_stmts)*100, 1), k, v) for v, k in l if k]

            d_pos_year_d_word_freq[part_of_speech][year] = {word: rel_freq for rel_freq, word, abs_freq in d_pos_year_l_pos_freq[part_of_speech][year]}
            #print d_pos_year_d_word_freq[part_of_speech][year]
        l_part_of_speech_freq = sorted(
            [(v, k) for k, v in d_part_of_speech_freqs[part_of_speech].iteritems()])[::-1]

        # print l_part_of_speech_freq
        l_part_of_speech_freq = [(round(v/no_stmts*100, 1), v, k) for v, k in l_part_of_speech_freq if k]
        # print l_part_of_speech_freq

        active_url = request.get_full_path()
        while active_url.endswith('=') and not active_url.endswith('?word0='):
            active_url = active_url[: -7]

        # print active_url
        if active_url.endswith('/'):
            new_search_field_number = 0
        elif not active_url.endswith('0'):
            new_search_field_number = int(active_url.split('word')[-1].split('=')[0]) + 1
        else:
            new_search_field_number = 0
        new_search_field_number = str(new_search_field_number)

        l_filtered_pos_freq = filter_l_pos_freq(d_gen_pos_freq, l_part_of_speech_freq, new_search_field_number, active_url)

        #for rel_freq, abs_freq, word, f in l_filtered_pos_freq:
            #l_year_words_rel_freqs = []
            #for year in xrange(oldest_year, newest_year +1):
                #try:


        d_gen_pos_word_rel_freq[part_of_speech] = {word: (rel_freq, abs_freq + 0.0) for (rel_freq, abs_freq, word, f) in l_filtered_pos_freq}
        # print l_part_of_speech_freq
        l_l_part_of_speech_freqs.append((part_of_speech, l_filtered_pos_freq))

    '''d_pos_l_years_rel_freq = {pos: {} for pos in l_part_of_speech_order}

    for year in xrange(oldest_year, newest_year):
        for pos in l_part_of_speech_order:
            for word in d_year_part_of_speech_freqs[year][part_of_speech] and word in d_gen_pos_word_rel_freq[pos]:'''


    l_year_str_l_freqs_words = get_significant_year_words(l_l_part_of_speech_freqs, d_pos_year_l_pos_freq, d_pos_year_d_word_freq, oldest_year, newest_year)

    l_count_date_url, l_dates, l_counts, l_counts_sorted_by_year = get_date_counts_from_stmts(stmts, request)

    return l_l_part_of_speech_freqs, l_year_str_l_freqs_words, l_count_date_url, l_dates, l_counts, l_counts_sorted_by_year


def color_search_words(stmts, all_search_terms):
    for index, term in enumerate(all_search_terms):
        term_lower = term.lower()
        replacement = ''.join(['<span class="color', str(index), '">', term, '</span>'])
        replacement_lower = ''.join(['<span class="color', str(index), '">', term_lower, '</span>'])
        for stmt in stmts:
            stmt.text = stmt.text.replace(term, replacement).replace(term_lower, replacement_lower)
    return stmts


def get_match_words_counts(stmts, all_search_terms, no_stmts):
    d_words_counts = {}
    print 989898, all_search_terms
    print stmts.count(), 99, no_stmts
    for stmt in stmts:
        l_words = []
        for words in [stmt.str_nouns, stmt.str_adjectives, stmt.str_verbs, stmt.str_other_words, stmt.str_partizip_i]:
            l_words_temp = words.split('|')
            for i in l_words_temp:
                l_words.append(i)

        for search_term in all_search_terms:
            for word in l_words:
                if search_term in word:

                    if word in d_words_counts:
                        d_words_counts[word] += 1
                    else:
                        d_words_counts[word] = 1
    print 76876, d_words_counts
    l_count_rel_count_word = sorted([(count, round(float(count)/no_stmts * 100, 2), word) for word, count in d_words_counts.iteritems() if len(word) < 30])[::-1]
    print 9797, l_count_rel_count_word
    return l_count_rel_count_word


def filter_statements(search_fields, filters):
    if search_fields:
        #print(filters, 1000)

        stmts = RegularStatement.objects.filter(**filters)
        #stmts = stmts.exclude(**{'speaker__function__name': u'Präsident/in'})
        #stmts = stmts.exclude(**{'speaker__function__name': u'Vizepräsident/in'})
        #print filters, 999999999999999999999

        if u'document__date__year' in filters:
            year_analysis = True
        else:
            year_analysis = False
        if u'speaker' in filters:
            speaker_analysis = True
        else:
            speaker_analysis = False
        no_stmts = stmts.count()
        filters = {}
        all_search_terms = []
        l_set_text_ids = []
        l_counts_match_words = []
        #print search_fields, 99999999999
        for term in search_fields:

            l_or_words = term.split(',')
            set_text_ids = set([])
            for word in l_or_words:
                all_search_terms.append(word)

                if ' ' in word:
                    first_word = word.split()[0]
                    try:
                        str_stmts_pks = WordMap.objects.filter(**{'word__contains': first_word})[0].str_stmt_pks
                    except IndexError:
                        continue
                    l_pks = str_stmts_pks.split('|')
                    l_pks = [pk for pk in l_pks if word in RegularStatement.objects.filter(**{'pk': pk})[0].text]
                    l_word_str_text_ids_no_texts = [(word, '|'.join(l_pks), len(l_pks))]
                else:
                    filters["word__contains"] = word
                    l_word_str_text_ids_no_texts = [(s.word, s.str_stmt_pks, s.no_stmts) for s in WordMap.objects.filter(**filters)]
                for word, str_text_ids, no_texts in l_word_str_text_ids_no_texts:
                    #print word, no_texts
                    l_counts_match_words.append((no_texts, word))
                    l_text_ids = str_text_ids.split('|')
                    #print word, len(l_text_ids), l_text_ids
                    #print len(set(l_text_ids))
                    set_text_ids.update([int(s) for s in l_text_ids if s])
            #print len(set_text_ids), 7777
            l_set_text_ids.append(set_text_ids)
        if len(l_set_text_ids) > 1 or l_set_text_ids[0]:
            #print 777777777777777777777
            #print l_set_text_ids
            smallest_set_text_ids = False
            len_smallest_set_text_ids = 'a'

            for set_text_ids in l_set_text_ids:
                len_set_text_ids = len(set_text_ids)
                if len_set_text_ids < len_smallest_set_text_ids:
                    len_smallest_set_text_ids = len_set_text_ids
                    smallest_set_text_ids = set_text_ids

            l_set_text_ids.remove(smallest_set_text_ids)
            smallest_l_text_ids = list(smallest_set_text_ids)
            #print len_smallest_set_text_ids, 999
            for the_id in smallest_set_text_ids:
                for set_text_ids in l_set_text_ids:
                    if the_id not in set_text_ids:
                        smallest_l_text_ids.remove(the_id)
                        #print 99
                        break
            stmts = stmts.filter(pk__in=smallest_l_text_ids)
        else:
            #print 888888888888888888888
            or_set = None
            commas = term.split(',')
            for w in commas:
                all_search_terms.append(w)
                for to_remove in ("word", ):
                    for query_extension in ("contains", "icontains", ):
                        to_remove_ext = "%s__%s" % (to_remove, query_extension)
                        if to_remove_ext in filters:
                            filters.pop(to_remove_ext)
                filters["cleaned_text__contains"] = w
                qset = stmts.filter(**filters)
                or_set = (or_set | qset) if or_set is not None else qset
            stmts = or_set
        #pk_filter = {}

        print 'filtered by pk'
        stmts = stmts.order_by("document__date", "order_id")
        no_stmts_filtered = stmts.count()

        if not year_analysis and not speaker_analysis and len(search_fields) < 2:
            l_counts_rel_counts_words = sorted([(no_texts, round(float(no_texts) / no_stmts_filtered * 100, 2), word) for (no_texts, word) in l_counts_match_words if len(word) < 30])[::-1]
        else:
            l_counts_rel_counts_words = get_match_words_counts(stmts, all_search_terms, no_stmts_filtered)

        # print(l_counts_rel_counts_words)
    else:
        stmts = RegularStatement.objects.filter(**filters)
        no_stmts = stmts.count()
        no_stmts_filtered = ''
        l_counts_rel_counts_words = []

    return stmts, no_stmts, no_stmts_filtered, l_counts_rel_counts_words


def filter_statements_cached(search_fields, filters, request, all_search_terms):
    # print(filters, 888)
    cache_filters = {}
    # print(filters, 2)
    for key, value in filters.iteritems():
        cache_filters[key] = unicode(value)
    key = "filter_statements_%s" % [search_fields, cache_filters]
    # print(key, 3)
    # print(type(key), 3)

    # print(type(key), 1)
    res = PickleCache.restore(key=key)
    res = None#######################################################
    if res is None:
        # print(filters, 999)
        stmts, no_stmts, no_stmts_filtered, l_counts_rel_counts_words = filter_statements(search_fields, filters)
        l_l_part_of_speech_freqs, l_year_str_l_freqs_words, l_count_date_url, l_dates, l_counts, l_counts_sorted_by_year = get_l_l_part_of_speech_freqs(stmts, request)
        stmts = color_search_words(stmts, all_search_terms)
        obj = {
            "no_stmts": no_stmts,
            "no_stmts_filtered": no_stmts_filtered,
            "stmts": stmts,
            "l_counts_rel_counts_words": l_counts_rel_counts_words,
            "l_l_part_of_speech_freqs": l_l_part_of_speech_freqs,
            "l_year_str_l_freqs_words": l_year_str_l_freqs_words,
            "l_count_date_url": l_count_date_url,
            "l_dates": l_dates,
            "l_counts": l_counts,
            "l_counts_sorted_by_year": l_counts_sorted_by_year

        }
        PickleCache.store(key, obj)
        print("CACHE STORED")
        return stmts, no_stmts, no_stmts_filtered, l_counts_rel_counts_words, \
               l_l_part_of_speech_freqs, l_year_str_l_freqs_words, l_count_date_url, l_dates, l_counts, l_counts_sorted_by_year
    else:
        print("CACHE RESTORED")
        return res["stmts"], res["no_stmts"], res["no_stmts_filtered"], res["l_counts_rel_counts_words"],\
               res["l_l_part_of_speech_freqs"], res["l_year_str_l_freqs_words"], res["l_count_date_url"], res["l_dates"], res["l_counts"], res["l_counts_sorted_by_year"]


def order_stmts_by_speaker_stmt_blocks(stmts, all_search_terms):
    l_speakers0 = [s.speaker for s in stmts]
    l_speakers = []

    for speaker in l_speakers0:
        if speaker not in l_speakers:
            # print(speaker.significant_words)
            l_speakers.append(speaker)

    l_speakers_block_nos_stmts = []
    no_stmt_blocks = 0
    for speaker in l_speakers:

        l_block_nos_stmts = []
        stmts_speaker = stmts.filter(speaker=speaker)
        l_stmts_block_nos0 = [s.stmt_block_no for s in stmts_speaker]
        l_stmts_block_nos = []

        for stmt_block_no in l_stmts_block_nos0:
            if stmt_block_no not in l_stmts_block_nos:
                l_stmts_block_nos.append(stmt_block_no)

        no_stmt_blocks += len(l_stmts_block_nos)

        for stmt_block_no in l_stmts_block_nos:
            stmts_block_no = stmts_speaker.filter(stmt_block_no=stmt_block_no)

            stmts_block_no = color_search_words(stmts_block_no, all_search_terms)
            l_block_nos_stmts.append(stmts_block_no)

        l_speakers_block_nos_stmts.append([speaker, l_block_nos_stmts])

    return l_speakers_block_nos_stmts, l_speakers, no_stmt_blocks



def count_speaker_party_from_statements(stmts, request):
    time = datetime.datetime.now()
    print("COUNT %s" % (datetime.datetime.now() - time))
    # number_of_statements = stmts.count()
    first_date = stmts[0].document.date
    last_date = stmts.reverse()[0].document.date
    #print(stmts.count())
    speaker_ids = [i[0] for i in stmts.values_list("speaker")]
    # print(speaker_ids)
    speaker_no_statements = {}

    print("%s COUNT speakers" % (datetime.datetime.now() - time))
    for i in speaker_ids:
        speaker = Speaker.objects.get(pk=i)

        if speaker in speaker_no_statements:
            speaker_no_statements[speaker] += 1
        else:
            speaker_no_statements[speaker] = 1

    print("%s COUNT parties" % (datetime.datetime.now() - time))
    party_no_statements = {}
    for speaker in speaker_no_statements:
        party = speaker.party.abbrev
        if party in party_no_statements:
            party_no_statements[party] += speaker_no_statements[speaker]
        else:
            party_no_statements[party] = speaker_no_statements[speaker]

    url_search_words_add = request.get_full_path().split('/')[-1]

    print("%s COUNT pos_freq" % (datetime.datetime.now() - time))
    d_speaker_counts = pos_freq_dic('speaker_stmt_count')
    # print d_speaker_counts

    print("%s COUNT sort" % (datetime.datetime.now() - time))
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

    print("%s COUNT sort party" % (datetime.datetime.now() - time))
    d_party_counts = pos_freq_dic('party_stmt_count')

    l_party_no_statements = sorted([(no_stmts, party, round(no_stmts / d_party_counts[party] * 100, 2)) for party, no_stmts in party_no_statements.iteritems() if party], key=lambda x: x[2])[::-1]


    return l_stmts_no_speaker, l_party_no_statements, first_date, last_date


def count_speaker_party_from_statements_cached(cachekey, stmts, request):
    obj = PickleCache.restore(cachekey)
    if obj is not None:
        return obj
    else:
        l_speaker, l_party, first_date, last_date = count_speaker_party_from_statements(stmts, request)
        PickleCache.store(cachekey, (l_speaker, l_party, first_date, last_date))

        return l_speaker, l_party, first_date, last_date


def get_date_counts_from_stmts(stmts, request):
    d_date_count = {}
    d_year_count = {}
    oldest_year = Document.objects.raw('SELECT id, date FROM basics_document LIMIT 1')[0].date.year
    newest_year = Document.objects.raw('SELECT id, date FROM basics_document ORDER BY date DESC LIMIT 1')[0].date.year
    for year in xrange(oldest_year, newest_year + 1):
        d_year_count[year] = 0

    for stmt in stmts:
        date = stmt.document.date
        year = date.year
        # print(date)

        d_year_count[year] += 1

        if date in d_date_count:
            d_date_count[date] += 1
        else:
            d_date_count[date] = 1

    current_url = request.get_full_path()


    if 'year' in current_url:
        l_count_date_url = sorted([(count, date, '') for date, count in d_date_count.iteritems()])[::-1]
        l_dates = [i[1] for i in l_count_date_url]
        l_counts = [i[0] for i in l_count_date_url]

        return l_count_date_url, l_dates, l_counts, []
    else:
        l_count_year_url = sorted(
            [(count, year, current_url + '&year=%i' % year) for year, count in d_year_count.iteritems()])[::-1]
        l_years = [i[1] for i in l_count_year_url]
        l_counts = [i[0] for i in l_count_year_url]

        l_counts_sorted_by_year = sorted([(year, d_year_count[year]) for year in l_years])
        l_counts_sorted_by_year = [i[1] for i in l_counts_sorted_by_year]
        return l_count_year_url, l_years, l_counts, l_counts_sorted_by_year


def get_l_speaker_distances(speaker):

    l_target_significant_words = speaker.significant_words.split('|')
    no_significant_words = len(l_target_significant_words)

    l_other_speakers = [other_speaker for other_speaker in Speaker.objects.all() if other_speaker != speaker]
    d_speaker_shared_words = {}

    for other_speaker in l_other_speakers:

        l_significant_words = other_speaker.significant_words.split('|')

        for word in l_target_significant_words:
            if word in l_significant_words:
                if other_speaker in d_speaker_shared_words:
                    d_speaker_shared_words[other_speaker] += 1
                else:
                    d_speaker_shared_words[other_speaker] = 1.0

    l_no_shared_words_speaker = sorted([(no_shared_words, speaker) for speaker, no_shared_words in d_speaker_shared_words.iteritems()])[::-1]

    l_no_shared_words_speaker = l_no_shared_words_speaker[:100]

    d_party_party_share_index = {}
    for no_shared_words, speaker in l_no_shared_words_speaker:
        party = speaker.party
        if not party.abbrev:
            continue
        if party in d_party_party_share_index:
            d_party_party_share_index[party] += no_shared_words/no_significant_words
        else:
            d_party_party_share_index[party] = no_shared_words/no_significant_words

    l_normalized_shares_parties = []
    sum_party_share_index = 0.0
    for party, party_share_index in d_party_party_share_index.iteritems():
        sum_party_share_index += party_share_index

    for party, party_share_index in d_party_party_share_index.iteritems():
        normalized_share = party_share_index/sum_party_share_index * 100
        l_normalized_shares_parties.append((normalized_share, party))

    l_normalized_shares_parties = sorted(l_normalized_shares_parties)[::-1]

    return l_no_shared_words_speaker, l_normalized_shares_parties

