# -*- coding: utf-8 -*
from __future__ import unicode_literals
import sqlite3
from find_persons import find_mentioned_persons_from_text
from commons import clean_text_add_spaces, l_of_words
from basics.models import *
from nltk import bigrams

from dictionary_functions import word_pair_dictionary


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
    elif part_of_speech == 'partizip_i':
        str_columns = 'all_forms, word'
    else:
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
    if part_of_speech == 'nouns':
        #print 6
        with open('data/other_capitalized_words3.txt', 'r') as f:
            l = f.read().decode('utf-8').split('\n')
            for line in l[:-1]:
                standard, all_forms = line.split('::')
                l_all_forms = all_forms.split('|')
                for form in l_all_forms:
                    d[form] = standard
        with open('data/abbrevs2.txt', 'r') as f:
            l = f.read().decode('utf-8').split('\n')
            l.append('IS')
            l.append('ISIS')
            l.append('UNO')
            l.append('NATO')
            l.append('EU')
            for line in l:
                d[line] = line
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
    word_new_orth = word.replace(u'ß', 'ss').replace('ph', 'f')
    word_new_orth_lower = word_new_orth.lower()
    first_letter = word[0]
    if first_letter.isupper() and word in d_nouns:
        return ''.join([d_nouns[word], '(n)'])
    elif first_letter.isupper() and word_new_orth in d_nouns:
        return ''.join([d_nouns[word_new_orth], '(n)'])
    if first_letter.isupper() and '-' in word:
        l_words = word.split('-')
        second_word = l_words[1]
        if second_word and second_word[0].isupper() and second_word in d_nouns:
            standard_second = d_nouns[second_word]
            return ''.join([word, '(n)']).replace(second_word, standard_second)
    if word_lower in d_partizip_i:
        return ''.join([d_partizip_i[word_lower], '(p)'])
    elif word_lower in d_adjectives:
        # print word, d_adjectives[word_lower]
        return ''.join([d_adjectives[word_lower], '(a)'])
    elif word_new_orth_lower in d_adjectives:
        # print word, d_adjectives[word_lower]
        return ''.join([d_adjectives[word_new_orth_lower], '(a)'])
    elif word_lower in d_verbs:
        return ''.join([d_verbs[word_lower], '(v)'])
    else:
        return word_lower

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

    cleaned_text = clean_text_add_spaces(text)# .replace("'", ' ')

    l_persons = find_mentioned_persons_from_text(text, d_first_names, d_last_names, set_no_first_first_names)

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

    no_unique_words = 0
    set_words_with_minus = ([])
    l_words2 = []
    for word in l_words:
        if len(word) < 2:
            continue
        if '-' not in word:
            l_words2.append(word)
        elif words_standard_form(word, d_nouns, d_adjectives, d_verbs, d_partizip_i)[-1] == ')':
            l_words2.append(word)
        elif word.startswith('-'):
            l_words2.append(word)
        elif words_standard_form(word.split('-')[0], d_nouns, d_adjectives, d_verbs, d_partizip_i)[-1] == ')':
            try:
                word1, word2 = word.split('-')
                l_words2.append(word1)
                l_words2.append(word2)
            except:
                l_words2.append(word)
        else:
            word1 = word.replace('-', '')
            if words_standard_form(word1, d_nouns, d_adjectives, d_verbs, d_partizip_i)[-1] == ')':
                l_words2.append(word1)
            else:
                l_words2.append(word)

    for word in l_words2:
        if not word:
            continue
        standard_form = words_standard_form(word, d_nouns, d_adjectives, d_verbs, d_partizip_i)
        if standard_form in l_words_in_text:
            continue
        no_unique_words += 1
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

    return str_adjectives, str_nouns, str_verbs, str_partizip_i, str_other_words, str_persons, str_titles, no_unique_words


#d_first_names = simple_dictionary('first_names.txt')
#d_last_names = multi_option_dictionary('last_names_short_full.txt')
#d_nouns, d_adjectives, d_verbs, d_partizip_i = l_part_of_speech_dics()

#print d_verbs[u'gekauftes']

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

#text = "Zweitens ist das kein deutsches Phänomen. In vielen Ländern, gerade in Europa, stellen wir fest – übrigens in den östlichen genauso wie in den westlichen Ländern –, dass Sportveranstaltungen offensichtlich missbraucht werden, um extremistische, antisemitische, gewaltbereite Parolen zu verbreiten und Gewalttaten im Umfeld von Sportveranstaltungen durchzuführen."

#print create_part_of_speech_strings_with_persons_and_wiki_titles(text, d_nouns, d_verbs, d_adjectives, d_partizip_i, d_first_names, d_last_names, set_no_first_first_names, d_wiki_titles)

#print words_standard_form('extremistisch', d_nouns, d_adjectives, d_verbs, d_partizip_i)

#conn, curs = connect_sqlite()
#part_of_speech_dictionary(conn, curs, 'adjectives')


def analyze_other_words():
    print 'analyzing other words'
    d_abbrevs = {}
    d_d_first_letter_capitalized_words = {}
    for i in u'ABCDEFGHIJKLMNOPQRSTUVWXYZÜÖÄ':
        d_d_first_letter_capitalized_words[i] = {}
    d_no_capital_or_upper_words = {}
    for leg_period in xrange(12, 19):
        stmts = RegularStatement.objects.filter(**{'document__legislative_period': leg_period})
        print leg_period
        for stmt in stmts:
            l_words = stmt.str_other_words.split('|')
            text = stmt.cleaned_text
            #if 'Obama' in text:
            #    print text
            for word in l_words:
                if not word or '-' in word:
                    continue
                if word[-1] == '-':
                    word = word[:-1]
                capitalized_word = ''.join([' ', word.capitalize(), ' '])
                upper_word = ''.join([' ', word.upper(), ' '])

                first_letter = capitalized_word[1]

                if capitalized_word in text:
                    #print capitalized_word
                    try:
                        if word in d_d_first_letter_capitalized_words[first_letter]:
                            d_d_first_letter_capitalized_words[first_letter][word] += 1
                        else:
                            d_d_first_letter_capitalized_words[first_letter][word] = 1
                    except KeyError:
                        #print first_letter
                        pass
                elif upper_word in text:
                    if word in d_abbrevs:
                        d_abbrevs[word] += 1
                    else:
                        d_abbrevs[word] = 1

                else:
                    if word in d_no_capital_or_upper_words:
                        d_no_capital_or_upper_words[word] += 1
                    else:
                        d_no_capital_or_upper_words[word] = 1

    d_first_letter_l_capitalized_words = {}
    for i in u'ABCDEFGHIJKLMNOPQRSTUVWXYZÜÖÄ':
        d_first_letter_capitalized_words = d_d_first_letter_capitalized_words[i]
        #print d_first_letter_capitalized_words

        d_first_letter_l_capitalized_words[i] = [word.capitalize() for word, count in d_first_letter_capitalized_words.iteritems() if (word not in d_no_capital_or_upper_words or d_no_capital_or_upper_words[word] < 5) and count > 2 and (word not in d_abbrevs or d_abbrevs[word] < 5) and word[0].isalpha()]

        #print len(d_first_letter_l_capitalized_words[i]), i

    l_abbrevs = [word.upper() for word, count in d_abbrevs.iteritems() if (word not in d_no_capital_or_upper_words or d_no_capital_or_upper_words[word] < 5) and count > 2 and (word not in d_first_letter_capitalized_words or d_first_letter_capitalized_words[word] < 5) and word[0].isalpha()]

    d_set_first_letter_word_stubs = {}
    l_short_capitalized_words = []
    set_endings = {'es', 'er', 'sse', 'ssen', 'en', 's', 'e', 'n'}
    l_endings = ['es', 'er', 'en', 's', 'e', 'n']
    for i in u'ABCDEFGHIJKLMNOPQRSTUVWXYZÜÖÄ':
        #print i
        set_word_stubs = set([])

        for word in d_first_letter_l_capitalized_words[i]:
            found_ending = False
            if len(word) > 6:
                if u'nderbeauftragte' in word:
                    print word
                word_stub = word.replace('ü', 'u').replace('ä', 'a').replace('ö', 'o').replace('ß', 'ss')
                if len(word) > 14:
                    for ending in ['ssen', 'sse']:
                        if word_stub.endswith(ending):
                            # if not ending == 's' or word_stub[-2] != 's':
                            word_stub = word_stub[:-len(ending)]
                            # else:
                            #    word_stub = word_stub[:-1]
                            found_ending = True
                            break
                    if found_ending:
                        set_word_stubs.add(word_stub)
                        continue

                for ending in l_endings:
                    if word_stub.endswith(ending):
                        #if not ending == 's' or word_stub[-2] != 's':
                        word_stub = word_stub[:-len(ending)]
                        #else:
                        #    word_stub = word_stub[:-1]
                        break

                set_word_stubs.add(word_stub)
            else:
                l_short_capitalized_words.append(word)
            #word_stub = word.replace('ü', 'u').replace('ä', 'a').replace('ö', 'o').replace('ß', 'ss')

        d_set_first_letter_word_stubs[i] = set_word_stubs
    d_first_letter_word_stubs_l_all_forms = {}
    set_endings.add('')
    l_extra_words = ['Masar-i-Scharif']

    for i in u'ABCDEFGHIJKLMNOPQRSTUVWXYZÜÖÄ':
        print i
        d_word_stubs = d_set_first_letter_word_stubs[i]
        d_word_stubs_l_all_forms = {}
        for word in d_d_first_letter_capitalized_words[i]:

            mod_word = word.replace('ü', 'u').replace('ä', 'a').replace('ö', 'o').replace('ß', 'ss').capitalize()
            #print mod_word
            for word_stub in d_word_stubs:
                len_word = len(word)
                len_word_stub = len(word_stub)
                if mod_word.startswith(word_stub) and mod_word[len_word_stub:] in set_endings:
                    #print mod_word
                        if word_stub in d_word_stubs_l_all_forms:
                            d_word_stubs_l_all_forms[word_stub].add(word.capitalize())
                        else:
                            d_word_stubs_l_all_forms[word_stub] = {word.capitalize()}
        d_first_letter_word_stubs_l_all_forms[i] = d_word_stubs_l_all_forms

    with open('data/other_capitalized_words2.txt', 'w') as a:
        for i in u'ABCDEFGHIJKLMNOPQRSTUVWXYZÜÖÄ':
            d_word_stubs_l_all_forms = d_first_letter_word_stubs_l_all_forms[i]
            for word, l_all_forms in d_word_stubs_l_all_forms.iteritems():
                shortest_word_length = 1000
                shortest_word = ''
                for word_form in l_all_forms:
                    len_word = len(word_form)
                    if len_word < shortest_word_length:
                        shortest_word = word_form
                        shortest_word_length = len_word
                #if len(l_all_forms) > 1:
                a.write(''.join([shortest_word, '::', '|'.join(l_all_forms), '\n']).encode('utf-8'))
        for word in l_short_capitalized_words:
            a.write(''.join([word, '::', word, '\n']).encode('utf-8'))

        for word in l_extra_words:
            a.write(''.join([word, '::', word, '\n']).encode('utf-8'))

    with open('data/abbrevs2.txt', 'w') as a:
        for word in l_abbrevs:
            a.write(''.join([word, '\n']).encode('utf-8'))


    #print set_capitalized_words

#analyze_other_words()


def get_standard_pair(set_word_pairs, str_set_articles):
    standard_form = False

    if len(set_word_pairs) == 1:
        standard_form = list(set_word_pairs)[0]
    elif len(set_word_pairs) == 2:
        first_word_pair, second_word_pair = set_word_pairs
        if len(first_word_pair) > len(second_word_pair):
            standard_form = second_word_pair
        else:
            standard_form = first_word_pair
    else:

        if str_set_articles == 'der':
            for word_pair in set_word_pairs:
                first_word = word_pair.split()[0]
                if first_word[-1] == 'e':
                    return word_pair

        if not standard_form:
            if str_set_articles == 'den':
                for word_pair in set_word_pairs:
                    first_word = word_pair.split()[0]
                    if first_word[-2:] == 'er' and word_pair[-2:]:
                        return word_pair
                    elif first_word[-1] == 'e':
                        return word_pair.replace(first_word, first_word + 'r')

        if not standard_form:
            if str_set_articles == 'das, den':
                for word_pair in set_word_pairs:
                    first_word = word_pair.split()[0]
                    if first_word[-2:] == 'er':
                        return word_pair
                    elif first_word[-1] == 'e':
                        return word_pair.replace(first_word, first_word + 'r')

        if not standard_form:
            for word_pair in set_word_pairs:
                first_word = word_pair.split()[0]
                if first_word[-1] not in 'ensrm' and word_pair[-1] != 's':
                    return word_pair

        if not standard_form:
            for word_pair in set_word_pairs:
                first_word = word_pair.split()[0]
                if first_word[-2:] == 'es' and not word_pair.endswith('s'):# and str_set_articles != 'das':
                    return word_pair

        if not standard_form:
            for word_pair in set_word_pairs:
                first_word = word_pair.split()[0]
                if first_word[-1:] == 'e':
                    return word_pair

        if not standard_form:
            for word_pair in set_word_pairs:
                first_word = word_pair.split()[0]
                if first_word[-2:] == 'er' and not word_pair.endswith('s'):
                    return word_pair


        if not standard_form:
            shortest_word_pair = ''
            len_shortest_word_pair = 'a'
            for word_pair in set_word_pairs:
                len_word_pair = len(word_pair)
                if len_word_pair < len_shortest_word_pair:
                    shortest_word_pair = word_pair
                    len_shortest_word_pair = len_word_pair
            standard_form = shortest_word_pair

    return standard_form

#print get_standard_pair({'Warschauer Pakts', 'Warschauer Paktes', 'Warschauer Pakt'}, '')


def find_word_pairs():

    set_not_first_word_stubs = {'Mein', 'Million', 'Abgeordnet', 'Kollegi', 'Kolleg', 'Minist', 'Ministeri', 'Welch', 'Ihrem', u'Bürg', 'Nord', 'Milliard', 'Millio', u'Rechtsausschuß', 'Unser', 'Gewerkschaft', 'Rentenversicherung', 'Staatsminist', 'Weiter', u'Abschließend', u'Umweltminist', 'Verbraucherzentral', 'Bundesinnenminist', 'Besonder', 'Finanz', u'Außenminist', u'Außenministeri', 'Konzertiert', 'Hundert', 'Verbraucherschutz', 'Herr', 'Frau', 'Bereich', 'Letzt', 'Aktuell', 'Verehrt', 'Abgegeben', 'Lieb', 'Wert', 'Osten', 'Reaktorsicherheit', 'Hilfe', 'Grupp', 'Buch', 'Finanzausschus', u'Technikfolgenabschätzung', u'Endgültig', 'Bundeskanzl', 'Bundeskanzleri', 'Verteidigungsausschus', 'Entwicklung', 'Haushaltsausschuss', 'Tagesordnungspunkt', 'Vereinbart', 'Erneuerbar', 'Bundesrepublik', 'Medi', 'Gegenprobe!-Enthaltungen?-Di', 'Sicherung', 'Gleich', 'Bundesregierung', 'Fortsetzung', 'Menge', 'Finanzminist', 'Handzeichen.-Di Gegenprobe!-Stimmenthaltungen?-Dann', 'Herzlich', 'Uns', 'Minut', 'Jahr', 'Schacht', 'Staat', u'Östlich', 'Regierung', 'Zukunft', 'Meng', 'Red', u'Ministerpräsident', u'Ministerpräsidenti', 'Land', 'Mitte', 'Schicksal', u'Präsident', 'Sein', 'Seit', 'Sieh', u'Stück', 'Summ', 'Tendenz', 'Teil', 'Them', 'Tisch', 'Tod', 'Tode', 'Tonn', 'Treib', 'Typs', 'Typ', u'Umweltökonomisch', 'Unabdingbar', u'Unabhängig', 'Unbedenklich', u'Grün', 'Grundbildung', 'Glas', 'Freund', 'Frag', 'Entsprechend', 'Einfach', 'EU-weit', 'Bundesland', u'Bundesaußenminist', 'Bildungsministeri', 'Bildungsminister', 'Beispiel', 'Arbeitsminist', 'Anlag', 'Verfolgt', 'Umfang', 'Tue', u'US-Präsident', 'Tourismuspolitisch', 'Tag', 'Studierend', u'Staatspräsident', u'Stück', 'Solch', 'Seit', 'Sein', 'Richtung', 'Sach', 'Regio', 'Problem', 'Kilomet', 'Kind', 'Koalitio', 'Koalitionsfraktion', 'Kommissar', 'Kommun', 'Konkret', 'Met', 'Meter', 'Beid', 'Fraktionsvorsitzend', u'Möglichkeit', u'Nächst', 'Monat', 'Kommerziell', 'Verfassungsorgan', u'Geschätzt', u'Gemäß', 'Transitland', 'Kurz', 'Ander', 'Beim', 'Bank', 'Bundesminist', 'Ding', 'Dutzend', 'Ehepaar', 'Fall', 'Firma', 'Familie', 'Forderung', 'Ge-Zu', 'Gesetzentwurf', 'Heimat', 'Heimatstadt', 'Insel', 'Leben', 'Laut', 'Liter', 'Manch', 'Schuld', 'Stund', 'Tausend'}

    set_first_word_not_pairing = set([])
    d_first_word_set_word_pairs = {}
    d_first_word_count = {}

    set_no_next_words = {'Sie', 'Frau', 'Herr', u'Nächster', 'Wes', 'Dr', 'Volksrepublik', 'Herrn', 'Professor', u'Schuß', 'Ihres', 'Ihrer', 'Schuss', 'Ich', 'Liebe', 'Verehrt', 'Ihren', 'Beratung', 'Antrag', 'Hohen', 'Ihr', 'Lieb', 'Meine', 'Ihrem', 'Euro', 'Prozent', 'Thema', u'Für', 'Anfang', 'Geist', 'Jedes', 'Jede', 'Jeder', 'Jeden', 'Jedem', 'Sicherheit', 'Recht', 'ZP', 'Bundesfinanzminist', 'Leistungsfähigkeit', 'Macht', 'Mein', 'Bereich', 'Deutschland', 'FDP', 'Herz', 'Jugend', u'Staatssekretär', u'Staatssekretärin', 'Seit', 'Kein', 'Millio', 'Mehr', 'Stadt', 'Verbraucherschutz', u'Länder', 'Land', 'Ausschuss', 'Haushaltsausschuss', 'Sozialordnung', 'Landwirtschaft', 'Teil', 'Bundesregierung', 'Stadtentwicklung', u'Beschlußempfehlung?-Gegenprobe!-Enthaltungen?-Di Beschlußempfehlung', 'Herzlich', 'Fraktion', 'Billion', 'Bundesregierung', 'Die', 'Tourismus', 'Faktor', 'Zwei', 'Rechtsausschuss', 'Tonnen', 'Wohnungswesen', 'Heute', 'Ende', 'Bundesregierung', 'Mensch', 'Menschen', 'DM', 'Schon', 'Verantwortung', 'Rechnung', 'Unbedenklich', u'Unabhängig', 'Verfolgt', 'Verfolgung', u'Länder', 'Ihre', 'Kanzl', u'Staatssekretär', u'Staatssekretäre', 'Kurz', 'Grundsatz', 'Vom', u'UN-Generalsekretär', 'Neun', 'Ihnen'}

    set_always_first_word = {'New', u'Europäischer', u'Europäischen', u'Europäisches', u'Europäische'}
    set_first_word_not_pairing.update(set_no_next_words)
    print set_first_word_not_pairing
    with open('data/str_other_words.txt', 'r') as f:
        l_lines = f.readlines()
        for line in l_lines:
            word, rel_freq = line.decode('utf-8').split('|')
            rel_freq = float(rel_freq)
            if rel_freq > 3.3:
                #if 'slamisch' in word:
                #    print word, 4
                #pass
                set_first_word_not_pairing.add(word.capitalize())

    with open('data/str_adjectives.txt', 'r') as f:
        l_lines = f.readlines()
        for line in l_lines:
            word, rel_freq = line.decode('utf-8').split('|')
            rel_freq = float(rel_freq)
            if rel_freq < 2:
                continue
            #if 'slamisch' in word:
            #    print word, 5, rel_freq
            capitalized_word = word.capitalize()
            for add in ['', 'e', 's', 'es', 'er', 'en', 'em']:

                set_first_word_not_pairing.add(''.join([capitalized_word, add]))

    d_word_pair_set_articles = {}
    d_word_pair_count = {}
    d_word_pair_set_texts = {}

    for leg_period in xrange(12, 19):
        stmts = RegularStatement.objects.filter(**{'document__legislative_period': leg_period})
        stmts = stmts.exclude(**{'speaker__function__name': u'Präsident/in'})
        stmts = stmts.exclude(**{'speaker__function__name': u'Vizepräsident/in'})
        print leg_period
        ignore_first_word = False
        for stmt in stmts:
            text = stmt.text
            pk = stmt.pk
            l_words = text.split()
            l_words = l_words[1:]
            for index, first_word in enumerate(l_words):
                if ignore_first_word:
                    ignore_first_word = False
                    continue
                if not first_word[0].isalpha():
                    first_word = first_word[1:]
                    if not first_word:
                        continue
                if first_word not in set_first_word_not_pairing and (first_word[-1].isalpha() or first_word[-1]
                    in '1234567890') and first_word[0].isupper():

                    if first_word in d_first_word_count:
                        d_first_word_count[first_word] += 1
                    else:
                        d_first_word_count[first_word] = 1
                    try:
                        next_word = l_words[index + 1]
                        if next_word[-1] in '.?!':
                            ignore_first_word = True
                        if next_word[0].isupper() and next_word not in set_no_next_words:

                            while True:
                                next_words_last_letter = next_word[-1]
                                if not next_words_last_letter.isalpha():
                                    next_word = next_word[:-1]
                                else:
                                    break
                            if next_word in set_no_next_words or len(next_word) == 1:
                                continue
                        else:
                            #set_first_word_not_pairing.add(first_word)
                            continue
                    except IndexError:
                        continue
                    article = ''
                    word_pair = ' '.join([first_word, next_word])
                    try:
                        maybe_article = l_words[index - 1]
                    except IndexError:
                        maybe_article = ''
                    if first_word.endswith('en'):

                            if maybe_article == 'der':
                                article = 'der'
                            elif maybe_article == 'die':
                                article = 'die'
                            elif maybe_article == 'den':
                                article = 'den'


                    else:
                        if maybe_article == 'das':
                            article = 'das'

                    try:
                        d_word_pair_count[word_pair] += 1
                        d_word_pair_set_texts[word_pair].add(pk)
                        d_word_pair_set_articles[word_pair].add(article)
                    except KeyError:
                        d_word_pair_count[word_pair] = 1
                        d_word_pair_set_texts[word_pair] = {pk}
                        d_word_pair_set_articles[word_pair] = {article}

    #print d_word_pair_count['Islamischen Staat'], 8787
    d_first_word_stub_second_word_count = {}
    d_first_word_stub_second_word_set_word_pairs = {}
    d_first_word_stub_second_word_set_pks = {}
    d_first_word_stub_second_word_set_articles = {}

    l_endings = ['en', 'es', 'er', 'em', 's', 'e', 'n', '']

    #print len(d_word_pair_count), 99999
    #return 6
    for word_pair, count in d_word_pair_count.iteritems():
        first_word, second_word = word_pair.split()
        if len(first_word) > 4:
            for index, ending in enumerate(l_endings):
                if first_word.endswith(ending):
                    if index > 6:
                        first_word_stub = first_word
                        break
                    elif index > 3:
                        first_word_stub = first_word[:-1]
                        break
                    else:
                        first_word_stub = first_word[:-2]
                        break
        else:
            first_word_stub = first_word

        if first_word_stub in set_not_first_word_stubs:
            continue

        first_word_stub_second_word = ' '.join([first_word_stub, second_word])

        try:
            d_first_word_stub_second_word_count[first_word_stub_second_word] += count
            d_first_word_stub_second_word_set_word_pairs[first_word_stub_second_word].add(word_pair)
            d_first_word_stub_second_word_set_pks[first_word_stub_second_word].update(d_word_pair_set_texts[word_pair])
            d_first_word_stub_second_word_set_articles[first_word_stub_second_word].update(d_word_pair_set_articles[word_pair])
        except KeyError:
            d_first_word_stub_second_word_count[first_word_stub_second_word] = count
            d_first_word_stub_second_word_set_word_pairs[first_word_stub_second_word] = {word_pair}
            d_first_word_stub_second_word_set_pks[first_word_stub_second_word] = d_word_pair_set_texts[word_pair]
            d_first_word_stub_second_word_set_articles[first_word_stub_second_word] = d_word_pair_set_articles[word_pair]

    d_first_word_stub_second_word_stub_set_word_pairs = {}
    d_first_word_stub_second_word_stub_set_pks = {}
    d_first_word_stub_second_word_stub_count = {}
    d_first_word_stub_second_stub_word_set_articles = {}
    for first_word_stub_second_word, set_word_pairs in d_first_word_stub_second_word_set_word_pairs.iteritems():

        if len(first_word_stub_second_word.split()[1]) > 4:
            if first_word_stub_second_word[-2:] == 'es':
                first_word_stub_second_word_stub = first_word_stub_second_word[:-2]
            elif first_word_stub_second_word[-1] == 's':
                first_word_stub_second_word_stub = first_word_stub_second_word[:-1]
            else:
                first_word_stub_second_word_stub = first_word_stub_second_word
        else:
            first_word_stub_second_word_stub = first_word_stub_second_word

        try:
            d_first_word_stub_second_word_stub_set_word_pairs[first_word_stub_second_word_stub].update(
                set_word_pairs)
            d_first_word_stub_second_word_stub_set_pks[first_word_stub_second_word_stub].update(
                d_first_word_stub_second_word_set_pks[first_word_stub_second_word])
            d_first_word_stub_second_word_stub_count[first_word_stub_second_word_stub] += \
                d_first_word_stub_second_word_count[first_word_stub_second_word]
            d_first_word_stub_second_stub_word_set_articles[first_word_stub_second_word_stub].update(
                d_first_word_stub_second_word_set_articles[first_word_stub_second_word])

        except KeyError:
            d_first_word_stub_second_word_stub_set_word_pairs[first_word_stub_second_word_stub] = set_word_pairs
            d_first_word_stub_second_word_stub_set_pks[first_word_stub_second_word_stub] = \
                d_first_word_stub_second_word_set_pks[first_word_stub_second_word]
            d_first_word_stub_second_word_stub_count[first_word_stub_second_word_stub] = \
                d_first_word_stub_second_word_count[first_word_stub_second_word]
            d_first_word_stub_second_stub_word_set_articles[first_word_stub_second_word_stub] = \
                d_first_word_stub_second_word_set_articles[first_word_stub_second_word]

    l = []
    for first_word_stub_second_word_stub, set_word_pairs in \
            d_first_word_stub_second_word_stub_set_word_pairs.iteritems():

        count = d_first_word_stub_second_word_stub_count[first_word_stub_second_word_stub]
        set_pks = d_first_word_stub_second_word_stub_set_pks[first_word_stub_second_word_stub]
        str_set_word_pairs = ', '.join(set_word_pairs)
        str_set_pks = ', '.join([str(i) for i in set_pks])
        set_articles = d_first_word_stub_second_stub_word_set_articles[first_word_stub_second_word_stub]
        str_set_articles = ', '.join(sorted([str(i) for i in set_articles if i]))
        standard_form = get_standard_pair(set_word_pairs, str_set_articles)

        #first_word_stub, second_word_stub = first_word_stub_second_word_stub.split()
        #stmts = RegularStatement.objects.all().filter(pk__in=set_pks)
        #l_texts = [stmt.text for stmt in stmts]

        l.append((count, standard_form, str_set_word_pairs, str_set_pks, str_set_articles))
    l.append([106, 'Euro Hawk', 'Euro Hawk', '1', 'der'])
    l = sorted(l)[::-1]

    with open('data/word_pairs.txt', 'w') as a:
        for count, first_word_stub_second_word_stub, str_set_word_pairs, str_set_pks, str_set_articles in l:
            if count > 10:
                a.write(' :: '.join([first_word_stub_second_word_stub, str_set_word_pairs]).encode('utf-8'))
                #a.write('::')
                #a.write(str_set_articles)
                a.write('\n')

#find_word_pairs()
#d_word_pairs = word_pair_dictionary()

def get_standardized_word_pairs_from_text(text, d_word_pairs):

    l_standard_word_pairs = []


    l_words = text.split()
    l_bigrams = list(bigrams(l_words))

    for bigram in l_bigrams:
        if not bigram[0][-1].isalpha():
            continue
        word_pair = ' '.join(bigram)
        while not word_pair[-1].isalpha() and word_pair[-1] not in '1234567890':
            word_pair = word_pair[:-1]
        while not word_pair[0].isalpha():
            word_pair = word_pair[1:]

        try:
            standard_pair = d_word_pairs[word_pair]
            l_standard_word_pairs.append(standard_pair)
        except KeyError:
            pass
    return '|'.join(set(l_standard_word_pairs))

#print get_standardized_word_pairs_from_text(u'Sehr geehrte Frau Präsidentin! Liebe Kolleginnen und Kollegen! Herr Minister! Ich bin jetzt die Erste, die im Plenum spricht, nachdem soeben alle Abgeordneten des Deutschen Bundestages von der Regierung darüber informiert Angela Merkels worden sind, dass sich Europa und damit auch Deutschland auf einen militärischen Angriff auf die Gebiete des „Islamischen Staates“ vorbereitet. Ich will sagen: Es fällt mir deshalb extrem schwer, jetzt einfach zur Tagesordnung überzugehen und mich darauf zu konzentrieren; ich will es aber trotzdem versuchen. Liebe Kolleginnen und Kollegen, 90 Prozent der Fläche in der Bundesrepublik sind ländlicher Raum. Jede zweite Bürgerin und jeder zweite Bürger wohnt im ländlichen Raum. Er ist damit keine Peripherie, kein Randbereich und auch kein Teil Deutschlands, der lediglich als Standort der Agrar-, Forst- und Energiewirtschaft verstanden werden darf.')
