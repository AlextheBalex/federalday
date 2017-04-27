# -*- coding: utf-8 -*

from __future__ import unicode_literals
import os
import django

django.setup()

from basics.models import *


def create_file_of_general_word_freqs():

    l_columns = ['str_adjectives', 'str_nouns', 'str_verbs', 'str_partizip_i', 'str_other_words']

    pos_dicts = RegularStatement.objects.values('str_adjectives', 'str_nouns', 'str_verbs', 'str_partizip_i', 'str_other_words')

    no_stmts = RegularStatement.objects.all().count() + 0.0

    l_pos_freq_dicts = {}, {}, {}, {}, {}

    no_all_words = 0
    l_no_pos_words = [0.0, 0.0, 0.0, 0.0, 0.0]

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

    print l_no_pos_words
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






