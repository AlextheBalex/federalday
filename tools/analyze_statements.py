# -*- coding: utf-8 -*

from __future__ import unicode_literals
import os
import gc
import django
from django.db import transaction
django.setup()

from basics.models import *
from commons import pos_freq_dic


def create_file_of_general_word_freqs():

    l_columns = ['str_adjectives', 'str_nouns', 'str_verbs', 'str_partizip_i', 'str_other_words', 'str_persons', 'str_word_pairs']

    pos_dicts = RegularStatement.objects.values('str_adjectives', 'str_nouns', 'str_verbs', 'str_partizip_i', 'str_other_words', 'str_persons', 'str_word_pairs')

    no_stmts = RegularStatement.objects.all().count() + 0.0

    l_pos_freq_dicts = {}, {}, {}, {}, {}, {}, {}

    no_all_words = 0
    l_no_pos_words = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    for pos_dict in pos_dicts:
        for index, column in enumerate(l_columns):
            l_words = pos_dict[column].split('|')
            for word in l_words:
                if word:
                    l_no_pos_words[index] += 1
                    no_all_words += 1
                    if word in l_pos_freq_dicts[index]:
                        l_pos_freq_dicts[index][word] += 1
                    else:
                        l_pos_freq_dicts[index][word] = 1

    # print l_no_pos_words
    path = os.getcwd() + '/data'

    for index, pos_freq_dict in enumerate(l_pos_freq_dicts):
        l_freq_word = sorted([(v, k) for k, v in pos_freq_dict.iteritems()])[::-1]
        #print l_freq_word
        file_path = path + '/' + l_columns[index] + '.txt'
        no_pos_words = l_no_pos_words[index]
        with open(file_path, 'w') as f:
            for abs_freq, word in l_freq_word:
                relative_freq = (abs_freq/no_stmts) * 100
                line = '|'.join([word, str(relative_freq)])
                f.write(line.encode('utf8'))
                f.write('\n')

# print create_file_of_general_word_freqs()


def create_file_of_speaker_function_party_stmts_counts():
    path = os.getcwd() + '/data/'

    parties = [party for party in Party.objects.all() if party.abbrev]

    speakers = [speaker for speaker in Speaker.objects.all()]

    d_party_counts = {}
    for party in parties:
        d_party_counts[party.abbrev] = RegularStatement.objects.filter(speaker__party=party).count()

    file_path = path + 'party_stmt_count' + '.txt'
    with open(file_path, 'w') as f:
        for party, count in d_party_counts.iteritems():
            line = '|'.join([party, str(count)])
            f.write(line.encode('utf8'))
            f.write('\n')

    d_speaker_counts = {}
    for speaker in speakers:
        d_speaker_counts[unicode(speaker)] = RegularStatement.objects.filter(speaker=speaker).count()

    file_path = path + 'speaker_stmt_count' + '.txt'
    with open(file_path, 'w') as f:
        for speaker, count in d_speaker_counts.iteritems():
            line = '|'.join([speaker, str(count)])
            f.write(line.encode('utf8'))
            f.write('\n')

# create_file_of_speaker_function_party_stmts_counts()


def get_l_significant_words(stmts, d_gen_pos_freq):
    l_part_of_speech_order = ['Substantive', 'Adjektive', 'Verben', 'Partizip I', 'Andere', 'Wort Paare']

    l_d_gen_pos_freq = []
    for pos in ['str_nouns', 'str_adjectives', 'str_verbs', 'str_partizip_i', 'str_other_words', 'str_word_pairs']:
        l_d_gen_pos_freq.append(d_gen_pos_freq[pos])
    d_part_of_speech_freqs = {'Substantive': {}, 'Adjektive': {}, 'Verben': {}, 'Partizip I': {}, 'Andere': {}, 'Wort Paare' : {}}

    l_pos_no_words = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    no_stmts = float(stmts.count())

    for stmt in stmts:
        l_nouns, l_adjectives, l_verbs, l_other_words, l_word_pairs = stmt.str_nouns.split('|'), stmt.str_adjectives.split(
            '|'), stmt.str_verbs.split('|'), stmt.str_other_words.split('|'), stmt.str_word_pairs.split('|')
        if stmt.str_partizip_i:
            l_partizip_i = stmt.str_partizip_i.split('|')
        else:
            l_partizip_i = []
        d_l_words = {'Substantive': l_nouns, 'Adjektive': l_adjectives, 'Verben': l_verbs, 'Partizip I': l_partizip_i,
                     'Andere': l_other_words, 'Wort Paare': l_word_pairs}

        for index, part_of_speech in enumerate(l_part_of_speech_order):

            l_words = d_l_words[part_of_speech]
            for word in l_words:
                l_pos_no_words[index] += 1
                if word in d_part_of_speech_freqs[part_of_speech]:
                    d_part_of_speech_freqs[part_of_speech][word] += 1
                else:
                    d_part_of_speech_freqs[part_of_speech][word] = 1

    l_significant_words = []
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

        for index_2, (rel_freq, abs_freq, word) in enumerate(l_part_of_speech_freq):
            gen_word_pos_freq = d_gen_pos_freq[word]

            if counter > 99:
                break

            if rel_freq > 2 * gen_word_pos_freq:
                counter += 1
                if abs_freq > 10:
                    # if rel_freq > 4 * gen_word_pos_freq:
                        # word = ''.join(['<strong>', word, '</strong>'])

                    l_significant_words.append((word))

        # print l_part_of_speech_freq

    return l_significant_words

def create_l_word_maps():
    l_part_of_speechs = ['str_nouns', 'str_adjectives', 'str_verbs', 'str_partizip_i', 'str_other_words', 'str_word_pairs']
    d_word_l_stmt_ids = {}

    for leg_period in xrange(12, 19):
        stmts = RegularStatement.objects.filter(**{'document__legislative_period': leg_period})
        print leg_period
        for stmt in stmts:
            stmt_id = getattr(stmt, 'pk')
            str_all_words = '|'.join([getattr(stmt, part_of_speech) for part_of_speech in l_part_of_speechs])
            l_all_words = str_all_words.split('|')
            for word in l_all_words:
                try:
                    d_word_l_stmt_ids[word].append(stmt_id)
                except KeyError:
                    d_word_l_stmt_ids[word] = [stmt_id]

    WordMap.objects.all().delete()
    print 'deleted word_maps_object'
    l_word_maps = []
    print 'created d_word_l_stmt_ids'
    for word, l_ids in d_word_l_stmt_ids.iteritems():
        str_pks = '|'.join([str(i) for i in l_ids])
        no_words_stmts = len(l_ids)
        l_word_maps.append(
            WordMap(
                word=word,
                str_stmt_pks=str_pks,
                no_stmts=no_words_stmts)
        )
    print 'created l_word_maps'
    return l_word_maps


def map_words_to_texts():

    l_word_maps = create_l_word_maps()

    start_index = 0
    while True:

        temp_l_word_maps = l_word_maps[start_index : start_index + 1000]
        start_index += 1000
        if not temp_l_word_maps:
            break
        print start_index

        WordMap.objects.bulk_create(temp_l_word_maps)

        #WordMap.objects.get_or_create(
        #    word=word,
        #    str_stmt_pks=str_pks,
        #    no_stmts=no_words_stmts
        #)

#map_words_to_texts()




