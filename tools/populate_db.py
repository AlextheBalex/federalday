# -*- coding: utf-8 -*
from __future__ import unicode_literals, print_function
import django

django.setup()

from django.db import transaction
import sys
import os
from basics.models import *
from dictionary_functions import simple_dictionary, multi_option_dictionary, multi_option_dictionary_v_always_l, word_pair_dictionary
from standard_word_filter import l_part_of_speech_dics, create_part_of_speech_strings_with_persons_and_wiki_titles
from download_plenarprotokolle import download_latest_plenarprotokolle, get_last_pdf_legnum_docnum
from fun_with_xml import transform_pdf
from commons import clean_text_add_spaces, get_d_gen_pos_freq
from analyze_statements import create_file_of_general_word_freqs, create_file_of_speaker_function_party_stmts_counts, get_l_significant_words, map_words_to_texts
from basics.views_helper import get_l_speaker_distances
from standard_word_filter import get_standardized_word_pairs_from_text


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
    function += ' '
    function = function.replace('im Bundesministerium', 'bei dem Bundesminister').replace('Staatssekretär ', 'Staatssekretär/in ').replace('Staatssekretärin', 'Staatssekretär/in').replace('räsident', 'räsident/in').replace('räsident/inin', 'räsident/in').replace('eauftragter', 'eauftragte/r').replace('eauftragte ', 'eauftragte/r ').replace('Senatorin', 'Senator/in').replace('Senator ', 'Senator/in ').replace('anzler ', 'anzler/in ').replace('anzlerin', 'anzler/in').replace('Chef ', 'Chef/in ')

    function = function.replace('inister ', 'inister/in ').replace('inisterin', 'inister/in').replace('bei der', 'bei der/bei dem').replace('beim', 'bei der/bei dem')

    return function.strip().replace('tärbei', 'tär bei').replace('BMAS', ' Bundesminister/in für Arbeit und Soziales').replace('Bundestags', 'Bundestages').replace('/in.', '/in').replace('Baden Württemberg', 'Baden-Württemberg')

def standardize_functions(function):

    function = function.replace(u'Staatsminister/in für Europa', u'Staatsminister/in für Europa im Auswärtigen Amt')

    l_functions_standard_function = [
        ([u'Beauftragte/r der Bundesregierung für die Belange behinderter Menschen',
         u'Beauftragte/r der Bundesregierung für die Belange der Behinderten',
         u'Beauftragte/r der Bundesregierung für die Belange von Menschen mit Behinderungen'],
        u'Beauftragte/r der Bundesregierung für die Belange von Menschen mit Behinderungen'),
        ([u'für Arbeit und Soziales', u'für Arbeit und Sozialordnung'], u'für Arbeit und Soziales'),
        ([u'für Bildung', u'Bundesminister/in für Bildung und Forschung', u'für Bildung und Wissenschaft'], u'für Bildung und Forschung'),
        ([u'für Ernährung und Landwirtschaft', u'für Ernährung'], u'für Ernährung und Landwirtschaft'),
        ([u'für Familie', u'für Familie und Senioren'], u'für Familie'),
        ([u'für wirtschaftliche Zusammenarbeit', u'für wirtschaftliche Zusammenarbeit und Entwicklung'], u'für wirtschaftliche Zusammenarbeit und Entwicklung')
        ]

    return function


def get_document_fields(document_path, stmt_block_no):

    d_doc = {}
    d_word_pairs = word_pair_dictionary()

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
        try:
            d_doc[order_id]['page'] = int(line.split('+page')[1])
        except IndexError:
            print(line)
            return 6

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
            elif d_doc[order_id]['party'] in ["Niedersachsen", "Thüringen", "Sachsen", "Rheinland-Pfalz", "Hamburg", "Brandenburg", "Schleswig-Holstein", "Baden-Württemberg", "Nordrhein-Westfalen", "Berlin", "Bremen", "Bayern", "Saarland", "Mecklenburg-Vorpommern", "Sachsen-Anhalt", "Hessen", "Baden Württemberg"]:
                d_doc[order_id]['party'] = ''
        except IndexError:
            d_doc[order_id]['party'] = ''

        d_doc[order_id]['party'] = d_doc[order_id]['party'].strip().replace('DIE LINKE.', 'DIE LINKE')
        if d_doc[order_id]['party'] in ['CSU', 'CSU/CSU']:
            d_doc[order_id]['party'] = 'CDU/CSU'
        if d_doc[order_id]['party'] in ['PDS', 'PDS/LL', 'PDS/Linke Liste', 'LINKE', 'DIE LINKE']:
            d_doc[order_id]['party'] = 'DIE LINKE'

        try:
            if u'Parl. Staatssekretär' in raw_speaker:
                function = u'Parl. Staatssekretär' + raw_speaker.split(u', Parl. Staatssekretär')[1]
                d_doc[order_id]['speaker'] = d_doc[order_id]['speaker'].split(u'Parl. Staatssekretär')[0].replace(',', '').strip()
            else:
                function = raw_speaker.split(',')[1]
        except IndexError:

            d_doc[order_id]['function'] = ''

            first_word = raw_speaker.split()[0]
            if 'räsident' in first_word or 'Senator' in first_word:
                function = first_word
                d_doc[order_id]['speaker'] = d_doc[order_id]['speaker'].replace(first_word, '').strip()
                d_doc[order_id]['party'] = ''
            else:
                function = 'Abgeordnete/r'
        if 'minister' in d_doc[order_id]['party']:
            d_doc[order_id]['function'] = d_doc[order_id]['party']
            d_doc[order_id]['party'] = ''
        d_doc[order_id]['function'] = make_functions_gender_neutral(function).strip().replace('Parl. Staatssekretär/in bei der/bei dem Bundesminister/in der Justiz und Verbraucherschutz', 'Parl. Staatssekretär/in bei der/bei dem Bundesminister/in der Justiz und für Verbraucherschutz').replace('Bundesministerium ', 'Bundesminister/in ').replace(u'für Justiz', u'der Justiz').replace(u'Bundesminister/in für Verteidigung', u'Bundesminister/in der Verteidigung').replace('))', ')').replace('Parlamentarischer', 'Parl.').replace(u'Bundesminister/in Wirtschaft und Technologie', u'Bundesminister/in für Wirtschaft und Technologie')

        text = line.split('|')[-1].split('+page')[0]
        d_doc[order_id]['text'] = text
        d_doc[order_id]['str_word_pairs'] = get_standardized_word_pairs_from_text(text, d_word_pairs)
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
        return 12, 0
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
                #print(order_id)
                try:
                    int(order_id)
                except ValueError:
                    continue

                e = d_doc[order_id]

                [party,__] = Party.objects.get_or_create(
                    name="unknown",
                    abbrev=e.get("party"),
                    significant_words='',
                )

                [func, __] = Function.objects.get_or_create(
                    name=e.get('function'),
                )
                # print(party, func)
                [speaker, __] = Speaker.objects.get_or_create(
                    name=e.get("speaker"),
                    party=party,
                    function=func,
                    significant_words=''
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
                    str_word_pairs=e.get('str_word_pairs'),
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


def add_significant_words_to_speaker():

    d_gen_pos_freq_dic = get_d_gen_pos_freq()

    for speaker in Speaker.objects.all():
        # print(speaker.name)
        stmts = RegularStatement.objects.filter(speaker=speaker)
        speaker.significant_words = '|'.join(get_l_significant_words(stmts, d_gen_pos_freq_dic))
        speaker.save(update_fields=["significant_words"])


def add_word_pairs_to_statements():
    print(add_word_pairs_to_statements)
    for leg_period in xrange(12, 19):
        print(leg_period)
        stmts = RegularStatement.objects.filter(**{'document__legislative_period': leg_period})
        for stmt in stmts:
            text = stmt.text
            set_word_pairs = get_standardized_word_pairs_from_text(text)

            stmt.str_word_pairs = '|'.join(set_word_pairs)
            #print(stmt.str_word_pairs)
            stmt.save(update_fields=["str_word_pairs"])

#add_word_pairs_to_statements()


'''def mark_statement_relevance():

    for stmt in RegularStatement.objects.all():
        if (u'Präsident' in stmt.speaker.function or u'Vizepräsident' in stmt.speaker.function) and not 'Bundesrat' in stmt.speaker.function:
            for i in ['a)', 'b)', 'c)', 'd)', 'e)', 'f)', 'g)']
            if 'usschuss' in stmt or stmt.text.count('Dr.') > 4:
                stmt.relevant = False
                stmt.save(update_fields=["relevant"])
                continue
        stmt.relevant = False
        stmt.save(update_fields=["relevant"])'''


def add_significant_words_to_parties():

    d_gen_pos_freq_dic = get_d_gen_pos_freq()
    for party in Party.objects.all():
        # print(speaker.name)
        stmts = RegularStatement.objects.filter(speaker__party=party)
        party.significant_words = '|'.join(get_l_significant_words(stmts, d_gen_pos_freq_dic))
        party.save(update_fields=["significant_words"])


def add_data_suggested_party_to_speaker():

    for speaker in Speaker.objects.all():
        l_no_shared_words_speaker, l_normalized_shares_parties = get_l_speaker_distances(speaker)
        if l_normalized_shares_parties:
            speaker.data_suggested_party = l_normalized_shares_parties[0][1]
            # print(speaker, l_normalized_shares_parties)
            speaker.save(update_fields=["data_suggested_party"])


def update_database(transform_pdfs, update_stats, pdf_transformation_start):

    txt_directory = os.path.dirname(os.path.realpath(sys.argv[0])).replace('federalday/tools',
                                                                   'app/txts/plenarprotokolle')

    new_documents_downloaded = False
    if download_latest_plenarprotokolle():
        new_documents_downloaded = True
    latest_pdf_legnum, latest_pdf_docnum = get_last_pdf_legnum_docnum()
    latest_leg_num_in_db, latest_docnum_in_db = get_latest_leg_period_doc_num_in_db()
    print(latest_leg_num_in_db, latest_docnum_in_db)

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

            if transform_pdfs and str(leg_num) + str(docnum).zfill(3) > pdf_transformation_start:
                print('working on pdf', pdf_file_name)
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
        #print(l_txt_file_paths)
        txts_to_db(l_txt_file_paths, stmt_block_no)

    if transform_pdfs or new_documents_downloaded or update_stats:

        print('doing statistics')
        add_statistics()
        print('creating file of general word freqs')
        create_file_of_general_word_freqs()
        print('creating file of speaker func party stmt counts')
        create_file_of_speaker_function_party_stmts_counts()
        print('adding significant words to speaker')
        add_significant_words_to_speaker()
        print('adding data suggested party to speaker')
        add_data_suggested_party_to_speaker()
        print('deleting saved search data')
        PickleCache.objects.all().delete()
        print('mapping words to texts')
        map_words_to_texts()


#update_database(False, True, '0')

#add_data_suggested_party_to_speaker()

#add_significant_words_to_parties()

#PickleCache.objects.all().delete()
#print(7)


def delete_all_tables():
    from django.db import connection
    with connection.cursor() as cursor:
        for table in ['basics_document', 'basics_function', 'basics_party', 'basics_picklecache', 'basics_regularstatement', 'basics_speaker', 'basics_statistics', 'basics_stmtblock', 'basics_wordmap', 'django_admin_log', 'django_content_type', 'django_migrations', 'django_session', 'auth_group', 'auth_group_permissions', 'auth_permission', 'auth_user', 'auth_user_groups', 'auth_user_user_permissions']:
            cursor.execute("DROP TABLE  IF EXISTS %s CASCADE" % table)

#delete_all_tables()
#print(get_latest_leg_period_doc_num_in_db())
