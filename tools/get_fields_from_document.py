# -*- coding: utf-8 -*

import sys
import os
from os import listdir


txt_directory = os.path.dirname(os.path.realpath(sys.argv[0])).replace('federalday/tools', 'app/txts/plenarprotokolle')

#print txt_directory


def get_document_fields(document_path):

    d_doc = {}

    import codecs
    with codecs.open(document_path, 'r', encoding="utf-8") as the_file:

        l_lines = the_file.readlines()
        l_lines = [line.strip() for line in l_lines if line and line != u'\n']

    file_name = document_path.split('/')[-1]

    d_doc['date'] = l_lines[0]
    d_doc['legislative_period'] = file_name[:2]
    d_doc['document_id'] = int(file_name.split('.')[0])

    for order_id, line in enumerate(l_lines[1:]):
        d_doc[order_id] = {}

        raw_speaker = line.split('|')[1].replace('speaker', '')
        d_doc[order_id]['speaker'] = raw_speaker.split('(')[0].split(',')[0]
        try:
            if raw_speaker.count('(') == 2:
                d_doc[order_id]['party'] = raw_speaker.split('(')[2].replace(')', '')
            else:
                d_doc[order_id]['party'] = raw_speaker.split('(')[1].replace(')', '')
        except IndexError:
            d_doc[order_id]['party'] = ''
        try:
            d_doc[order_id]['function'] = raw_speaker.split(',')[1]
        except IndexError:
            d_doc[order_id]['function'] = ''
            first_word = raw_speaker.split()[0]
            if 'räsident' in first_word:
                d_doc[order_id]['function'] = first_word
            else:
                d_doc[order_id]['function'] = ''

        text = line.split('|')[-1]
        d_doc[order_id]['text'] = text
        d_doc[order_id]['str_adjectives'], d_doc[order_id]['str_nouns'], d_doc[order_id]['str_verbs'], d_doc[order_id]['str_partizip_i'], d_doc[order_id]['str_other_words'], d_doc[order_id]['str_persons'], d_doc[order_id]['str_titles'] = create_part_of_speech_strings_with_persons_and_wiki_titles(text, d_nouns, d_verbs, d_adjectives, d_partizip_i, d_first_names, d_last_names, set_no_first_first_names, d_wiki_titles)
    return d_doc


def get_file_paths_legislative_period(legislative_period):

    legislative_period_dir = '/'.join([txt_directory, legislative_period])

    l_txt_paths = sorted(['/'.join([legislative_period_dir, f]) for f in listdir(legislative_period_dir)])

    return l_txt_paths

