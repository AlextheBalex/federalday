# -*- coding: utf-8 -*

from __future__ import unicode_literals
from dictionary_functions import simple_dictionary, multi_option_dictionary
from commons import clean_text


def make_genitiv(word):
    if word[-1] in u'szßx':
        genitiv_word = ''.join([word, "'"])
    else:
        genitiv_word = ''.join([word, 's'])
    return genitiv_word

set_no_first_first_names = {'Bundeskanzlerin', 'Kanzlerin', u'Präsidentin', 'Ministerin', 'Umweltministerin',
                            'Abgeordnete', 'Familienministerin', 'Finanzministerin', 'Bildungsministerin',
                            'Verkehrsministerin', 'Arbeitsministerin', 'Außenministerin', 'Premierministerin',
                            'Verteidigungsministerin', 'Innenministerin', u'Ministerpräsidentin', 'Bundeskanzler',
                            'Kanzler', u'Präsident', 'Minister', 'Umweltminister', 'Abgeordneter','Familienminister',
                            'Finanzminister', 'Bildungsminister', 'Verkehrsminister', 'Arbeitsminister',
                            'Außenminister', 'Premierminister', 'Verteidigungsminister', 'Innenminister',
                            u'Ministerpräsident', 'Nur', 'Premierminister', 'Premierministerin', 'Herr', 'Frau',
                            'Vizepräsident', 'Vizepräsidentin'}

#d_first_names = simple_dictionary('first_names.txt')
#d_last_names = multi_option_dictionary('last_names_short_full.txt')

def find_full_name_in_text(maybe_last_name, index, l_words, text, d_first_names, d_last_names, set_no_first_first_names):
    #print word, 55
    last_name = ''
    l_last_names = []
    l_first_names = []
    try:
        maybe_second_part_of_last_name = l_words[index + 1]
        maybe_full_last_name = ' '.join([maybe_last_name, maybe_second_part_of_last_name])

        if maybe_second_part_of_last_name in d_last_names and maybe_second_part_of_last_name not in d_first_names and  maybe_full_last_name in text:
            l_last_names.append(maybe_full_last_name)
    except IndexError:
        #print 5
        maybe_full_last_name = 'kk'
    try:
        value = d_last_names[maybe_last_name]
        #print value, 6
    except KeyError:
        return False
    if type(value) == list:

        for full_last_name in value:
            if full_last_name in text or make_genitiv(full_last_name) in text:
                if last_name:
                    l_last_names.append(full_last_name)
                else:
                    l_last_names = [full_last_name]
    else:
        l_last_names.append(value)
    longest_last_name = ''
    for last_name in l_last_names:
        if len(last_name) > len(longest_last_name) and last_name in text:
            longest_last_name = last_name
    #print longest_last_name, 'longest_last_name'
    if longest_last_name == maybe_full_last_name:
        #print 'yes'
        len_last_name = 1
    else:
        len_last_name = len(longest_last_name.split())

    maybe_first_name = l_words[index - len_last_name]

    if len(maybe_first_name) == 1:
        maybe_first_name = ''.join([maybe_first_name, '.'])
    #print maybe_first_name, 10
    #print index, 'index'
    #print len_last_name, 'len_last_name'
    if index >= len_last_name and maybe_first_name[0].isupper() and maybe_first_name in d_first_names:
        #print maybe_first_name, 11
        l_first_names.append(maybe_first_name)
        #print l_first_names
        if index >= len_last_name + 1:
            first_first_name = l_words[index - len_last_name - 1]

            #if first_first_name in set_no_first_first_names:
            #if first_first_name[0].isupper() and first_first_name in d_first_names and first_first_name not in set_no_first_first_names:
                #print first_first_name, first_first_name in set_no_first_first_names
                #l_first_names.append(first_first_name)

    first_name = ' '.join(l_first_names[::-1])
    #print first_name, 8
    if first_name and longest_last_name:
        full_name = ' '.join([first_name, longest_last_name])
        #print full_name
        if full_name in ['Crystal Meth', u'Beverly Hills', 'Bear Stearns', 'Merril Lynch', u'Washington Post', 'Morgan Stanley', 'Golden Gate Bridge', 'Freddie Mac', 'Fannie Mae', 'Morgan Chase', 'Wells Fargo', '', 'Taj Mahal', 'West Bank', 'Costa Rica', 'West Point', 'Grand Prix', 'Merrill Lynch', 'Hugo Boss', 'Oh Gott', 'Hong Kong', 'Pax Christi', 'Paris Ende', 'Judas Priest', 'Mai Zeit', 'North Face', 'West Coast', 'Visa Europe', 'Fox Sports', 'Kung Fu Panda', 'Frau das Kind', 'Texas Lightning', 'Go West', u'Villa Hügel', 'Grand Tour', 'Gold Council', 'Paris Saint Germain', 'Kung Fu', u'Jud Süß', 'Biene Maja', 'Tampa Bay', 'West End', 'Main Street', 'Dschihad Union', 'Red Bull', 'Al Kaida'] or full_name not in text:
            return False
        l_full_name = full_name.split()
        if len(l_full_name) > 2 and l_full_name[1] in d_first_names and l_full_name[0] in set_no_first_first_names:
            l_full_name = l_full_name[1:]
            full_name = ' '.join(l_full_name)

        return full_name
    else:
        return False

def find_mentioned_persons_from_text(text, d_first_names, d_last_names, set_no_first_first_names):
    d_persons = {}
    l_words = text.split()
    l_persons_in_text = []
    for index, word in enumerate(l_words):
        # print word, 0
        word = clean_text(word)
        if not word:
            continue
        if word in d_last_names:
            last_name = word
            full_name = find_full_name_in_text(last_name, index, l_words, text, d_first_names, d_last_names,
                                               set_no_first_first_names)
            #print full_name
            if full_name and full_name not in l_persons_in_text:
                l_persons_in_text.append(full_name)
        elif word[-1] in "'s":
            word = word[:-1]
            if word in d_last_names:
                # print word, 1
                full_name = find_full_name_in_text(word, index, l_words, text, d_first_names, d_last_names,
                                                   set_no_first_first_names)
                if full_name and full_name not in l_persons_in_text:
                    l_persons_in_text.append(full_name)

    return l_persons_in_text

#print find_mentioned_persons_from_text('Bundeskanzlerin Angela Merkel macht Horst Köhler', d_first_names, d_last_names, set_no_first_first_names)