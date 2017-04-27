# -*- coding: utf-8 -*

import xml.etree.cElementTree as ET
import numpy
import os
import sys
from os import listdir
import re
import math

project_directory = os.path.dirname(os.path.realpath(sys.argv[0]))
print project_directory


def list_to_file(li, file_path):
    with open(file_path, 'w') as a:
        for line in li:
            
            try:
                a.write(line.encode('utf-8'))
            except UnicodeDecodeError:
                a.write(line)
            a.write('\n')
            
            
def first_tuple_item_list_to_file(li, file_path):
    with open(file_path, 'w') as a:
        for line in li:
            line = line[0]
            try:
                a.write(line.encode('utf-8'))
            except UnicodeDecodeError:
                a.write(line)
            a.write('\n')

def tuple_list_to_file(li, file_path):
    with open(file_path, 'w') as a:
        for bbox, line in li:
            #print line
            try:
                a.write(bbox.encode('utf-8'))
                a.write('\n')
                a.write(line.encode('utf-8'))
            except UnicodeDecodeError:
                a.write(bbox)
                a.write(line)
            a.write('\n')
            
            
def unite_lines(lines_list):
    
    new_lines_list = []
    new_line_list = []
    index = 0
    
    while True:
        try:
            line = lines_list[index]
        except IndexError:
            break
        try:
            line_before = lines_list[index-1]
        except IndexError:
            line_before = ''
        #print line
        if not line:
            if new_line_list:
                new_line = ' '.join(new_line_list)
                new_lines_list.append(new_line)
            new_lines_list.append('')
            new_line_list = []
            index += 1
            continue
        elif new_line_list:
            new_line_list.append(line)
            index += 1
        else:
            new_line_list = [line]
            index += 1
    
    new_lines_list = [i.replace('    ', '') for i in new_lines_list]
    return new_lines_list
            

def get_l_bbox_textboxes_from_xml(xml_path):
    
    tree = ET.ElementTree(file=xml_path)
    l_bbox_textlines = []

    for page_elem in tree.iter('page'):
        page = page_elem.get('id')
        #if page > '1':
        #    break#####################
        for textline in page_elem.iter('textline'):
            l_textline = []
            l_bold_word = []
            #for textline in textbox.iter('textline'):
                #print sub_elem.attrib.get('text')
            for letter_elem in textline.iter('text'):
                letter = letter_elem.text
                #print letter_elem.get('font')
                try:
                    font = letter_elem.get('font')
                    
                    if 'Bold' in font:
                        bold = True
                        
                    else:
                        bold = False
                except TypeError:
                    #print letter_elem.get('text')
                    bold = False
                
                if bold and not l_bold_word and letter != ' ':
                    l_bold_word = [letter]
                elif bold and l_bold_word and letter != ' ':
                    l_bold_word.append(letter)
                    #print l_bold_word
                elif (not bold and l_bold_word) or (l_bold_word and letter == ' '):
                    bold_word = ''.join(l_bold_word).strip()
                    if bold_word[-1] == ',':
                        l_textline.append(''.join([bold_word[:-1], '[bold]', ',']))
                    elif bold_word[-1] == ':':
                        l_textline.append(''.join([bold_word[:-1], '[bold]', ':']))
                    elif bold_word[-1] == '.':
                        l_textline.append(''.join([bold_word[:-1], '[bold]', '.']))
                    else:
                        l_textline.append(''.join([bold_word, '[bold]']))
                    l_bold_word = []
                    l_textline.append(letter)
                    bold = False
                    
                elif not bold and not l_bold_word:
                    l_textline.append(letter)
                #l_textbox.append(letter)
            textline_text = ''.join(l_textline)
            if textline_text:
                bbox = textline.get('bbox')
                            
                page_bbox = ','.join([page, bbox])
                #print type(bbox)
                #break
                bbox_textline = [page_bbox, re.sub(u'\([A-Z]\)', u'', textline_text)]
                l_bbox_textlines.append(bbox_textline)
                #l_text_boxes.append('\n')
            #break
    return l_bbox_textlines



def get_median_x1(l_bbox_textboxes):
    l_x1 = []
    for bbox_textbox in l_bbox_textboxes:
        bbox = bbox_textbox[0]
        l_bbox = bbox.split(',')
        x1 = float(l_bbox[1])
        l_x1.append(x1)
    return numpy.median(l_x1)
#print get_median_x1(l_bbox_textboxes)


def order_page_side(l_side, min_x1_side, sec_min_x1_side):
    #print l_side, 'order_page_side 1'
    l_ordered_side = []
    min_x1_side += 4
    sec_min_x1_side += 5
    end_line_before = ''
    interruption = False
    
    d_side = {}
    y1_before = 0
    for y1, x1, line in l_side:
        if y1 in d_side:
            d_side[y1].append((x1, line))
        else:
            d_side[y1] = [(x1, line)]
    #print d_side
    for (k, l_x1_line) in d_side.iteritems():
        if len(l_x1_line) > 1:
            l_x1_line = sorted(l_x1_line)
            combined_line = ' '.join([a[1] for a in l_x1_line])
            d_side[k] = (l_x1_line[0][0], combined_line)
        else:
            d_side[k] = d_side[k][0]
            
    l_side = sorted([(k, v) for k, v in d_side.iteritems()])[::-1]
    l_side = [a[1] for a in l_side]
            
    for index, (x1, line) in enumerate(l_side):
        #if '(Schluss' in line:
        #    print line, 999
        line = line.strip()
        
        if not line: #or re.match(u'\([A-Z]\)', line):
            end_line_before = ''
            continue
        if end_line_before == ')':
            interruption = False
        if (x1 > sec_min_x1_side or '[' in line) and line.startswith('('):
            #interruption = True
            #if line[-1] == ')':
            #    interruption = False
            l_ordered_side.append('')
            line = ''.join(['    ', line])
            l_ordered_side.append(line)
        elif x1 > sec_min_x1_side:
            try:
                '''x1_before = l_side[index-1][0]
                next_x1 = l_side[index + 1][0]
                if next_x1 < sec_min_x1_side and line[-1] != ')' and x1_before < sec_min_x1_side:
                    l_ordered_side.append('')
                    line = ''.join(['>', line])
                else:'''
                line = ''.join(['    ', line])
                l_ordered_side.append(line)
            except IndexError:
                line = ''.join(['    ', line])
                l_ordered_side.append(line)
            
        elif x1 > min_x1_side: #or ('[bold]' in line.split()[0] and line[0].isupper()): #and not interruption:
            #print 'x1:', x1, 'min_1:', min_x1_side, line 
            l_ordered_side.append('')
            line = ''.join(['>', line])
            l_ordered_side.append(line)
        elif end_line_before == ')':

            l_ordered_side.append('')
            l_ordered_side.append(line)
        else:
            l_ordered_side.append(line)
            
        end_line_before = line[-1]
        
        
    return l_ordered_side


def order_page(l_page_x1_x2_lines, l_page_x1, l_page_x2):
    #schluss = False
    
    min_x1 = min(sorted(l_page_x1)[4:])
    max_x2 = max(sorted(l_page_x2)[:-4])
    middle_line = (min_x1 + max_x2)/2
    #print middle_line, 'm'
    
    l_left = []
    l_x1_left = []
    l_right = []
    l_x1_right = []
    
    l_left_lines = []
    l_right_lines = []
    
    for y1, x1, x2, line in l_page_x1_x2_lines:
        
        if x1 < middle_line:
            l_x1_left.append(x1)
            l_left.append((y1, x1, line))
        elif x1 >= middle_line:
            #if '(Schluss' in line:
            #    schluss = True
            #    print line, 'order_page'
            l_x1_right.append(x1)
            l_right.append((y1, x1, line))
 
    #print len(l_right), 'len l_right'
    #print l_right
    min_x1_left = min_x1
    l_x1_right = sorted(l_x1_right)
    try:
        min_x1_right = min(l_x1_right[5:])
        #print l_x1_right[5:10]
        #print 1
    except ValueError:
        min_x1_right = min(l_x1_right[1:])
        #print 2
    try:
        sec_min_x1_left = min([x for x in l_x1_left if x > min_x1_left + 3])
    except ValueError:
        sec_min_x1_left = min_x1_left + 10
    #print 3
    try:
        sec_min_x1_right = min([x for x in l_x1_right if x > min_x1_right + 3])
    except ValueError:
        sec_min_x1_right = min_x1_right + 10
    #print 666
    #print len(l_right), 'len l_right 2'
    #print l_right
    l_ordered_left = order_page_side(l_left, min_x1_left, sec_min_x1_left)
    l_ordered_right = order_page_side(l_right, min_x1_right, sec_min_x1_right)
    
    #print min_x1_left, 'min_x1_left'
    #print min_x1_right, 'min_x1_right'
    #print middle_line, 'middle_line'
    #print sec_min_x1_left, 'sec_min_left'
    #print sec_min_x1_right, 'sec_min_x1_right'
    #print 

    return l_ordered_left, l_ordered_right
    #print middle_line, 55
    #return 2, 4 


def is_crap(line):
    
    if line == '(cid:9)' or line == '(cid:9)[bold]' or re.match(u'^[1-90]+$', line) or re.match(u'^[1-90]+\s[A-Z]$', line) or line.count('.') > 5 or len(line) < 3:
        return True
    return False



def order_by_page(l_bbox_lines):
    
    last_page = int(l_bbox_lines[-1][0].split(',')[0])
    
    d_page_bbox_line = {}
    d_page_l_x1 = {}
    d_page_l_x2 = {}
    
    for page in xrange(1, last_page + 1):
        d_page_bbox_line[page] = []
        d_page_l_x1[page] = []
        d_page_l_x2[page] = []
    
    d_page_lines_left = {}
    d_page_lines_right = {}
    
    y1_before = ''
    l_temp_values_to_sort = []
    tempx1 = 100
    
    for bbox, line in l_bbox_lines:
        line = line.strip()
        #if '(Schluss: 13.04 Uhr)' in line:
            #print 888
        if is_crap(line):
            #print line
            continue
        l_bbox = bbox.split(',')
        page = int(l_bbox[0])
        x1 = int(float(l_bbox[1]))
        x2 = int(float(l_bbox[3]))
        y1 = math.ceil(float(l_bbox[2]))
        
        #line = ''.join([line, '+', str(page)])
        #if y1 == y1_before:
            #l_temp_values_to_sort.append([y1, tempx1, #x2, line])
            #tempx1 -= 1
            
            
        d_page_bbox_line[page].append([y1, x1, x2, line])
        d_page_l_x1[page].append(x1)
        d_page_l_x2[page].append(x2)
        
    for page in xrange(1, last_page + 1):
        #print 'page', page
        try:            
            d_page_bbox_line[page] = [a for a in sorted(d_page_bbox_line[page])[::-1]]
            d_page_lines_left[page], d_page_lines_right[page] = order_page(d_page_bbox_line[page], d_page_l_x1[page], d_page_l_x2[page])
        except ValueError:
            #print page
            d_page_lines_left[page], d_page_lines_right[page] = [], []
            
    return d_page_lines_left, d_page_lines_right


def general_ordering(xml_path):
    
    l_bbox_lines = get_l_bbox_textboxes_from_xml(xml_path)

    tuple_list_to_file(l_bbox_lines, '/home/foritisiemperor/Music/transform_pdf/app/xmls/position_file_last.txt')
    d_page_lines_left, d_page_lines_right = order_by_page(l_bbox_lines)

    l_lines = []
    
    page = 1
    while True:
        
        try:
            l_page_left = d_page_lines_left[page]
            #l_page_left = [''.join([line, '+', str(page)]) for line in l_page_left]
        except KeyError:
            print page, 'last page'
            
        try:
            l_page_right = d_page_lines_right[page]
            #l_page_right = [''.join([line, '+', str(page)]) for line in l_page_right]
        except KeyError:
            break
        l_lines.append('|page%i|' %(page))
        l_lines.append('')
        l_lines.extend(l_page_left)
        l_lines.extend(l_page_right)
        
        page += 1

    return l_lines

#l_lines = [u'und Finanzierung. Mit dieser Bibliothek wird der deut-', u'sche Beitrag zur Europäischen Digitalen Bibliothek', u'Europeana erbracht und damit Verpflichtungen gegen-', u'über der EU entsprochen.']
    
def correct_split_words(lines_list):

    index = 0
    d_trans_lines = {}
    while True:
        try:
            line = d_trans_lines[index]
            #print line, 4
        except KeyError:
            try:
                line = lines_list[index]
            except IndexError:
                break
            #print line
        len_line = len(line)
        #print line[-1], len(line)
        if len_line > 15 and line[-1] == u'-':
            #print line, 0
            try:
                next_line = lines_list[index+1]
            except IndexError:
                break
            if re.match(u'^[a-zäüöß].{3,}', next_line) and not (next_line.startswith('und ') or next_line.startswith('oder ')):
                #print 1, next_line
                li_words_line = line.split()
                word_first_part = li_words_line[-1][:-1]
                line = ' '.join(li_words_line[:-1])
                #print line, 1
                next_line = ''.join([word_first_part, next_line])
                #print next_line, 2
                d_trans_lines[index] = line
                d_trans_lines[index+1] = next_line
                index += 1
                continue
            elif next_line.startswith('|page'):
                try:
                    next_next_line = lines_list[index+2]
                except IndexError:
                    break
                if re.match(u'^[a-zäüöß].{3,}', next_next_line) and not (next_next_line.startswith('und ') or next_next_line.startswith('oder ')):
                    li_words_line = line.split()
                    word_first_part = li_words_line[-1][:-1]
                    line = ' '.join(li_words_line[:-1])
                    #print line, 1
                    next_next_line = ''.join([word_first_part, next_next_line])
                    #print next_line, 2
                    d_trans_lines[index] = line
                    d_trans_lines[index+1] = next_line
                    d_trans_lines[index+2] = next_next_line
                    index += 2
                    #print next_line, 1
                    continue
                    
        elif len_line > 15 and line[-7:] == '-[bold]':
            try:
                next_line = lines_list[index+1]
            except IndexError:
                break
            if re.match(r'^[a-zäüö].{3,}', next_line):
                li_words_line = line.split()
                word_first_part = li_words_line[-1][:-7]
                line = ' '.join(li_words_line[:-1])
                #print line, 1
                next_line = ''.join([word_first_part, next_line])
                #print next_line, 2
                d_trans_lines[index] = line
                d_trans_lines[index+1] = next_line
                index += 1
                continue
            
        d_trans_lines[index] = line
        index += 1
        
    l_trans_lines = []
    for index in xrange(len(d_trans_lines)):
        l_trans_lines.append(d_trans_lines[index])

    return l_trans_lines 
    
#print correct_split_words(l_lines)
        

#general_ordering('10248.xml')


def repair_faulty_lines(pdf_name, l_lines):
    
    d_faulty_pdfs = {
    '01016.pdf' : [(u'>Präsident[bold] Dr[bold]. Köhler[bold]  Das Wort hat der Herr', u'>Präsident[bold] Dr[bold]. Köhler[bold]: Das Wort hat der Herr')],
    '01111.pdf' : [(u'    Vizepäsident[bold] Dr[bold]. Schmid[bold]:  Verzeihung, Herr', u'    Vizepräsident[bold] Dr[bold]. Schmid[bold]:  Verzeihung, Herr')],
    '01222.pdf' : [(u'>Erler (SPD): Herr Präsident! Meine sehr', u'>Erler[bold] (SPD): Herr Präsident! Meine sehr')],
    '01222.pdf' : [(u'>Fröhlich (Frakionslos): Herr Präsiden! Meine', u'>Fröhlich[bold] (Fraktionslos): Herr Präsiden! Meine')],#, (u'    —Vizepräsident[bold] Dr[bold]. Schmid[bold]:', u'    Vizepräsident[bold] Dr[bold]. Schmid[bold]:')],
    '01017.pdf' : [(u'>Dr[bold].  Schröder[bold]  (CDU/CSU)  Ich s agte  bereits, daß', u'>Dr[bold].  Schröder[bold] (CDU/CSU):  Ich sagte  bereits, daß')],
    '01012.pdf' : [(u'>Blank[bold] CDU)[bold]:  Meine Damen und Herren! Meine', u'>Blank[bold] (CDU)[bold]:  Meine Damen und Herren! Meine')],
    '01014.pdf' : [(u'>Strauss (CSU): Meine Damen und Herren! Was', u'>Strauss[bold] (CSU): Meine Damen und Herren! Was'), (u'>Rische (KPD), Antragsteller: Meine Damen und', u'>Rische[bold] (KPD), Antragsteller: Meine Damen und')],
    '01019.pdf' : [(u'I  Präsident[bold] Dr[bold]. Köhler[bold]:  Meine Damen und Herren!', u'>Präsident[bold] Dr[bold]. Köhler[bold]:  Meine Damen und Herren!'), (u'>Matthes, Schriftführer: Beurlaubt sind wegen', u'>Matthes[bold], Schriftführer: Beurlaubt sind wegen')],
    '01011.pdf' :[(u"    Dr[bold]. Höpker-Aschoff[bold]  (FDP': Herr Präsident, ich", u"    Dr[bold]. Höpker-Aschoff[bold]  (FDP): Herr Präsident, ich")],
    '01010.pdf' : [(u'    Dr[bold]. Adenauer[bold].  Bundeskanzler: Meine Damen', u'Dr[bold]. Adenauer[bold].,  Bundeskanzler: Meine Damen')],
    '01028.pdf' : [(u'>Präsident[bold] Dr[bold]. Köhler[bold]. Das Wort hat Herr', u'>Präsident[bold] Dr[bold]. Köhler[bold]: Das Wort hat Herr')],
    '01027.pdf' : [(u'>Präsident[bold] Dr[bold]. Köhler[bold]  Als nächster Redner hat', u'>Präsident[bold] Dr[bold]. Köhler[bold]: Als nächster Redner hat'), (u'>Blücher, Bundesminister für Angelegenheiten', u'>Blücher[bold], Bundesminister für Angelegenheiten'), (u'    Vizepräsident[bold]  br[bold].  Schmid[bold]:  Das Wort hat der', u'    Vizepräsident[bold]  Dr[bold].  Schmid[bold]:  Das Wort hat der'), (u'>Loritz[bold]', u'>Loritz[bold] (WAV):'), (u'    (WAV):', u''), (u'    Ich spreche zur Geschäfts', u'    Ich spreche zur Geschäftsordnung,'), (u'ordnung,', u'')],
    '01024.pdf' : [(u'>Reimann (KPD): Ich habe offen und freimütig', u'>Reimann[bold] (KPD): Ich habe offen und freimütig')],
    '01029.pdf' : [(u'>Brunner[bold]  (SPD: Meine sehr verehrten Damen', u'>Brunner[bold]  (SPD): Meine sehr verehrten Damen')],
    '01025.pdf' : [(u'    Sauerborn[bold], Staatssekretär im, Bundesministerium', u'    Sauerborn[bold], Staatssekretär im Bundesministerium'), (u'>Renner[bold]  (KPD) Abgeordneter: Ich wäre schon seit', u'>Renner[bold] (KPD): Ich wäre schon seit')],
    '01031.pdf' : [(u'>Loritz[bold]  (WAV) Antragsteller: Ich werde nachher', u'>Loritz[bold]  (WAV), Antragsteller: Ich werde nachher')],
    '01037.pdf' : [(u'    (FDP)[bold]:  Aus diesem Grunde beantrage ich,', u'    Euler[bold] (FDP)[bold]:  Aus diesem Grunde beantrage ich,')],
    '01049.pdf' : [(u'>loritz[bold]  (BP): Nachdem der Herr Präsident', u'>Loritz[bold]  (BP): Nachdem der Herr Präsident'), (u'>loritz[bold] (WAV): Wir haben uns nicht mehr', u'>Loritz[bold] (WAV): Wir haben uns nicht mehr')]}
    
    if pdf_name in d_faulty_pdfs:
        for a_tuple in d_faulty_pdfs[pdf_name]:
            
            faulty_line, correct_line = a_tuple
            index_faulty_line = l_lines.index(faulty_line)
            l_lines[index_faulty_line] = correct_line
    
    return l_lines

#l_lines = [u'>Frau[bold] Karwatzki[bold],  Parl. Staatssekretär: Herr Kollege,']

def line_speaker_match(line):
    #print 0
    if re.match(u'^(Abg\[bold\]\.\s)?(von\[bold\]\s+)?[A-ZÖÜÄ][a-zöüäß\-\']{2,}([A-ZÖÜÄ][a-zöüäß\-\']{2,})?\[bold\]', line) or re.match(u'^([DO]r(\.-Ing)?(\[bold\])?\.\s{1,}){1,}(.*\[bold\]\s)*[A-ZÖÜÄ][a-zöüäß\-\']{2,}([A-ZÖÜÄ][a-zöüäß\-\']{2,})?\[bold\]', line) or re.match(u'^(Dr\[bold\]\.\s{1,}){1,}h(\[bold\])?\.\s*c\[bold\]\.\s{1,}[A-ZÖÜÄ\'][a-zäüöß\-]{2,}\[bold\]', line):
        #print 1
        
        maybe_speaker = line.split(':')[0]
        
        if len(maybe_speaker.split()) < 2:
            return False
        
        if '(' in maybe_speaker and not ')' in maybe_speaker or (re.match(u'.*\d{2,}.*', maybe_speaker) and not u'(BÜNDNIS' in maybe_speaker):
            return False
        for i in ['mitgeteil', 'gesagt', 'zitier', 'bekannt', 'agesordnung', 'Fortsetzung', '(TA)', '(UN', '(Dr.']:
            if i in maybe_speaker:
                return False
                
        if '[' in line and not '[bold]' in line:
            return False
        
        if re.match(u'^.{3,}\(.+\)\s*(\[bold\]\s*)*$', maybe_speaker) or ',' in maybe_speaker or u'präsiden' in maybe_speaker.lower():
            #print 2
            if maybe_speaker.count(',') > 1 and not 'minister' in maybe_speaker.lower():
                return False
        
            if ',' in maybe_speaker:
                last_word_maybe_speaker = maybe_speaker.split(',')[0].split()[-1]
                if last_word_maybe_speaker[0].islower():
                    #print 3
                    return False
                    
                maybe_title = maybe_speaker.split(',')[1]
                if maybe_title and maybe_title.strip()[0].islower():
                    return False
                
                if '[bold]' in maybe_title:
                    if re.match(u'^.{3,}\(.+\)\s*(\[bold\])?', maybe_speaker) or u'Bundeskanzler' in maybe_title or u'minister' in maybe_title.lower():
                        #print 4
                        #print maybe_title, maybe_speaker
                        pass 
                    else:
                        #print 6
                        return False
            
            if '.' in maybe_speaker and not ('Dr[bold].' in maybe_speaker or 'Dr.-Ing[bold]' in maybe_speaker or 'Abg[bold].' in maybe_speaker or 'Dr.' in maybe_speaker or 'Or[bold].' in maybe_speaker or 'Parl.' in maybe_speaker):
                #print 5
                return False

            #print 77, maybe_speaker
            return maybe_speaker
    
    return False
    

def mark_speakers(l_lines):
    index = 0
    l_lines_out = []
    
    while True:
        extra_index = False
        try:
            line = l_lines[index]
        except IndexError:
            break
        
        line = line.replace('>', '').replace('    ', '')
        line = ' '.join(line.split())
        l_lines_out.append(line)
        if ((re.match(u'^[A-ZÜÖÄ\']', line) or line.startswith('von')) and '[bold]' in line) and not line.startswith('('):
            #print 9
            if ':' in line:
                speaker = line_speaker_match(line)
                if speaker:

                    text = line.split(':')[1]
                    l_lines_out[-1] = ''.join(['|speaker', speaker, '|', text])
                    index += 1
                    continue 

            else:
                try:
                    next_line = l_lines[index + 1].replace('>', '').replace('    ', '')
                    if not next_line:
                        extra_index = True
                        next_line = l_lines[index + 2].replace('>', '').replace('    ', '')

                except IndexError:
                    pass
                next_line = ' '.join(next_line.split())
                combined_line = ' '.join([line, next_line])

                if ':' in combined_line:

                    if not line_speaker_match(next_line):

                        speaker = line_speaker_match(combined_line)

                    else:

                        speaker = False
                    if speaker:

                        text = combined_line.split(':')[1]
                        l_lines_out[-1] = ''.join(['|speaker', speaker, '|', text])
                        if extra_index:
                            index +=3
                        else:
                            index += 2
                        continue
                        
        index += 1
    
    l_lines_out_2 = []
    for line in l_lines_out:
        if line.startswith('|speaker') and l_lines_out_2[-1]:
            l_lines_out_2.append('')
            l_lines_out_2.append(line)
        else:
            l_lines_out_2.append(line)
            
            
    return l_lines_out_2
                
# print mark_speakers(l_lines)


def clean_lines(l_lines):

    l_lines = [line.replace(u'(cid:228)', u'ä') for line in l_lines]
    l_lines = [line.replace(u'(cid:252)', u'ü').replace(u'(cid:223)', u'ß').replace(u'(cid:150)', u'–').replace(u'(cid:220)', u'Ü').replace(u'(cid:246)', u'ö').replace(u'(cid:132)', u'„').replace(u'(cid:147)', u'“').replace(u'(cid:133)', u'...').replace(u'(cid:214)', u'Ö').replace(u'(cid:146)', u"'").replace(u'(cid:240)', u'ğ') for line in l_lines]
    
    l_lines = [' '.join([word.strip() for word in line.split()]) for line in l_lines]
    
    l_lines = [line.replace(',,', ',').replace(">'", ">").replace('(cid:9)', '').replace(u'    —', '    ').replace(u'President', u'Präsident'). replace(u'>Präsident Dr[bold].', u'>Präsident[bold] Dr[bold].').replace(');', '),').replace('{', '(').replace(' :', ':').replace(' .', '.') for line in l_lines]
    
    return l_lines

#l_lines = [u'gleichzeitig die Ab schiebung abgelehnter Asylbewerber zu forcieren']
    
def clean_lines_2(l_lines):
    
    
    l_lines = [line.replace('(', ' (') for line in l_lines]
    l_lines = [u' '.join(line.split()) for line in l_lines]
    l_lines = [line.replace(' :', ':').replace('[bold]', '').replace(u'GRÜ- NEN', u'GRÜNEN').replace('- ', '-').replace('-und ', '- und ').replace('-oder ', '- oder').replace('/ ', '/') for line in l_lines]
    
    for index, line in enumerate(l_lines):
        l_lines[index] = line.replace(u'In nern', u'Innern').replace(u'Bundes kanzler', u'Bundeskanzler').replace(u'Bun des', u'Bundes').replace(u'Bun- d', u'Bund').replace(u'Bundes- m', u'Bundesm').replace(u'Finan- zen', u'Finanzen').replace(u'Um- welt', u'Umwelt').replace(u'Ver- braucher', u'Verbraucher').replace(u'In- nern', u'Innern').replace(u'Bundes- ka', u'Bundeska').replace(' .', '.').replace('Ab schiebung', 'Abschiebung').replace(u'\xad ', '').replace(u'\xad', '-')

        
    return l_lines
    
#print clean_lines_2(l_lines)
    
def add_speakers(l_pages_speakers_indexes, l_lines):

    deleted_lines_count = 0
    
    l_indexes_lines = [[index, line] for (index, line) in enumerate(l_lines)]
    
    for speaker, index in l_pages_speakers_indexes:
        index -= deleted_lines_count
        if speaker.startswith('|page'):
            continue
        else:
            line = l_lines[index]
            try:
                speaker, text = line.split(':')
                l_indexes_lines[index][1] = ''.join(['|speaker:', speaker, '|', text])
            except ValueError:
                print line
                next_line = l_lines[index + 1]
                combined_line = ' '.join([line, next_line])
                print combined_line
                speaker, text = combined_line.split(':')
                l_indexes_lines[index][1] = ''.join(['|speaker:', speaker, '|', text])
                
                l_indexes_lines.pop(index+1)
                deleted_lines_count += 1
            
    l_lines = [i[1] for i in l_indexes_lines]
    return l_lines

#l_lines_in = [u'>Danke schön. – Frau Staatsministerin, bitte.', '|page17|','', 'Deutscher Bundestag – 18. Wahlperiode – 13. Sitzung. Berlin, Mittwoch, den 12. Februar 2014','','>Dr[bold]. Maria[bold] Böhmer[bold], Staatsministerin im Auswärtigen','', '','Amt:', '>Der Zuspruch zu den Deutschkursen an den Goethe-', 'Instituten ist in der Tat sehr gut. Ich glaube, sie haben']

def take_out_page_headers(l_lines_in):
    l_lines_out = ['']
    index = 0
    page_header = False
    
    while True:
        try:
            line = l_lines_in[index]
        except IndexError:
            break
        index += 1
        if line.startswith('|page'):
            page_header = True
            l_lines_out.append(line)
            continue
        
        if page_header:
            #print line, 1
            if not line or re.match(u'[1-90]+', line):
                #print line, 2
                continue
            elif re.match(u'.*Deutscher.*Bundestag.*Wahlperiode.*Sitzung.*[1-90]{4}.*', line):
                #print line, 3
                continue
            else:
                #print line, 4
                if line[0] == '>': 
                    l_lines_out.append(line)
                page_header = False
                continue
        else:        
            if l_lines_out[-1] and line.startswith('>'):
                l_lines_out.append('')
            l_lines_out.append(line)
            
    return l_lines_out

#print take_out_page_headers(l_lines_in)


def add_date(l_lines):
    
    l_months = ['', 'Januar', 'Februar', u'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']
    
    for line in l_lines:
        if re.match(u'.*Deutscher.*Bundestag.*Wahlperiode.*Sitzung.*,\s+den.*[1-90]{4}.*', line):
            raw_date = line.split('den')[-1].replace('[bold]', '').replace('.', '')
            day, month, year = raw_date.split()
            month = str(l_months.index(month)).zfill(2)

            date = '/'.join([year, month, day])
            
            return date
        elif re.match(u'.*(Berlin|Bonn).*,.*,\s+den.*[1-90]{4}.*', line):
            raw_date = line.split('den')[-1].replace('[bold]', '').replace('.', '')
            day, month, year = raw_date.split()
            month = str(l_months.index(month)).zfill(2)
            date = '/'.join([year, month, day])
            
            return date
            

    print 'fail'
            
            
def cut_end(l_lines):
    #print len(l_lines), 'len uncut'

    cut_lines = []
    before_end = False
    #re.match(u'.*Die\sSitzung\sist\sgeschlossen\.', line)
    #re.match(u'.*\(Schlu(ss|ß).*:.*Uhr.*\).*', line)
    for line in l_lines[::-1]:
        #if line.startswith('(Schluss'):
            #print 777
        if not before_end and (re.match(u'.*Die\sSitzung\sist\sgeschlossen\.', line) or re.match(u'.*\(Schlu(ss|ß).*:.*Uhr.*\).*', line)):
            #print line
            before_end = True
        if before_end:
            cut_lines.append(line)
    #print len(cut_lines), 'len cut'
    return cut_lines[::-1]


def cut_beginning(l_lines_text_output):
    
    l_lines_text_output_2 = []
    append = False
    for line in l_lines_text_output:
        if not append and line.startswith('|speaker'):
            append = True
        if append:
          l_lines_text_output_2.append(line)  
            
    
    return l_lines_text_output_2
    
#l_lines =['Ich lege ein besonderes Augenmerk auf die Willkommenskultur. Nachdem wir in der letzten Legislaturperiode die Weichen dafür hier im Land gestellt haben, ist es auch sehr sinnvoll, mit aller Kraft und Kreativität die','','','','Möglichkeiten der Auswärtigen Kultur und Bildungspolitik auszuloten und zu nutzen, um die Willkommenskultur weiter voranzubringen. Für die Arbeit im Bundestag ist eines entscheidend: Manch einer hat mir gesagt: Es gibt hier eine sogenannte Große Koalition, wenn es um Kultur- und Bildungspolitik geht. – Ich würde sagen: Es gibt hierbei eine Allparteienkoalition. Ich sage rückblickend herzlichen Dank an alle, die sich so intensiv eingebracht haben.']
    
def take_out_interruptions(l_lines):
    
    interruption = False
    l_new_lines = []
    add = ''
    for index, line in enumerate(l_lines):
        if line.startswith('('):
            if '|page' in line:
                add = re.findall(u'\|page\d+\|', line)[0]
                #print add

            interruption = True
        else:

            line = ''.join([line, add])
            add = ''
            try:
                if line and interruption and not l_new_lines[-1] and not l_new_lines[-2] and not l_new_lines[-3]:
                    l_new_lines = l_new_lines[:-3]
                    line_to_combine = l_new_lines[-1]
                    l_new_lines.pop()
                    combi_line = ' '.join([line_to_combine, line])
                    l_new_lines.append(combi_line)
                elif line and interruption and not l_new_lines[-1] and not l_new_lines[-2]:
                    l_new_lines = l_new_lines[:-2]
                    line_to_combine = l_new_lines[-1]
                    l_new_lines.pop()
                    combi_line = ' '.join([line_to_combine, line])
                    l_new_lines.append(combi_line)
                else:
                    l_new_lines.append(line)
            except IndexError:
                l_new_lines.append(line)
            if not line.startswith('('):
                interruption = False
            
        
    return l_new_lines
    

def add_speakers_to_all_text_parts(l_lines):
    
    speaker = ''
    for index, line in enumerate(l_lines):
        if line.startswith('|speaker'):
            speaker = '|' + line.split('|')[1] + '|'
            continue
        elif not line:
            continue
        else:
            l_lines[index] = ''.join([speaker, line])
    
    l_new_lines = []
    
    for line in l_lines:
        if not line:
            l_new_lines.append(line)
        elif line.split('|')[2]:
            l_new_lines.append(line)
    return l_new_lines

#l_lines =['>Das Gesetz dient insgesamt drei primären Zielen . Es','', '', '', 'geht  darum,  die  Asylverfahren  zu  beschleunigen,  die'
#'Unterbringung  zu  erleichtern  und  gleichzeitig  die  Ab­', 'schiebung abgelehnter Asylbewerber zu forcieren . Auch']
    
def delete_useless_empty_lines(l_lines):
    
    l_new_lines = []
    line_not_finished = False
    index = 0
    while True:
        try:
            line = l_lines[index]
        except IndexError:
            return l_new_lines
        if line and line[-1] not in '.:?!|)':
            line_not_finished = True
        elif line:
            line_not_finished = False
            
        if not line and line_not_finished:
            try:
                next_line = l_lines[index+1]
                if next_line.startswith('|speaker'):
                    l_new_lines.append('')
            except IndexError:
                pass
        else:
            if line.startswith('(') and ')' not in line[:-1]:
                l_new_lines.append('')
            l_new_lines.append(line)
        if line.endswith(')'):
            l_new_lines.append('')
            
        index += 1
        
    return l_new_lines
            
#print delete_useless_empty_lines(l_lines)

def add_page_numbers_to_lines(l_lines):
    
    for line in l_lines:
        page_str = re.findall(u'\|page\d+\|', line)
        if page_str:
            page = str(int(page_str[0].split('e')[1][:-1]) - 1)
            break
    
    l_new_lines = []
    
    for line in l_lines:
        page_str = re.findall(u'\|page\d+\|', line)
        if page_str:
            
            page = str(int(page_str[0].split('e')[1][:-1]))
            line = re.sub(u'\|page\d+\|', u'', line)
        if line:
            line = ''.join([line, '+page', page])
        l_new_lines.append(line)
    
    return l_new_lines
            

def transform_pdf(pdf_name):
    
    pdf_path = '/'.join(['/home/foritisiemperor/Music/transform_pdf/app', 'pdfs', 'plenarprotokolle', pdf_name[:2], pdf_name])
    if os.path.exists(pdf_path):
        print pdf_path
    else:
        return False
    xml_path = pdf_path[:-4].replace('pdfs', 'xmls') + '.xml'
    xml_dir = os.path.dirname(xml_path)
    #print local_dir
    if os.path.exists(xml_dir) == False:
        os.makedirs(xml_dir)
    output_path = pdf_path[:-4].replace('pdfs', 'txts') + '.txt'
    print xml_path, 1
    if not os.path.exists(xml_path):
        print 2
        bash_command = 'pdf2txt.py -o %s -t xml %s' %(xml_path, pdf_path)
        print xml_path, 'xml path'
        #print bash_command
        os.system(bash_command)
        
    l_lines = general_ordering(xml_path)
    #print len(l_lines), 1
    l_lines = cut_end(l_lines)
    #print len(l_lines), 2
    l_lines = clean_lines(l_lines)
    date = add_date(l_lines)
    #print len(l_lines), 3
    l_lines = take_out_page_headers(l_lines)
    #print len(l_lines), 4
    l_lines = correct_split_words(l_lines)
    #print len(l_lines), 5
    l_lines = repair_faulty_lines(pdf_name, l_lines)
    #print len(l_lines), 6
    l_lines = delete_useless_empty_lines(l_lines)
    #print len(l_lines), 7
    l_lines = mark_speakers(l_lines)
    #print len(l_lines), 8
    
    l_lines = cut_beginning(l_lines)
    #print len(l_lines), 9
    
    l_lines = unite_lines(l_lines)
    #print len(l_lines), 10
    
    l_lines = take_out_interruptions(l_lines)
    #print len(l_lines), 11
    l_lines = delete_useless_empty_lines(l_lines)
    #print len(l_lines), 12
    l_lines = unite_lines(l_lines)
    #print len(l_lines), 13
    l_lines = clean_lines_2(l_lines)
    #print len(l_lines), 14
    l_lines = add_speakers_to_all_text_parts(l_lines)
    #print len(l_lines), 15
    l_lines = add_page_numbers_to_lines(l_lines)
    
    l_lines = [date] + l_lines
    
    #test_speakers_output_path = '/'.join([project_directory, 'test_files', 'speakers', pdf_name.replace('pdf', 'txt')])
    
    #first_tuple_item_list_to_file(l_pages_speakers_indexes, test_speakers_output_path)
    
    output_dir = os.path.dirname(output_path)
    #print local_dir
    if os.path.exists(output_dir) == False:
        os.makedirs(output_dir)
    list_to_file(l_lines, output_path)
    return True
        

transform_pdf('18120.pdf')

#l = [u""">Das Gesetz dient insgesamt drei primären Zielen . Es

    

#geht  darum,  die  Asylverfahren  zu  beschleunigen,  die"""]
#print l

#for a in l:
#    a = ' '.join([word.strip() for word in a.split()])
#    print [a]
#    print a.replace(u'\n', '')

def transform_wahlperiode(wahlperiode):
    
    wahlperioden_dir = '/'.join([project_directory, 'pdfs', 'plenarprotokolle', wahlperiode])
    
    l_pdf_names = sorted([f for f in listdir(wahlperioden_dir)])
    
    for pdf_name in l_pdf_names:
        transform_pdf(pdf_name)
        print
        
#transform_wahlperiode('18')
