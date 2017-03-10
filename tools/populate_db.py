# -*- coding: utf-8 -*
from __future__ import unicode_literals, print_function

import django

django.setup()

from django.db import transaction
import sys
import os
from os import listdir
from basics.models import *
from dictionary_functions import simple_dictionary, multi_option_dictionary, multi_option_dictionary_v_always_l
from standard_word_filter import l_part_of_speech_dics, create_part_of_speech_strings_with_persons_and_wiki_titles
from get_fields_from_document import get_document_fields

txt_directory = os.path.dirname(os.path.realpath(sys.argv[0])).replace('federalday/tools', 'app/txts/plenarprotokolle')

d_first_names = simple_dictionary('first_names.txt')
d_last_names = multi_option_dictionary('last_names_short_full.txt')
d_nouns, d_adjectives, d_verbs, d_partizip_i = l_part_of_speech_dics()
d_wiki_titles = multi_option_dictionary_v_always_l('wiki_titles_with_synonyms_first_word_full_form_reduced.txt')
set_no_first_first_names = {'Bundeskanzlerin', 'Kanzlerin', u'Präsidentin', 'Ministerin', 'Umweltministerin',
                            'Abgeordnete', 'Familienministerin', 'Finanzministerin', 'Bildungsministerin',
                            'Verkehrsministerin', 'Arbeitsministerin', 'Außenministerin', 'Premierministerin',
                            'Verteidigungsministerin', 'Innenministerin', u'Ministerpräsidentin', 'Bundeskanzler',
                            'Kanzler', u'Präsident', 'Minister', 'Umweltminister', 'Abgeordneter', 'Familienminister',
                            'Finanzminister', 'Bildungsminister', 'Verkehrsminister', 'Arbeitsminister',
                            'Außenminister', 'Premierminister', 'Verteidigungsminister', 'Innenminister',
                            u'Ministerpräsident', 'Nur', 'Premierminister', 'Premierministerin', 'Herr', 'Frau',
                            'Vizepräsident', 'Vizepräsidentin', 'Kollege', 'Kollegin'}


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


if __name__ == "__main__":

    Speaker.objects.all().delete()
    RegularStatement.objects.all().delete()
    Document.objects.all().delete()
    Party.objects.all().delete()
    Function.objects.all().delete()

    l_file_paths = get_file_paths_legislative_period('18')


    for file_path in l_file_paths:
        print(file_path)
        d_doc = get_document_fields(file_path)
        #print(d_doc.get('document_id'))
        [doc, __] = Document.objects.get_or_create(
            legislative_period=d_doc.get("legislative_period", -1),
            document_id=d_doc.get("document_id", -1),
            date=d_doc.get("date", None).replace("/", "-"),
        )

        with transaction.atomic():
            for order_id in d_doc:
                try:
                    int(order_id)
                except ValueError:
                    continue

                e = d_doc[order_id]

                [party,__] = Party.objects.get_or_create(
                    name="unknown",
                    abbrev=e.get("party"),
                )

                [func,__] = Function.objects.get_or_create(
                    name=e.get('function'),
                )
                #print(party, func)
                [speaker,__] = Speaker.objects.get_or_create(
                    name=e.get("speaker"),
                    party=party,
                    function=func,
                )

                RegularStatement.objects.create(
                    text=e.get("text"),
                    str_adjectives = e.get('str_adjectives'),
                    str_nouns = e.get('str_nouns'),
                    str_verbs = e.get('str_verbs'),
                    str_partizip_i = e.get('partizip_i'),
                    str_other_words = e.get('str_other_words'),
                    str_persons = e.get('str_persons'),
                    str_titles = e.get('str_titles'),
                    order_id=order_id,
                    document=doc,
                    speaker=speaker,
                )

    '''try:
        cdu = Party.objects.get(abbrev="SPD")
        print(cdu)
    except Party.DoesNotExist:
        print("No SPD")'''

    #for x in ["Klugscheißer", "FrisörIn", "Schreiner"]:
    #    Function.objects.create(name=x)

    #Speaker.objects.create(name="Klaus Günther", party=)


    #print(Speaker.objects.all())
