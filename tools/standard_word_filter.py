# -*- coding: utf-8 -*
from __future__ import unicode_literals
import sqlite3
from find_persons import find_mentioned_persons_from_text
from dictionary_functions import simple_dictionary, multi_option_dictionary, multi_option_dictionary_v_always_l
from commons import clean_the_text_add_spaces, l_of_words


def connect_sqlite():
    conn = sqlite3.connect('/home/foritisiemperor/Music/transform_pdf/app/words.sqlite')
    c = conn.cursor()
    return conn, c

def select_columns_sqlite(conn, curs, table, col_name):
    sql = "SELECT %s from %s;" %(col_name, table)
    print sql
    o = curs.execute(sql)
    l = o.fetchall()
    l = [i for i in l]
    return l

def part_of_speech_dictionary(conn_sqlite, curs_sqlite, part_of_speech):
    print part_of_speech
    if part_of_speech in 'nouns, adjectives':
        str_columns = 'all_forms, nominativ_singular'
    if part_of_speech == 'partizip_i':
        str_columns = 'all_forms, word'
    if part_of_speech == 'verbs':
        str_columns = 'all_forms, infinitiv'
    l = select_columns_sqlite(conn_sqlite, curs_sqlite, part_of_speech, str_columns)
    d = {}
    for a_tuple in l:
        #print a_tuple
        l = a_tuple[0].split('/')
        #print l
        for i in l:
            if i not in d:
                d[i] = a_tuple[1]
    d.pop('', None)
    return d

def l_part_of_speech_dics():
    conn, curs = connect_sqlite()
    l_parts_of_speech = ['nouns', 'adjectives', 'verbs', 'partizip_i']
    l_ds = []
    for part_of_speech in l_parts_of_speech:
        part_of_speech_d = part_of_speech_dictionary(conn, curs, part_of_speech)
        l_ds.append(part_of_speech_d)
    return l_ds

def words_standard_form(word, d_nouns, d_adjectives, d_verbs, d_partizip_i):
    word_lower = word.lower()
    if word[0].isupper() and word in d_nouns:
        standard_form = ''.join([d_nouns[word], '(n)'])
    elif word_lower in d_partizip_i:
        standard_form = ''.join([d_partizip_i[word_lower], '(p)'])
    elif word_lower in d_adjectives:
        standard_form = ''.join([d_adjectives[word_lower], '(a)'])
    elif word_lower in d_verbs:
        standard_form = ''.join([d_verbs[word_lower], '(v)'])

    else:
        return word_lower
    return standard_form

def find_wiki_titles_from_text(text, d_wiki_titles):
    l_words = l_of_words(text)
    l_titles_in_text = []
    index = -1
    skip_indexes = 0
    while True:
        index += 1 + skip_indexes
        try:
            word = l_words[index]
            #print word
        except IndexError:
            #print index, word
            break
        skip_indexes = 0
        if (word[0].isupper() or word.startswith('al-')) and word in d_wiki_titles:
            #print word, 1
            l_full_forms = d_wiki_titles[word]
            #print l_full_forms, 2
            longest_full_form = ''
            text_part = ''.join([' '.join(l_words[index : index + 4]), ' '])
            for full_form in l_full_forms:
                if ''.join([full_form, ' ']) in text_part:
                    #print full_form, 8
                    len_full_form = len(full_form)
                    if len_full_form > len(longest_full_form):
                        longest_full_form = full_form
            if longest_full_form:
                skip_indexes = len(longest_full_form.split()) - 1
                if longest_full_form not in l_titles_in_text:
                    l_titles_in_text.append(longest_full_form)
    return l_titles_in_text

def create_part_of_speech_strings_with_persons_and_wiki_titles(text, d_nouns, d_verbs, d_adjectives, d_partizip_i, d_first_names, d_last_names, set_no_first_first_names, d_wiki_titles):

    cleaned_text = clean_the_text_add_spaces(text).replace("'", ' ')

    l_persons = find_mentioned_persons_from_text(text, d_first_names, d_last_names, set_no_first_first_names)
    for person in l_persons:
        cleaned_text = cleaned_text.replace(person, ' ')

    str_persons = '|'.join(l_persons)

    l_titles_in_text = find_wiki_titles_from_text(text, d_wiki_titles)

    str_titles = '|'.join(l_titles_in_text)

    l_words_in_text = []
    l_words = set(cleaned_text.split())
    l_adjectives = []
    l_nouns = []
    l_verbs = []
    l_partizip_i = []
    l_other_words = []
    for word in l_words:
        if len(word) < 2:
            continue
        standard_form = words_standard_form(word, d_nouns, d_adjectives, d_verbs, d_partizip_i)
        if standard_form in l_words_in_text:
            continue
        #print word, standard_form
        l_words_in_text.append(standard_form)
        if '(a)' in standard_form:
            l_adjectives.append(standard_form.split('(')[0])
        elif '(n)' in standard_form:
            l_nouns.append(standard_form.split('(')[0])
        elif '(v)' in standard_form:
            l_verbs.append(standard_form.split('(')[0])
        elif '(p)' in standard_form:
            l_partizip_i.append(standard_form.split('(')[0])
        else:
            l_other_words.append(standard_form)
    str_adjectives = '|'.join(l_adjectives)
    #return str_adjectives, 1
    str_nouns = '|'.join(l_nouns)
    str_verbs = '|'.join(l_verbs)
    str_partizip_i = '|'.join(l_partizip_i)
    #print l_other_words, 2
    str_other_words = '|'.join(l_other_words)

    return str_adjectives, str_nouns, str_verbs, str_partizip_i, str_other_words, str_persons, str_titles



#d_first_names = simple_dictionary('first_names.txt')
#d_last_names = multi_option_dictionary('last_names_short_full.txt')
#d_nouns, d_adjectives, d_verbs, d_partizip_i = l_part_of_speech_dics()
#d_wiki_titles = multi_option_dictionary_v_always_l('wiki_titles_with_synonyms_first_word_full_form_reduced.txt')

set_no_first_first_names = {'Bundeskanzlerin', 'Kanzlerin', u'Präsidentin', 'Ministerin', 'Umweltministerin',
                            'Abgeordnete', 'Familienministerin', 'Finanzministerin', 'Bildungsministerin',
                            'Verkehrsministerin', 'Arbeitsministerin', 'Außenministerin', 'Premierministerin',
                            'Verteidigungsministerin', 'Innenministerin', u'Ministerpräsidentin', 'Bundeskanzler',
                            'Kanzler', u'Präsident', 'Minister', 'Umweltminister', 'Abgeordneter', 'Familienminister',
                            'Finanzminister', 'Bildungsminister', 'Verkehrsminister', 'Arbeitsminister',
                            'Außenminister', 'Premierminister', 'Verteidigungsminister', 'Innenminister',
                            u'Ministerpräsident', 'Nur', 'Premierminister', 'Premierministerin', 'Herr', 'Frau',
                            'Vizepräsident', 'Vizepräsidentin'}

text = "kleines Frankreich Deutschland Stefan Müller Hunde größer laufendes fahrendes fuhr Angela Merkel"

#print create_part_of_speech_strings_with_persons_and_wiki_titles(text, d_nouns, d_verbs, d_adjectives, d_partizip_i, d_first_names, d_last_names, set_no_first_first_names, d_wiki_titles)