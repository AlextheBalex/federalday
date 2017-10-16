# -*- coding: utf-8 -*

import os
import codecs

def clean_text(text):
    clean_text = ''.join([letter for letter in text if letter and letter.isalpha()]).strip()
    clean_text = u' '.join(clean_text.split())
    return clean_text

def clean_text_add_spaces(text):
    clean_text = text.replace(u' ', ' ').replace('|', ' ')
    clean_text = ''.join([letter for letter in clean_text if letter and letter.isalpha() or letter in "'0123456789 -"]).strip()
    clean_text = u' '.join(clean_text.split())
    clean_text = ''.join([' ', clean_text, ' '])
    return clean_text

def l_of_words(text):
    clean_text = text.replace(u' ', ' ').replace('|', ' ')
    clean_text = ''.join([letter for letter in clean_text if letter and letter.isalpha() or letter in "'0123456789 -"]).strip()
    return clean_text.split()


def pos_freq_dic(pos):
    d = {}
    path = os.getcwd()
    # print(path)
    if "tools/data" in path:
        file_path = path + '/' + pos + '.txt'
    elif "tools" in path:
        file_path = path + '/data' + '/' + pos + '.txt'
    else:
        file_path = path + '/tools/data' + '/' + pos + '.txt'

    with codecs.open(file_path, 'r', encoding='utf-8') as r:
        l_lines = r.read().split('\n')
        for line in l_lines:
            if line:
                word, rel_freq = line.split('|')
                d[word] = float(rel_freq)

    return d


def get_d_gen_pos_freq():
    d_gen_pos_freq = {}

    for pos in ['str_nouns', 'str_adjectives', 'str_verbs', 'str_partizip_i', 'str_other_words', 'str_word_pairs']:
        d_gen_pos_freq[pos] = pos_freq_dic(pos)

    return d_gen_pos_freq