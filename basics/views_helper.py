# -*- coding: utf-8 -*

from __future__ import unicode_literals
import codecs
from models import *
import os


def pos_freq_dic(pos):
    d = {}
    path = os.getcwd() + '/tools/data'
    file_path = path + '/' + pos + '.txt'

    with codecs.open(file_path, 'r', encoding='utf-8') as r:
        l_lines = r.read().split('\n')
        for line in l_lines:
            if line:
                word, rel_freq = line.split('|')
                d[word] = float(rel_freq)

    return d


def get_l_l_part_of_speech_freqs(stmts, request):
    l_part_of_speech_order = ['Substantive', 'Adjektive', 'Verben', 'Partizip I', 'Andere']

    l_d_gen_pos_freq = []
    for pos in ['str_nouns', 'str_adjectives', 'str_verbs', 'str_partizip_i', 'str_other_words']:
        l_d_gen_pos_freq.append(pos_freq_dic(pos))
    d_part_of_speech_freqs = {'Substantive': {}, 'Adjektive': {}, 'Verben': {}, 'Partizip I': {}, 'Andere': {}}

    l_pos_no_words = [0.0, 0.0, 0.0, 0.0, 0.0]

    no_stmts = stmts.count() + 0.0

    for stmt in stmts:
        l_nouns, l_adjectives, l_verbs, l_other_words = stmt.str_nouns.split('|'), stmt.str_adjectives.split(
            '|'), stmt.str_verbs.split('|'), stmt.str_other_words.split('|')
        if stmt.str_partizip_i:
            l_partizip_i = stmt.str_partizip_i.split('|')
        else:
            l_partizip_i = []
        d_l_words = {'Substantive': l_nouns, 'Adjektive': l_adjectives, 'Verben': l_verbs, 'Partizip I': l_partizip_i,
                     'Andere': l_other_words}

        for index, part_of_speech in enumerate(l_part_of_speech_order):

            l_words = d_l_words[part_of_speech]
            for word in l_words:
                l_pos_no_words[index] += 1
                if word in d_part_of_speech_freqs[part_of_speech]:
                    d_part_of_speech_freqs[part_of_speech][word] += 1
                else:
                    d_part_of_speech_freqs[part_of_speech][word] = 1

    l_l_part_of_speech_freqs = []
    for index, part_of_speech in enumerate(l_part_of_speech_order):
        pos_no_words = l_pos_no_words[index]
        d_gen_pos_freq = l_d_gen_pos_freq[index]
        #print d_gen_pos_freq
        # print(d_part_of_speech_freqs[part_of_speech])
        l_part_of_speech_freq = sorted(
            [(v, k) for k, v in d_part_of_speech_freqs[part_of_speech].iteritems()])[::-1]
        # print l_part_of_speech_freq
        l_part_of_speech_freq = [(round(v/no_stmts*100, 1), v, k) for v, k in l_part_of_speech_freq if k]
        # print l_part_of_speech_freq
        # l_part_of_speech_freq = [(round(rel_v, 1), v, k) for rel_v, v, k in l_part_of_speech_freq if rel_v > d_gen_pos_freq[k] *2]

        counter = 0
        l_filtered_pos_freq = []
        active_url = request.get_full_path()
        while active_url.endswith('=') and not active_url.endswith('?word0='):
            active_url = active_url[: -7]

        print active_url
        if active_url.endswith('/'):
            new_search_field_number = 0
        elif not active_url.endswith('0'):
            new_search_field_number = int(active_url.split('word')[-1].split('=')[0]) + 1
        else:
            new_search_field_number = 0
        new_search_field_number = str(new_search_field_number)

        for index, (rel_freq, abs_freq, word) in enumerate(l_part_of_speech_freq):
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

        # print l_part_of_speech_freq
        l_l_part_of_speech_freqs.append((part_of_speech, l_filtered_pos_freq))

    return l_l_part_of_speech_freqs


def color_search_words(stmts, all_search_terms):
    for index, term in enumerate(all_search_terms):
        term_lower = term.lower()
        replacement = ''.join(['<span class="color', str(index), '">', term, '</span>'])
        replacement_lower = ''.join(['<span class="color', str(index), '">', term_lower, '</span>'])
        for stmt in stmts:
            stmt.text = stmt.text.replace(term, replacement).replace(term_lower, replacement_lower)
    return stmts


def filter_statements(search_fields, filters):
    if search_fields:
        stmts = RegularStatement.objects.filter(**filters)
        no_stmts = stmts.count()
        filters = {}
        for term in search_fields:
            or_set = None
            commas = term.split(',')
            for w in commas:
                filters["text__contains"] = w
                qset = stmts.filter(**filters)
                or_set = (or_set | qset) if or_set is not None else qset
            stmts = or_set
        stmts = stmts.order_by("document__date", "order_id")
        no_stmts_filtered = stmts.count()
    else:
        stmts = RegularStatement.objects.filter(**filters)
        no_stmts = stmts.count()
        no_stmts_filtered = ''

    return stmts, no_stmts, no_stmts_filtered


def order_stmts_by_speaker_stmt_blocks(stmts, all_search_terms):
    l_speakers0 = [s.speaker for s in stmts]
    l_speakers = []

    for speaker in l_speakers0:
        if speaker not in l_speakers:
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