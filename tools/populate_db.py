# -*- coding: utf-8 -*
from __future__ import unicode_literals, print_function

import django

django.setup()

from django.db import transaction
import sys
import os
from basics.models import *
from dictionary_functions import simple_dictionary, multi_option_dictionary, multi_option_dictionary_v_always_l
from standard_word_filter import l_part_of_speech_dics, create_part_of_speech_strings_with_persons_and_wiki_titles
# from get_fields_from_document import get_document_fields
from download_plenarprotokolle import download_latest_plenarprotokolle, get_last_pdf_legnum_docnum
from fun_with_xml import transform_pdf
from commons import clean_text_add_spaces
from analyze_statements import create_file_of_general_word_freqs, create_file_of_speaker_function_party_stmts_counts


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


def make_functions_gender_neutral(function):
    function = function.replace('Staatssekretär ', 'Staatssekretär/in ').replace('Staatssekretärin', 'Staatssekretär/in').replace('räsident', 'räsident/in').replace('räsident/inin', 'räsident/in').replace('eauftragter', 'eauftragte/r').replace('eauftragte ', 'eauftragte/r ').replace('Senatorin', 'Senator/in').replace('Senator ', 'Senator/in ').replace('anzler ', 'anzler/in ').replace('anzlerin', 'anzler/in')

    function = function.replace('inister ', 'inister/in ').replace('inisterin', 'inister/in').replace('bei der', 'bei der/bei dem').replace('beim', 'bei der/bei dem')

    return function


def get_document_fields(document_path, stmt_block_no):

    d_doc = {}

    import codecs

    with codecs.open(document_path, 'r', encoding="utf-8") as the_file:

        l_lines = the_file.readlines()
        l_lines = [line.strip() for line in l_lines if line and line != u'\n']

    file_name = document_path.split('/')[-1]

    d_doc['date'] = l_lines[0]
    d_doc['legislative_period'] = file_name[:2]
    d_doc['document_id'] = int(file_name.split('.')[0])
    d_doc['url'] = ''.join(['http://dip21.bundestag.de/dip21/btp/', str(d_doc['legislative_period']), '/', str(d_doc['document_id']), '.pdf'])
    print(d_doc['url'])

    last_speaker = ''
    for order_id, line in enumerate(l_lines[1:]):
        d_doc[order_id] = {}

        d_doc[order_id]['page'] = int(line.split('+page')[1])

        raw_speaker = line.split('|')[1].replace('speaker', '')

        speaker = raw_speaker.split('(')[0].split(',')[0]
        d_doc[order_id]['speaker'] = speaker
        if speaker != last_speaker:
            stmt_block_no += 1
        d_doc[order_id]['stmt_block_no'] = stmt_block_no

        try:
            if raw_speaker.count('(') == 2 and not "(spricht von seinem Platz aus)" in raw_speaker:
                d_doc[order_id]['party'] = raw_speaker.split('(')[2].replace(')', '')
            else:
                d_doc[order_id]['party'] = raw_speaker.split('(')[1].replace(')', '')
            if "BÜNDNIS 90/" in d_doc[order_id]['party']:
                d_doc[order_id]['party'] = "BÜNDNIS 90/DIE GRÜNEN"
            elif d_doc[order_id]['party'] in ["Niedersachsen", "Thüringen", "Sachsen", "Rheinland-Pfalz", "Hamburg", "Brandenburg", "Schleswig-Holstein", "Baden-Württemberg", "Nordrhein-Westfalen", "Berlin", "Bremen", "Bayern", "Saarland", "Mecklenburg-Vorpommern", "Sachsen-Anhalt", "Hessen"]:
                d_doc[order_id]['party'] = ''
        except IndexError:
            d_doc[order_id]['party'] = ''

        d_doc[order_id]['party'] = d_doc[order_id]['party'].strip()

        try:
            function = raw_speaker.split(',')[1]
        except IndexError:
            d_doc[order_id]['function'] = ''
            first_word = raw_speaker.split()[0]
            if 'räsident' in first_word:
                function = first_word
                d_doc[order_id]['speaker'] = d_doc[order_id]['speaker'].replace(first_word, '').strip()
            else:
                function = 'Abgeordnete/r'
        d_doc[order_id]['function'] = make_functions_gender_neutral(function).strip().replace('Parl. Staatssekretär/in bei der/bei dem Bundesminister/in der Justiz und Verbraucherschutz', 'Parl. Staatssekretär/in bei der/bei dem Bundesminister/in der Justiz und für Verbraucherschutz')

        # for a in ['Bundes­ kanzler']:
        #    if a in d_doc[order_id]['function']:
        #        print(d_doc['document_id'], a)
        text = line.split('|')[-1].split('+page')[0]
        d_doc[order_id]['text'] = text
        d_doc[order_id]['cleaned_text'] = clean_text_add_spaces(text)
        d_doc[order_id]['str_adjectives'], d_doc[order_id]['str_nouns'], d_doc[order_id]['str_verbs'], d_doc[order_id]['str_partizip_i'], d_doc[order_id]['str_other_words'], d_doc[order_id]['str_persons'], d_doc[order_id]['str_titles'], d_doc[order_id]['no_unique_words'] = create_part_of_speech_strings_with_persons_and_wiki_titles(text, d_nouns, d_verbs, d_adjectives, d_partizip_i, d_first_names, d_last_names, set_no_first_first_names, d_wiki_titles)
    return d_doc, stmt_block_no

def get_txt_file_path(txt_directory, leg_num, docnum):

    file_path = '/'.join([txt_directory, str(leg_num).zfill(2), ''.join([str(leg_num).zfill(2), str(docnum).zfill(3), '.txt'])])

    if not os.path.exists(file_path):
        return False

    return file_path

def get_latest_leg_period_doc_num_in_db():
    try:
        latest_document_in_db = list(Document.objects.all().order_by("document_id"))[-1]

    except IndexError:
        return 16, 0
    latest_document_in_db_id = str(latest_document_in_db.document_id)
    docnum = latest_document_in_db_id[2:]
    leg_num = latest_document_in_db_id[:2]

    return int(leg_num), int(docnum)


def txts_to_db(l_txt_file_paths, stmt_block_no):

    for file_path in l_txt_file_paths:
        print('trying to put file to db:', file_path)

        d_doc, stmt_block_no = get_document_fields(file_path, stmt_block_no)

        # print(d_doc.get('document_id'))
        [doc, __] = Document.objects.get_or_create(
            legislative_period=d_doc.get("legislative_period", -1),
            document_id=d_doc.get("document_id", -1),
            date=d_doc.get("date", None).replace("/", "-"),
            url=d_doc.get("url", None)
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

                [func, __] = Function.objects.get_or_create(
                    name=e.get('function'),
                )
                # print(party, func)
                [speaker, __] = Speaker.objects.get_or_create(
                    name=e.get("speaker"),
                    party=party,
                    function=func,
                )

                [stmt_block_no0, __] = StmtBlock.objects.get_or_create(
                    stmt_block_no=e.get('stmt_block_no'),
                    speaker=speaker,
                    document=doc,
                )

                RegularStatement.objects.create(
                    text=e.get("text"),
                    str_adjectives=e.get('str_adjectives'),
                    str_nouns=e.get('str_nouns'),
                    str_verbs=e.get('str_verbs'),
                    str_partizip_i=e.get('str_partizip_i'),
                    str_other_words=e.get('str_other_words'),
                    str_persons=e.get('str_persons'),
                    str_titles=e.get('str_titles'),
                    order_id=order_id,
                    document=doc,
                    speaker=speaker,
                    page=e.get('page'),
                    cleaned_text=e.get('cleaned_text'),
                    stmt_block_no=stmt_block_no0,
                    no_unique_words=e.get('no_unique_words'),
                )

def add_statistics():

    Statistics.objects.create(
        no_plenarprotokolle=Document.objects.all().count(),
        no_speakers=Speaker.objects.all().count(),
        no_functions=Function.objects.all().count(),
        no_parties=Party.objects.all().count(),
    )

def update_database(first_delete_all, transform_pdfs):

    PickleCache.objects.all().delete()

    if first_delete_all:
        # if __name__ == "__main__":
        print(88888)
        StmtBlock.objects.all().delete()
        Speaker.objects.all().delete()
        RegularStatement.objects.all().delete()
        Document.objects.all().delete()
        Party.objects.all().delete()
        Function.objects.all().delete()

    txt_directory = os.path.dirname(os.path.realpath(sys.argv[0])).replace('federalday/tools',
                                                                           'app/txts/plenarprotokolle')
    download_latest_plenarprotokolle()
    latest_pdf_legnum, latest_pdf_docnum = get_last_pdf_legnum_docnum()
    latest_leg_num_in_db, latest_docnum_in_db = get_latest_leg_period_doc_num_in_db()
    # print(get_latest_leg_period_doc_num_in_db(), 999)

    leg_nums_to_db = xrange(latest_leg_num_in_db, latest_pdf_legnum + 1)
    # print(leg_nums_to_db, 99999999)
    stmt_block_no = 0
    for leg_num in leg_nums_to_db:
        l_txt_file_paths = []
        # print(leg_num, latest_leg_num_in_db, 'leg_num')
        if leg_num == latest_leg_num_in_db:
            # print(777)
            start_docnum = latest_docnum_in_db + 1
        else:
            # print(888)
            start_docnum = 1

        for docnum in xrange(start_docnum, 400):
            # print(docnum, leg_num, 'docnum989898')
            pdf_file_name = ''.join([str(leg_num).zfill(2), str(docnum).zfill(3), '.pdf'])
            print('working on pdf', pdf_file_name)
            if transform_pdfs:

                if transform_pdf(pdf_file_name):
                    pass
                else:
                    break

            file_path = get_txt_file_path(txt_directory, leg_num, docnum)
            if not file_path:
                break
            # print(file_path, 33333)
            l_txt_file_paths.append(file_path)
        # print(l_txt_file_paths)
        txts_to_db(l_txt_file_paths, stmt_block_no)

    add_statistics()

    create_file_of_general_word_freqs()

    create_file_of_speaker_function_party_stmts_counts()

# update_database(False, False)

# print(Document.objects.all())

# latest_document_in_db = list(Document.objects.all().order_by("document_id"))[-1]


PickleCache.objects.all().delete()
