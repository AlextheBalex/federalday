# -*- coding: utf-8 -*

import xml.etree.cElementTree as ET
import numpy
import os
import sys
from os import listdir
import re
import math
import string

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
    
    lines_list_2 = []
    
    for index, line in enumerate(lines_list):
        if line.startswith('ZP '):
            lines_list_2.append('')
        
        
        try:
            line_before = lines_list[index-1]
        except IndexError:
            line_before = ''
            
        if line_before.startswith('|page') and line.startswith('('):

            #print line, line_before
            lines_list_2.append('')
            lines_list_2.append(line)
            
            #index += 1
            continue
        lines_list_2.append(line)
    
    new_lines_list = []
    new_line_list = []
    index = 0
    
    while True:
        try:
            line = lines_list_2[index].strip()
        except IndexError:
            break
            
        try:
            line_before = lines_list_2[index-1]
        except IndexError:
            line_before = ''
            
        '''if line_before.startswith('|page') and line.startswith('('):

            print line, line_before
            new_lines_list.append('')
            new_lines_list.append(line)
            
            #index += 1
            continue'''
                
        #print line
        if not line or (len(line) > 10 and (line[1] == ')' or (line[1] == '.' and line[0] in '0123456789'))):
            if new_line_list:
                new_line = ' '.join(new_line_list)
                new_lines_list.append(new_line)
            new_lines_list.append('')
            if line:
                new_line_list = [line]
            else:
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
    
    if '14237' in xml_path or '14212' in xml_path or '15011' in xml_path:
    
        with open(xml_path, 'r') as a:
            l_lines = a.readlines()
            
        l_lines2 = []
        for index, line in enumerate(l_lines):
            line = line.decode('utf-8')
            if u'font="IOIPAG' in line or '00" bbox=' in line:

                pass
            elif '14237' in xml_path and index in [ 577817] and '</page>' in line:
                #print line
                pass
            elif '14212' in xml_path and index in [ 584597] and '</page>' in line:
                #print line
                pass
            elif '12057' in xml_path and index > 272106:
                pass
            #elif '15011' in xml_path and index == 430829:
            #    print line
            #    pass
            else:
                l_lines2.append(line)
                
        with open(xml_path, 'w') as a:
            for line in l_lines2:
                line = "%s" % line
                a.write(line.encode('utf-8'))

    tree = ET.ElementTree(file=xml_path)
    l_bbox_textlines = []

    for page_elem in tree.iter('page'):
        page = page_elem.get('id')
        #print page
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
        
        y1 = int(y1)
        if y1 in d_side:
            d_side[y1].append((x1, line))
        elif y1-1 in d_side:
            d_side[y1-1].append((x1, line))
        elif y1+1 in d_side:
            d_side[y1+1].append((x1, line))
        elif y1-2 in d_side:
            d_side[y1-2].append((x1, line))
        elif y1+2 in d_side:
            d_side[y1+2].append((x1, line))
        elif y1-3 in d_side:
            d_side[y1-3].append((x1, line))
        elif y1+3 in d_side:
            d_side[y1+3].append((x1, line))
        else:
            d_side[y1] = [(x1, line)]
    # print d_side
    for (y1, l_x1_line) in d_side.iteritems():
        len_l_x1_line = len(l_x1_line)
        if len_l_x1_line > 1:
            
            l_x1_line = sorted(l_x1_line)
            combined_line = ' '.join([a[1] for a in l_x1_line])
            d_side[y1] = (l_x1_line[0][0], combined_line)
        else:
            d_side[y1] = d_side[y1][0]
            
    l_side = sorted([(y1, v) for y1, v in d_side.iteritems()])[::-1]

    l_side = [a[1] for a in l_side]
            
    for index, (x1, line) in enumerate(l_side):
        line = line.strip().replace('(cid:9)', '')
        
        if not line:
            end_line_before = ''
            continue
        if end_line_before == ')':
            interruption = False
        if (x1 > sec_min_x1_side or '[' in line) and line.startswith('('):
            l_ordered_side.append('')
            line = ''.join(['    ', line])
            l_ordered_side.append(line)
        elif x1 > sec_min_x1_side:
            try:
                line = ''.join(['    ', line])
                l_ordered_side.append(line)
            except IndexError:
                line = ''.join(['    ', line])
                l_ordered_side.append(line)
            
        elif x1 > min_x1_side:
            l_ordered_side.append('')
            line = ''.join(['>', line])
            l_ordered_side.append(line)
        elif end_line_before == ')':

            l_ordered_side.append('')
            l_ordered_side.append(line)
        else:
            l_ordered_side.append(line)
            
        if line.endswith(')[bold]'):
            end_line_before = ')'
        else:
            end_line_before = line[-1]
        
    return l_ordered_side


def order_page(l_page_x1_x2_lines, l_page_x1, l_page_x2):
    
    try:
    
        min_x1 = min(sorted(l_page_x1)[4:])
        max_x2 = max(sorted(l_page_x2)[:-4])
    except ValueError:
        return [], []
    middle_line = (min_x1 + max_x2)/2 - 20
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
            if x2-x1 < 10 and x1 < middle_line + 20:
                #print line
                l_x1_left.append(x1)
                l_left.append((y1, x1, line))
                continue
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
        try:
            min_x1_right = min(l_x1_right[1:])
        except ValueError:
            min_x1_right = 0
            
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
    
    if line == '(cid:9)' or line == '(cid:9)[bold]' or re.match(u'^[1-90]+(\[bold\])?$', line) or re.match(u'^[1-90]+\s[A-Z]$', line):  #  or line.count('.') > 5 
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
        #try:            
        d_page_bbox_line[page] = [a for a in sorted(d_page_bbox_line[page])[::-1]]
        d_page_lines_left[page], d_page_lines_right[page] = order_page(d_page_bbox_line[page], d_page_l_x1[page], d_page_l_x2[page])
        #except ValueError:
            #print page
            #d_page_lines_left[page], #d_page_lines_right[page] = [], []
            
    return d_page_lines_left, d_page_lines_right

'''line = line.replace('(cid:39)', 'D').replace('(cid:72)', 'e').replace('(cid:88)', 'u').replace('(cid:87)', 't').replace('(cid:86)', 's').replace('(cid:70)', 'c')'''


def transform_cids(l_bbox_lines):
    
    l_bbox_lines_2 = []
    cmap = []

    for index, letter in enumerate('abcdefghijklmnopqrstuvwxyz'):
        cid = '(cid:' + str(68 + index) + ')'
        cmap.append([cid, letter])
        
    for index, letter in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
        cid = '(cid:' + str(36 + index) + ')'
        cmap.append([cid, letter])
        
    for index, number in enumerate('0123456789'):
        cid = '(cid:' + str(19 + index) + ')'
        cmap.append([cid, number])
        
        l_bbox_lines_2 = []
        for index, (bbox, line) in enumerate(l_bbox_lines):
            for cid, letter in cmap:
                line = line.replace(cid, letter)
            line = line.replace('(cid:3)', ' ').replace('(cid:15)', ',').replace('(cid:17)', '.').replace('(cid:137)', u'ß').replace('(cid:129)', u'ü').replace('(cid:18)', '/').replace('(cid:124)', u'ö').replace('(cid:108)', u'ä').replace('(cid:29)', ':').replace('(cid:104)', u'Ü').replace('(cid:16)', '-').replace('(cid:182)', "'").replace('(cid:11)', '(').replace('(cid:12)', ')').replace('(cid:177)', u'–').replace('(cid:196)', u'"').replace('(cid:179)', '"').replace('(cid:34)', '?').replace('(cid:30)', ';').replace('(cid:98)', u'Ä').replace('(cid:134)', u'§').replace('(cid:103)', u'Ö').replace('(cid:4)', '!').replace('(cid:62)', '[').replace('(cid:64)', ']').replace(' [bold]', '[bold]').replace('cid:112', u'é').replace('(cid:105)', u'á').replace('](', '] (').replace('(cid:195)', u'‚').replace('(cid:181)', u'‘').replace('(F.D.P.)', '(FDP)').replace('.[bold]', '[bold].').replace('(F.D.P,)', '(FDP)')
            l_bbox_lines_2.append((bbox, line))
    
    return l_bbox_lines_2

def general_ordering(xml_path):
    
    l_bbox_lines = get_l_bbox_textboxes_from_xml(xml_path)
    
    if l_bbox_lines[0][1].count('(cid:') > 12:
        l_bbox_lines = transform_cids(l_bbox_lines)
    
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
        l_lines.append('|page%i|' % page)
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
        #print d_trans_lines
        try:
            line = d_trans_lines[index].replace('- -', '-')
            #print line, 4
        except KeyError:
            try:
                line = lines_list[index].replace('- -', '-')
            except IndexError:
                break

        len_line = len(line)
        #print line[-1], len(line)
        if len_line > 15 and line[-1] == u'-':
            #print line, 0
            
            try:
                next_line = lines_list[index+1].replace('- -', '-')
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

#l_lines = ['uuz', u'Dr[bold]. Irmgard[bold] Schwaetzer[bold] (FDP):  Frau', 'kjhkjh.']

def no_bold_line_speaker_match(line, d_speaker_short_long):
    #print 0
    if re.match(u'^(Staatsminister\s)?(Abg\[bold\]\.\s)?(von\[bold\]\s+)?[A-ZÖÜÄ][a-zöüäß\-\']{2,}([A-ZÖÜÄ][a-zöüäß\-\']{2,})?(\[bold\])?', line) or re.match(u'^(Staatsminister\s)?([DO]r(\.-Ing)?(\[bold\])?\.\s{1,}){1,}(.*(\[bold\])?\s)*[A-ZÖÜÄ][a-zöüäß\-\']{2,}([A-ZÖÜÄ][a-zöüäß\-\']{2,})?(\[bold\])?', line) or re.match(u'^(Staatsminister\s)?(Dr\[bold\]\.\s{1,}){1,}h(\[bold\])?\.\s*c\[bold\]\.\s{1,}[A-ZÖÜÄ\'][a-zäüöß\-]{2,}(\[bold\])?', line) or re.match(u'^[A-Za-z]{,6}räsident.*:(\[bold\])?', line):
        #print 1
        
        maybe_speaker = line.split(':')[0]
        
        if len(maybe_speaker.split()) < 2:
            return False
        
        if '(' in maybe_speaker and not ')' in maybe_speaker or (re.match(u'.*\d{2,}.*', maybe_speaker) and not u'(BÜNDNIS' in maybe_speaker):
            return False
        for i in ['mitgeteil', 'gesagt', 'zitier', 'bekannt', 'agesordnung', 'Fortsetzung', '(TA)', '(UN', '(Dr.', 'Herr ', 'Sie ', ' ich ', 'So ', ' so ', ' wissen ', ' wir ', 'Wir ', 'und der', 'sprechen ', 'Ihnen,', ' man ', '?', '!', 'Brief[bold] des[bold]', ' habe', u'Präsidentschaft[bold]', u'erklärt', u'Wachstum[bold', u'Stichwort', 'Kollege', 'dennoch', 'wahr', ' CDU/CSU', '(alle', u'Ergänzung', 'TOP', ' stellen ', 'wollen', ' sein ', ' muss ', 'Inhalt', u'Überweisung', ' rufe ', '..', 'Anlage ', 'Beratung', 'Reden ', 'Herr[bold]', ' ja', ' hierzu', 'Stellung', ' nimmt', ' hat ', ' recht', ' USA', ' ist', ' zitier', 'Wort.', u'Änderung', '(II)', '(III)', 'Berichterstattung', ' mittei', 'Zusatzp', 'als', ' eine ', ' nennen', ' durch', u' heißt', ' dies', ' frag', ' sag', ' hin ', u' überwiesen', 'ZP', 'Nachtragshaushalt', ' hat', u'„', u'Ländern', 'Privilegien', u' muß', 'Solms Landwirtschaft', 'des Senats ', 'des Bundesrates ', 'seiner', u'geäußert', '  richtigen ', 'Gegenruf', 'Abgeordneten', ' einer ', ' wird ', 'Zitat', 'anderen', ' folgt', ' sind', ' wie', ' richtigen']:
            if i in maybe_speaker:
                return False
                
        if '[' in line and not '[bold]' in line:
            return False
            
        if 'minister' in line and not ',' in maybe_speaker.split('minister')[0]:
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
            maybe_speaker = repair_name(maybe_speaker)
            if ',' in maybe_speaker:
                speaker_short = maybe_speaker.split(',')[0]
                if speaker_short in d_speaker_short_long:
                    maybe_speaker = d_speaker_short_long[speaker_short]
            return maybe_speaker.strip()
    
    return False
    
#print no_bold_line_speaker_match('Dr. Paul Krüger, Ulrich Adam und der Fraktion der CDU/CSU')


def repair_name(name):
    #if 'Manfred' in name and ' r. ' in name:
        #print name
    l_small_stuff = [
    (' r. ', ''),
    (u'DIE GRÜ- NEN', u'DIE GRÜNEN'),
    ('(CDU/-CSU)', '(CDU/CSU)'),
    ('B ', 'B'),
    ('Sig rid', 'Sigrid'),
    ('Dr. h. c. ', ''),
    ('Dr. Ing. ', ''),
    ('Dr.-Ing. ', ''),
    ('Dr. ', ''),
    ('CDU/-CSU', 'CDU/CSU'),
    (u'Bündnis 90/GRÜNE', u'BÜNDNIS 90/DIE GRÜNEN'),
    (' (vom Platz aus sprechend)', ''),
    (' (vom Platz sprechend)', ''),
    (u'(BÜNDNIS DIE GRÜNEN)', u'(BÜNDNIS 90/DIE GRÜNEN)'),
    (u'Bündnis 90/GRUNE', u'BÜNDNIS 90/DIE GRÜNEN'),
    ('Mart in ', 'Martin '),
    ('WalCh', 'Walch'),
    ('(FPD)', '(FDP)'),
    ('Linke-Liste', 'Linke Liste'),
    ('Dr.', ''),
    (u'Bündnis', u'BÜNDNIS'),
    ('Prof. ', ''),
    ('Professor ', ''),
    (' d a', ''),
    ('h.c. ', ''),
    ('h. c ', ''),
    (u'Vizespräsident', u'Vizepräsident'),
    ('a. D. ', ''),
    ('Nobert', 'Norbert'),
    ('Bundesminister der n Justiz', 'Bundesminister der Justiz'),
    (u'und soziale Sicherung', u'und Soziale Sicherung'),
    (u'im Auswärtige Amt', u'im Auswärtigen Amt'),
    ('Parl ', 'Parl.'),
    ('Staatsminister beim Bundesminister Bundeskanzler', 'Staatsminister beim Bundeskanzler')]
    
    for stuff, replacement in l_small_stuff:
        name = name.replace(stuff, replacement)
        
    name = name.replace('Pari.', 'Parl.').replace(u'Dietmar Schütz (Oldenburg) (CDU/CSU)', 
    u'Peter Paziorek (CDU/CSU)').replace(u'Barbara Holl', 
    u'Barbara Höll').replace(u'HöII', 
    u'Höll').replace('Ottmar Schreiner (CDU/CSU)', 'Ottmar Schreiner (SPD)').replace('Peter H. Carstensen', 
    'Peter Harry Carstensen').replace(u'Petra Blass (PDS)',
    u'Petra Bläss (PDS)').replace(u'Petra Hinz (Herborn) (BÜNDNIS 90/DIE GRÜNEN)', 
    u'Priska Hinz (Herborn) (BÜNDNIS 90/DIE GRÜNEN)').replace(u'Petra Pau (fraktionslos)',
    u'Petra Pau (PDS)').replace(u'Gesine Lötzsch (fraktionslos)',
    u'Gesine Lötzsch (PDS)').replace(u'Rolf Kähne (PDS)',
    u'Rolf Köhne (PDS)').replace(u'Sevim Dagdelen',
    u'Sevim Dağdelen').replace(u'Thomas Koenigs (BÜNDNIS 90/DIE GRÜNEN)',
    u'Tom Koenigs (BÜNDNIS 90/DIE GRÜNEN)').replace('Uda Carmen Freia Heller (CDU/CSU)',
    'Uda Heller (CDU/CSU)').replace('Ulricke Flach', 
    'Ulrike Flach').replace(u'Uwe Göliner (SPD)', 
    u'Uwe Göllner (SPD)').replace('Wilhelm-Josef Sebastian',
    'Wilhelm Josef Sebastian').replace('Wolfgang BIerstedt',
    'Wolfgang Bierstedt').replace(u'Wolfgang Börnsen (Bönstrup) (SPD)',
    u'Wolfgang Börnsen (Bönstrup) (CDU/CSU)').replace('Wolfgang llte (SPD)',
    'Wolfgang Ilte (SPD)').replace('Wolfgang lite (SPD)', 'Wolfgang Ilte (SPD)').replace('Wolfgang Neskovic',
    u'Wolfgang Nešković').replace('fraktionlos',
    'fraktionslos').replace('Angela Dorothea Merkel',
    'Angela Merkel').replace('Raumordung', 'Raumordnung').replace(u'Jürgen Rütters', 
    u'Jürgen Rüttgers').replace('ministerde', 'minister de').replace(u'dentin Süssmuth', 
    u'dentin Rita Süssmuth').replace(u'für besondere Augaben und Chef des Bundeskanzleramtes',
    u'für besondere Aufgaben und Chef des Bundeskanzleramtes').replace(u'Frau Matthäus-Maier',
    u'Ingrid Matthäus-Maier').replace(u'Frau Rönsch',
    u'Hannelore Rönsch').replace(u'Vizepräsident Becker', 
    u'Vizepräsident Helmuth Becker').replace('Hans-Joachim Vogel',
    'Hans-Jochen Vogel').replace(u'Vizepräsident Klein', 
    u'Vizepräsident Hans Klein').replace(u'Vizepräsidentin Schmidt', 
    u'Vizepräsidentin Renate Schmidt').replace(u'Ministerpräsident Biedenkopf (Sachsen)', 
    u'Ministerpräsident Kurt Biedenkopf (Sachsen)').replace(u'Jürgen W. Möllemann', 
    u'Jürgen Möllemann').replace('Dieter Julius Kronenberg',
    'Dieter-Julius Kronenberg').replace(u'Uwe-Jens Rudi Rössel',
    u'Uwe-Jens Rössel').replace('Jens (SPD)', 
    'Uwe Jens (SPD)').replace('Pari. Staat',
    'Parl. Staat').replace('(CDU)', '(CDU/CSU)').replace('Gemot Eder (SPD)'
    , 'Gernot Erler (SPD)').replace('Gemot Erler (SPD)', 'Gernot Erler (SPD)').replace(u'Hansjörgen Doss', u'Hansjürgen Doss').replace('Heimrich (CDU/CSU)', 'Herbert Helmrich (CDU/CSU)').replace('Heinz Adolf', 
    'Heinz-Adolf').replace('Helmut Wieczorek (Duisburg) (FDP)', 'Helmut Wieczorek (Duisburg) (SPD)').replace('Don e Marx (SPD)', 
    'Dorle Marx (SPD)').replace('Herrmann Rind (FDP)', 'Hermann Rind (FDP)').replace('Volker Rahe', u'Volker Rühe').replace('Peter Raumsauer', 'Peter Ramsauer').replace('Simon Georg Wittmann',
    'Simon Wittmann').replace('Susanne Rahard-Vahldieck', 'Susanne Rahardt-Vahldieck').replace('Wilifried Penner', 
    'Willfried Penner').replace('Wilfried Penner', 'Willfried Penner').replace('Frau Adler (SPD)', 'Brigitte Adler (SPD)').replace(u'Frau Schmidt (Nürnberg) (SPD)',
    u'Renate Schmidt (Nürnberg) (SPD)').replace(u'Frau Schenk (BÜNDNIS 90/DIE GRÜNEN)', 
    u'Christina Schenk (BÜNDNIS 90/DIE GRÜNEN)').replace(u'Frau Götte', u'Rose Götte').replace('Frau Walz (FDP)', 'Ingrid Walz (FDP)').replace('Frau Bergmann-Pohl', 'Sabine Bergmann-Pohl').replace('Frau Wohlleben (SPD)',
    'Verena Wohlleben (SPD)').replace(u'Günter Friedrich Nolting',
    u'Günther Friedrich Nolting').replace('Frau Wolf (SPD)', 'Hanna Wolf (SPD)').replace(u'Frau Fischer (Gräfenhainichen) (SPD)', 
    u'Evelin Fischer (Gräfenhainichen) (SPD)').replace(u'Frau Eichhorn (CDU/CSU)', u'Maria Eichhorn (CDU/CSU)').replace(u'Frau Bläss (PDS/Linke Liste)',
    u'Petra Bläss (PDS/Linke Liste)').replace(u'Peter Bläss', u'Petra Bläss').replace('HitsChler', 'Hitschler').replace('Walther Hitschler', 'Walter Hitschler').replace('Walther Franz Altherr', 'Walter Franz Altherr').replace('Frau Odendahl (SPD)', 'Doris Odendahl (SPD)').replace('Cristian Schmidt', 'Christian Schmidt').replace(u'Dagmar G. Wöhrl', u'Dagmar Wöhrl').replace('Deltef', 'Detlef').replace(u'Bündnis',
    u'BÜNDNIS').replace('Wolfgang Freiherr von Steffen', 'Wolfgang Freiherr von Stetten').replace(u'Bömsen', u'Börnsen').replace('Voiker ', 'Volker ').replace(u'Frau Däubler-Gmelin', u'Herta Däubler-Gmelin').replace('Volkmar Uwe Vogel',
    'Volkmar Vogel').replace('Detlef von Larcher',
    'Detlev von Larcher').replace(u'Günther Verheugen', u'Günter Verheugen').replace('Uwe Jens Heuer', 'Uwe-Jens Heuer').replace('Ursula Eid-Simon', 'Uschi Eid').replace('Uschi Eid-Simon ', 'Uschi Eid ').replace('Usa Peters', 
    'Lisa Peters').replace('Uta Titze ', 'Uta Titze-Stecher ').replace('Ursula Jelpke', 
    'Ulla Jelpke').replace('Ursula Heinen ', 'Ursula Heinen Esser ').replace('Ulri ke',
    'Ulrike').replace(u'Ulrike Höfken-Deipenbrock', 
    u'Ulrike Höfken').replace('Ulrich Inner (FDP)', 
    'Ulrich Irmer (FDP)').replace(u'Ursula Lötzer', u'Ulla Lötzer').replace('Ursula Schmidt (Aachen) (SPD)', 'Ulla Schmidt (Aachen) (SPD)').replace('Ursula Burchardt (SPD)', 'Ulla Burchardt (SPD)').replace('Ueselott', 'Lieselott').replace('Tito Braune', 'Tilo Braune').replace('Susanne Jaffke-Witt', 'Susanne Jaffke').replace(u'Susanne Kastner Vizepräsidentin', 
    u'Vizepräsidentin Susanne Kastner').replace(u'Staatssekretär Bernd Kränzle (Bayern)', 
    u'Bernd Kränzle (Bayern), Staatssekretär').replace('Skarpells-Sperk', 'Skarpelis-Sperk').replace('Sigrig Hoth', 'Sigrid Hoth').replace('Sigrid Hoth (SPD)', 'Sigrid Hoth (FDP)').replace('Siegrid Hoth', 'Sigrid Hoth').replace('LoreMaria', 'Lore Maria').replace(u'Jürgen Koeppelin', 
    u'Jürgen Koppelin').replace('Joseph-Todor', 
    'Joseph-Theodor').replace('Rudolf Karl Krause (Bonese)', 'Rudolf Krause (Bonese)').replace('Rudolf Horst Meinl', 'Rudolf Meinl').replace('Ronja Schmitt', 'Ronja Kemmer').replace('Riege (PDS/Linke Liste)', 'Gerhard Riege (PDS/Linke Liste)').replace(u'Reinhard Göhner (FDP)', u'Reinhard Göhner, Parl. Staatssekretär').replace('Eckart Pick', 'Eckhart Pick').replace('Peter Patema', 'Peter Paterna').replace('Peter Harry Cartensen', 
    'Peter Harry Carstensen').replace('Peter Harald Rauen', 'Peter Rauen').replace('Paul Friedhoff',
    'Paul K. Friedhoff').replace('Minister Peter Fischer (Niedersachsen)', 'Peter Fischer, Minister (Niedersachsen)').replace(u'Norbert Rängen (CDU/CSU)', u'Norbert Röttgen (CDU/CSU)').replace('Norbert Formanski', 
    'Notberg Formanski').replace('Michaela Engelmeier-Heite', 'Michaela Engelmeier').replace('Martin Meyer (Siegertsbrunn) (CDU/CSU)', 'Martin Mayer (Siegertsbrunn) (CDU/CSU)').replace('Marielulse Beck', 'Marieluise Beck').replace(u'Marine Böttcher', u'Maritta Böttcher').replace(u'Marina Böttcher', u'Maritta Böttcher').replace('Maria Anna Klein-Schmeink', 'Maria Klein-Schmeink').replace('Margret Funke-Schmidt-Rink', 'Margret Funke-Schmitt-Rink').replace('Margarete Wolf', 
    'Margareta Wolf').replace('Margareta Wolf-Mayer', 'Margareta Wolf').replace('Lilo Blunck', 'Lieselott Blunck').replace('Liselott Blunck', 
    'Lieselott Blunck').replace('Konrad Elmar (SPD)', 'Konrad Elmer (SPD)').replace('Konrad Gildes (SPD)', 'Konrad Gilges (SPD)').replace('Klaus W. Lippold (Offenbach) (SPD)', 'Klaus W. Lippold (Offenbach) (CDU/CSU)').replace(u'Klaus-Jürgen Wamick', u'Klaus-Jürgen Warnick').replace('Klaus Hames', 'Klaus Harries').replace('Klaus-Dieter Uelhof ', 'Klaus-Dieter Uelhoff ').replace('Klaus-Dieter-Feige', 
    'Klaus-Dieter Feige').replace('Klaus Dieter Feige', 'Klaus-Dieter Feige').replace('von und zu Guttenberg', 'von Guttenberg').replace('Karl. ', 'Karl ').replace('Karl-Hermann Haack',
    'Karl Hermann Haack').replace('Klejdzinksi', 
    'Klejdzinski').replace('Karl-Heinz Homhues', 'Karl-Heinz Hornhues').replace('Kai Boris Gehring', 'Kai Gehring').replace(u'Kristina Köhler (CDU/CSU)', u'Kristina Schröder (CDU/CSU)').replace(u'Jürgen Stamick', u'Jürgen Starnick').replace(u'Jürgen Schmude (FDP)', u'Jürgen Schmude (SPD)').replace('Holle rith', 
    'Hollerith').replace('Jells Teuchner', 'Jella Teuchner').replace('Irmgard Adam-Schwaetzer (FDP)', 'Irmgard Schwaetzer (FDP)').replace(u'Ingrid Matthäus-Maler', u'Ingrid Matthäus-Maier').replace(u'Ingrid Matthäus Maier', u'Ingrid Matthäus-Maier').replace('Ingomar Heuchler', 'Ingomar Hauchler').replace(u'Inge Höger-Neuling', u'Inge Höger').replace(u'Hubert Wilhelm Hüppe', u'Hubert Hüppe').replace('Ulrich Inner (FDP)', 
    'Ulrich Irmer (FDP)').replace('Horst Kubatsrhka', 'Horst Kubatschka').replace('Horst Kubatschka (CDU/CSU)', 'Horst Kubatschka (SPD)').replace('Horst Eylmann (SPD)', 'Horst Eylmann (CDU/CSU)').replace('Herrmann Otto Solms', 'Hermann Otto Solms').replace('Otto Soims', 'Otto Solms').replace('Hermann E. Ott', 'Hermann Ott').replace('Helmut Koschyk (CDU/CSU)', 'Hartmut Koschyk (CDU/CSU)').replace('Heinz-Georg Seifert', 
    'Heinz-Georg Seiffert').replace('Heinz-Georg Seiffert (CDU/CSU)', 'Heinz Seiffert (CDU/CSU)').replace('Heinrich Leonhard Kolb', 'Heinrich L. Kolb').replace('Heinrich Kolb', 'Heinrich L. Kolb').replace('Heide Wright', 'Heidemarie Wright').replace('Heidi Wright', 'Heidemarie Wright').replace('Heidi Lippmann-Kasten', 
    'Heidi Lippmann').replace('Hedda Meseke (SPD)', 'Hedda Meseke (CDU/CSU)').replace('Hans Peter Bartels', 'Hans-Peter Bartels').replace('Hans-Jochim Otto', 'Hans-Joachim Otto').replace('Hans Joachim Otto', 'Hans-Joachim Otto').replace('Hans-Joachim Welt (SPD)', 
    'Jochen Welt (SPD)').replace('Hans Gottfried Bemrath (SPD)', 'Hans Gottfried Bernrath (SPD)').replace(u'Günther Krings', u'Günter Krings').replace(u'Günther Bredehom', u'Günther Bredehorn').replace('Grietje Bettin', 'Grietje Staffelt').replace('Gisela Altmann', 
    'Gila Altmann').replace('Gert Wiliner', 'Gert Willner').replace('Gernot Eder', 'Gernot Erler').replace('Gerhard O. Pfeffermann', 
    'Gerhard Pfeffermann').replace('Gerda Hasselfeld (CDU/CSU)', 'Gerda Hasselfeldt (CDU/CSU)').replace('Friehelm Ost', 'Friedhelm Ost').replace('Frederik Schulze', 'Frederick Schulze').replace('Frau Wollenberger', 'Vera Wollenberger').replace('Frau Wisniewski', 'Roswitha Wisniewski').replace('Frau Wieczorek-Zeul', 'Heidemarie Wieczorek-Zeul').replace('Frau Wiechatzek', 
    'Gabriele Wiechatzek').replace('Frau Weyel', 
    'Gudrun Weyel').replace('Frau Wetzel', 'Margrit Wetzel').replace('Frau Weiler', 'Barbara Weiler').replace('Frau von Teichman und Logischen', 
    'Cornelia von Teichman und Logischen').replace('Frau von Renesse', 'Margot von Renesse').replace('Frau Skarpelis-Sperk', 'Sigrid Skarpelis-Sperk').replace('Frau Schmalz-Jacobsen', 'Cornelia Schmalz-Jacobsen').replace('Frau Otto (SPD)', 'Helga Otto (SPD)').replace('Frau Merkel', 'Angela Merkel').replace('Frau Mehl', 'Ulrike Mehl').replace(u'Frau Matthäus-Maier', u'Ingrid Matthäus-Maier').replace(u'Frau Lucyga', u'Christine Lucyga').replace('Frau Leutheusser-Schnarrenberger', 
    'Sabine Leutheusser-Schnarrenberger').replace('Frau Lederer', 'Andrea Lederer').replace(u'Frau Köppe', u'Ingrid Köppe').replace('Frau Jelpke', 'Ulla Jelpke').replace('Frau Jaffke', 
    'Susanne Jaffke').replace('Frau Iwersen', 
    'Gabriele Iwersen').replace(u'Frau Höll', u'Barbara Höll').replace('Frau Hartenstein', 
    'Liesel Hartenstein').replace('Frau Gleicke', 
    'Iris Gleicke').replace('Frau Funke-Schmitt-Rink',
    'Margret Funke-Schmitt-Rink').replace('Frau Fischer', 'Frau Fischer').replace('Frau Fischer (PDS/Linke Liste)', 'Ursula Fischer (PDS/Linke Liste)').replace('Frau Enkelmann',
    'Dagmar Enkelmann').replace('Uta Titze-Stecher-Stecher', 'Uta Titze-Stecher')
    
    l = [
        (u'Probst Parl. St', 'Probst, Parl. St'),
        ('erninger Parl. Sta', 'erninger Parl. Sta'),
        (u'Präsident des Bundesrates Klaus Wedemeier', u'Klaus Wedemeier, Präsident des Bundesrates'),
        (u'Präsident des Senats Wedemeier (Bremen)', u'Klaus Wedemeier, Präsident des Senats (Bremen)'),
        ('Frau Caspers-Merk', 'Marion Caspers-Merk'),
        ('Frau Bulmahn', 'Edelgard Bulmahn'),
        ('Frau Braband', 'Jutta Braband'),
        ('Frau Blunck', 'Lieselott Blunck'),
        ('Frau Becker-Inglau', 'Ingrid Becker-Inglau'),
        ('Frau Babel', 'Gisela Babel'),
        ('Ferdi Tillmann', 'Ferdinand Tillmann'),
        (u'Eva-Maria Bulling-Schröter', u'Eva Bulling-Schröter'),
        ('Ernst Walthemathe', 'Ernst Waltemathe'),
        ('Erika Steinbach-Hermann', 'Erika Steinbach'),
        ('Erich Fritz', 'Erich G. Fritz'),
        ('Elke Leonhard-Schmid', 'Elke Leonhard'),
        ('Eike Maria Hovermann', 'Eike Hovermann'),
        ('Dagmar Engelmann', 'Dagmar Enkelmann'),
        ('Cornelle Sonntag-Wolgast', 'Cornelie Sonntag-Wolgast'),
        ('Cornelie von Teichman', 'Cornelia von Teichman und Logischen'),
        ('Cornelia Mayer', 'Conny Mayer'),
        ('Comelie Sonntag-Wolgast', 'Cornelie Sonntag-Wolgast'),
        ('Christine Lycyga', 'Christine Lucyga'),
        ('Christina Lucyga', 'Christine Lucyga'),
        ('Christine Lucyga', 'Christiane Lucyga'),
        ('Christen Happach-Kasan', 'Christel Happach-Kasan'),
        ('Carl Eduard von Bismarck', 'Carl-Eduard von Bismarck'),
        ('Cari-Detlev', 'Carl-Detlev'),
        ('Cajus Julius Caesar', 'Cajus Caesar'),
        ('Burkhard Hirsch (SPD)', 'Burkhard Hirsch (FDP)'),
        ('Birgit Homburger', 'Birgitt Homburger'),
        ('Birgit Hamburger', 'Birgit Homburger'),
        ('Bernhard Jadoda', 'Bernhard Jagoda'),
        (u'Barbara Hält', u'Barbara Höll'),
        (u'Barbara Hall', u'Barbara Höll'),
        ('Axel Trost', 'Axel Troost'),
        ('Annellie Buntenbach', 'Annelie Buntenbach'),
        ('Andrej Konstantin Hunko', 'Andrej Hunko'),
        (u'Andreas Lämmel', u'Andreas G. Lämmel'),
        (u'Arne Börsen', u'Arne Börnsen'),
        (u'Arne Bömsen', u'Arne Börnsen'),
        ('Amo Schmidt', 'Arno Schmidt'),
        ('Ame ', 'Arne '),
        (u'Andrea Astrid Voßhoff', u'Andrea Voßhoff'),
        (u'Achim Großmanmn', u'Achim Großmann'),
        ('Ursula Seiler-Aibring', 'Ursula Seiler-Albring'),
        (u'Rita Süßmuth', u'Rita Süssmuth'),
        (u'Rita Süßmüth', u'Rita Süssmuth'),
        (u'Katrin Göhring-Eckardt', u'Katrin Göring-Eckardt'),
        (u'Katrin Göring-Eckhardt', u'Katrin Göring-Eckardt'),
        (u'Ministerpräsident Dr. Wagner (Rheinland-Pfalz)', u'Carl-Ludwig Wagner, Ministerpräsident (Rheinland-Pfalz)'),
        (u'Vizepräsident Thierse', u'Vizepräsident Wolfgang Thierse'),
        (u'Vizepräsidentin Schmidt', u'Vizepräsidentin Renate Schmidt'),
        ('Karl-Hermann Haack', 'Karl Hermann Haack'),
        (u'Vizepräsidentin Hasselfeldt', u'Vizepräsidentin Gerda Hasselfeldt'),
        ('Burkard Hirsch', 'Burkhard Hirsch'),
        ('Burhard Hirsch', 'Burkhard Hirsch'),
        ('Burkhard Husch', 'Burkhard Hirsch'),
        (u'Alterspräsident Brandt', u'Alterspräsident Willy Brandt'),
        (u'Wolfang Gröbl', u'Wolfgang Gröbl'),
        ('Wilhelm Rave', 'Wilhelm Rawe'),
        ('Rudolf. Kraus', 'Rudolf Kraus'),
        ('Manfred Castens', 'Manfred Carstens'),
        ('KurtBodewig', 'Kurt Bodewig'),
        (u'Jürchen Echternach', u'Jürgen Echternach'),
        (u'Adam-Schwaetzer Bundesminister für Raumordnung, Bauwesen und Städtebau', u'Irmgard Schwaetzer, Bundesminister für Raumordnung, Bauwesen und Städtebau'),
        (u'Frau Geiger, Parl. Staatssekretär beim Bundesminister für wirtschaftliche Zusammenarbeit', u'Michaela Geiger, Parl. Staatssekretär beim Bundesminister für wirtschaftliche Zusammenarbeit'),
        ('LIntner', 'Lintner'),
        ('Eduard Linter', 'Eduard Lintner'),
        ('Eduard Lindtner', 'Eduard Lintner'),
        ('Bernd Schmidtbauer', 'Bernd Schmidbauer'),
        (u'Jürgen Borchert', 'Jochen Borchert'),
        ('Josef Borchert', 'Jochen Borchert'),
        ('Frau Merkel, Bundesminister', 'Angela Merkel, Bundesminister'),
        ('Frau Hasselfeldt', 'Gerda Hasselfeldt'),
        ('Frau Adam-Schwaetzer', 'Irmgard Schwaetzer'),
        ('Barbara FStolterfoht', 'Barbara Stolterfoht'),
        (u'Uwe-Jens Rudi Rössel', u'Uwe-Jens Rössel'),
        (u'Katrin Dagmar Göring-Eckardt', u'Katrin Göring-Eckardt'),
        (u'Minister Kühbacher (Brandenburg)', u'Minister Klaus-Dieter Kühbacher (Brandenburg)'),
        (u'Bernd Kränzle (Bayern), Staatssekretär', u'Bernd Kränzle, Staatssekretär (Bayern)')
        ]
        
    for a, replacement in l:
        name = name.replace(a, replacement)
    
    l_name_stubs = [('Cornelia von Teichman', 'Cornelia von Teichman und Logischen'),
    ('Christina Jantz', 'Christina Jantz-Herrmann'),
    (u'Vizepräsident Hans-Ulrich', u'Vizepräsident Hans-Ulrich Klose'),
    ('Gerda Hasselfeld', 'Gerda Hasselfeldt')]
        
    for name_stub, full_name in l_name_stubs:
        if name_stub in name and not full_name in name:
            name = ''.join([full_name, name.replace(name_stub, '')])
            break

    
    l_name_stubs = [
    (u'Blüm', u'Norbert Blüm'),
    ('Graf Lambsdorff (FDP)', 'Otto Graf Lambsdorff (FDP)'),
    ('Kohl, Bundeskanzler', 'Helmut Kohl, Bundeskanzler'),
    ('Kinkel', 'Klaus Kinkel'),
    ('Kansy', 'Dietmar Kansy'),
    ('Janzen (SPD)', 'Ulrich Janzen (SPD)'),
    ('Penner (SPD)', 'Willfried Penner (SPD)'),
    ('Stavenhagen', 'Lutz Stavenhagen'),
    ('Laufs (CDU/CSU)', 'Paul Laufs (CDU/CSU)'),
    (u'Grünewald', u'Joachim Grünewald'),
    (u'Göhner', u'Reinhard Göhner'),
    ('Lammert', 'Norbert Lammert'),
    ('Rose (CDU/CSU)', 'Klaus Rose (CDU/CSU)'),
    ('Sperling (SPD)', 'Dietrich Sperling (SPD)'),
    (u'Guttmacher (FDP)', u'Karlheinz Guttmacher (FDP)'),
    (u'Küster (SPD)', u'Uwe Küster (SPD)'),
    (u'Päselt (CDU/CSU)', u'Gerhard Päselt (CDU/CSU)'),
    ('Weng (Gerlingen) (FDP)', 'Wolfgang Weng (Gerlingen) (FDP)'),
    (u'Türk (FDP)', u'Jürgen Türk (FDP)'),
    ('Thomae (FDP)', 'Dieter Thomae (FDP)'),
    ('Thalheim (SPD)', 'Gerald Thalheim (SPD)'),
    ('Struck (SPD)', 'Peter Struck (SPD)'),
    ('Stercken (CDU/CSU)', 'Hans Stercken (CDU/CSU)'),
    ('Soell (SPD)', 'Hartmut Soell (SPD)'),
    ('Seifert (PDS/L', 'Ilja Seifert (PDS/L'),
    ('Schumann (Kroppenstedt) (PDS/Linke Liste)', 'Fritz Schumann (Kroppenstedt) (PDS/Linke Liste)'),
    ('Schmude (SPD)', u'Jürgen Schmude (SPD)'),
    (u'Rüttgers (CDU/CSU)', u'Jürgen Rüttgers (CDU/CSU)'),
    ('Pick (SPD)', 'Eckhart Pick (SPD)'),
    ('Menzel (FDP)', 'Bruno Menzel (FDP)'),
    ('Krause (Bonese) (CDU/CSU)', 'Rudolf Krause (Bonese) (CDU/CSU)'),
    ('Kolb (FDP)', 'Heinrich Kolb (FDP)'),
    ('Kohl (CDU/CSU)', 'Helmut Kohl (CDU/CSU)'),
    ('Knaape (SPD)', 'Hans-Hinrich Knaape (SPD)'),
    ('Keller (PDS/Linke Liste)', 'Dietmar Keller (PDS/Linke Liste)'),
    ('Hoyer (FDP)', 'Werner Hoyer (FDP)'),
    ('Hitschler (FDP)', 'Walter Hitschler (FDP)'),
    ('Heuer (P', 'Uwe-Jens Heuer (P'),
    ('Hirsch (FDP)', 'Burkhard Hirsch (FDP)'),
    ('Gysi (PDS', 'Gregor Gysi (PDS'),
    ('Glotz (SPD)', 'Peter Glotz (SPD)'),
    (u'Geißler (CDU/CSU)', u'Heiner Geißler (CDU/CSU)'),
    (u'Möllemann, Bundesminister für Wirtschaft', u'Jürgen Möllemann, Bundesminister für Wirtschaft'),
    (u'Möllemann (FDP)', u'Jürgen Möllemann (FDP)'), 
    (u'Schmitz (Baesweiler)', u'Hans Peter Schmitz (Baesweiler)'),
    (u'Ortleb', u'Rainer Ortleb'),
    ('Stoltenberg', 'Gerhard Stoltenberg'),
    (u'Töpfer', u'Klaus Töpfer'),
    ('Waigel', 'Theodor Waigel'),
    ('Adam-Schwaetzer', 'Irmgard  Adam-Schwaetzer'),
    (u'Solms', u'Hermann Otto Solms'),
    (u'Faltlhauser', u'Kurt Faltlhauser'),
    ('Schulz (Berlin) (B', 'Werner Schulz (Berlin) (B'),
    ('Genscher', 'Hans-Dietrich Genscher'),
    ('Gansel (SPD)', 'Norbert Gansel (SPD)'),
    (u'Kühbacher, Minister (Brandenburg)', u'Klaus-Dieter Kühbacher, Minister (Brandenburg)'),
    ('Kronenberg', 'Dieter-Julius Kronenberg'),
    ('Duve (SPD)', 'Freimut Duve (SPD)'),
    ('Fuchtel (CDU/CSU)', 'Hans-Joachim Fuchtel (CDU/CSU)'),
    ('Ganschow (FDP)', u'Jörg Ganschow (FDP)'),
    ('Geis (CDU/CSU)', 'Norbert Geis (CDU/CSU)'),
    ('Norbert Gels (CDU/CSU)', 'Norbert Geis (CDU/CSU)'),
    ('Heistermann (SPD)', 'Dieter Heistermann (SPD)'),
    ('Heyenn (SPD)', u'Günther Heyenn (SPD)'),
    ('Gysi (PDS/Linke Liste)', 'Gregor Gysi (PDS/Linke Liste)'),
    ('Hansen (FDP)', 'Dirk Hansen (FDP)'),
    (u'Dörflinger (CDU/CSU)', u'Werner Dörflinger (CDU/CSU)'),
    ('Walther (SPD)', 'Rudi Walther (SPD)'),
    ('Weis (SPD)', 'Reinhard Weis (SPD)'),
    ('Werner (Ulm) (CDU/CSU)', 'Herbert Werner (Ulm) (CDU/CSU)'),
    (u'Roth (Gießen) (CDU/CSU)', u'Adolf Roth (Gießen) (CDU/CSU)'),
    ('Roth (SPD)', 'Wolfgang Roth (SPD)'),
    ('Doss (CDU/CSU)', u'Hansjürgen Doss (CDU/CSU)'),
    ('Reschke (SPD)', 'Otto Reschke (SPD)'),
    ('Rind (FDP)', 'Hermann Rind (FDP)'),
    ('Reuschenbach (SPD)', 'Peter W. Reuschenbach (SPD)'),
    ('Rossmanith (CDU/CSU)', 'Kurt J. Rossmanith (CDU/CSU)'),
    (u'Rühe (CDU/CSU)', u'Volker Rühe (CDU/CSU)'),
    ('Sauer (Salzgitter) (CDU/CSU)', 'Helmut Sauer (Salzgitter) (CDU/CSU)'),
    (u'Schäfer (Offenburg) (SPD)', u'Harald B. Schäfer (Offenburg) (SPD)'),
    ('Schily (SPD)', 'Otto Schily (SPD)'),
    ('Schmidt (Salzgitter) (SPD)', 'Wilhelm Schmidt (Salzgitter) (SPD)'),
    ('Schreiner (SPD)', 'Ottmar Schreiner (SPD)'),
    ('Schwanitz (SPD)', 'Rolf Schwanitz (SPD)'),
    ('Schwanhold (SPD)', 'Ernst Schwanhold (SPD)'),
    ('Schwarz (CDU/CSU)', 'Stefan Schwarz (CDU/CSU)'),
    ('Seesing (CDU/CSU)', 'Heinrich Seesing (CDU/CSU)'),
    ('Singer (SPD)', 'Johannes Singer (SPD)'),
    ('Steiner (CDU/CSU)', 'Heinz-Alfred Steiner (SPD)'),
    ('Steiner (SPD)', 'Heinz-Alfred Steiner (SPD)'),
    ('Stockhausen (CDU/CSU)', 'Karl Stockhausen (CDU/CSU)'),
    ('Gallus', 'Georg Gallus'),
    ('Wimmer, Parl', 'Willy Wimmer, Parl'),
    ('Duve', 'Freimut Duve'),
    ('Seehofer', 'Horst Seehofer'),
    ('Opel (SPD)', 'Manfred Opel (SPD)'),
    ('Erler (SPD', 'Gernot Erler (SPD'),
    ('Koppelin (FDP)', u'Jürgen Koppelin (FDP)'),
    (u'Grünbeck (FDP)', u'Josef Grünbeck (FDP)'),
    (u'Nolting (FDP)', u'Günther Friedrich Nolting (FDP)'),
    ('Rixe (SPD)', u'Günter Rixe (SPD)'),
    ('Meckelburg (CDU/CSU)', 'Wolfgang Meckelburg (CDU/CSU)'),
    ('Engelmann (CDU/CSU)', 'Wolfgang Engelmann (CDU/CSU)'),
    (u'Dreßler (SPD)', u'Rudolf Dreßler (SPD)'),
    ('Conradi (SPD)', 'Peter Conradi (SPD)'),
    ('Raidel (CDU/CSU)', 'Hans Raidel (CDU/CSU)'),
    ('Zywietz (FDP)', 'Werner Zywietz (FDP)'),
    ('Wolfgramm (FDP)', 'Torsten Wolfgramm (FDP)'),
    (u'Wiefelspütz (SPD)', u'Dieter Wiefelspütz (SPD)'),
    (u'Weiß (Berlin) (Bündnis 90/GRÜNE)', u'Konrad Weiß (Berlin) (Bündnis 90/GRÜNE)'),
    ('Weis (Stendal) (SPD)', 'Reinhard Weis (Stendal) (SPD)'),
    ('Weisskirchen (Wiesloch) (SPD)', 'Gert Weisskirchen (Wiesloch) (SPD)'),
    ('Wallow (SPD)', 'Hans Wallow (SPD)'),
    ('von Larcher (SPD)', 'Detlev von Larcher (SPD)'),
    ('Vogel (Ennepetal) (CDU/CSU)', 'Friedrich Vogel (Ennepetal) (CDU/CSU)'),
    (u'Verheugen (SPD)', u'Günter Verheugen (SPD)'),
    ('Vergin (SPD)', 'Siegfried Vergin (SPD)'),
    (u'Toetemeyer (SPD)', u'Hans-Günther Toetemeyer (SPD)'),
    ('Thierse (SPD)', 'Wolfgang Thierse (SPD)'),
    ('Scharrenbroich (CDU/CSU)', 'Heribert Scharrenbroich (CDU/CSU)'),
    ('Reimann (SPD)', 'Manfred Reimann (SPD)'),
    ('Rau (CDU/CSU)', 'Rolf Rau (CDU/CSU)'),
    (u'Poppe (BÜNDNIS 90/DIE GRÜNEN)', u'Gerd Poppe (BÜNDNIS 90/DIE GRÜNEN)'),
    ('Peter Kemper (SPD)', 'Hans-Peter Kemper (SPD)'),
    ('Peter (Kassel) (SPD)', 'Horst Peter (Kassel) (SPD)'),
    ('Graf Lambsdorff (FDP)', 'Otto Graf Lambsdorff (FDP)'),
    ('Nitsch (CDU/CSU)', 'Johannes Nitsch (CDU/CSU)'),
    ('Oostergetelo (SPD)', 'Jan Oostergetelo (SPD)'),
    ('Ostertag (SPD)', 'Adolf Ostertag (SPD)'),
    (u'Müntefering (SPD)', u'Franz Müntefering (SPD)'),
    (u'Müller (Wadern) (CDU/CSU)', u'Hans-Werner Müller (Wadern) (CDU/CSU)'),
    (u'Mischnick (FDP)', u'Wolfgang Mischnick (FDP)'),
    ('Meckel (SPD)', 'Markus Meckel (SPD)'),
    (u'Lühr (FDP)', u'Uwe Lühr (FDP)'),
    (u'Lüder (FDP)', u'Wolfgang Lüder (FDP)'),
    ('Lowack (CDU/CSU)', 'Ortwin Lowack (CDU/CSU)'),
    ('Lischewski (CDU/CSU)', 'Manfred Lischewski (CDU/CSU)'),
    ('Lamers (CDU/CSU)', 'Karl Lamers (CDU/CSU)'),
    ('Kuhlwein (SPD)', 'Eckart Kuhlwein (SPD)'),
    ('Kriedner (CDU/CSU)', 'Arnulf Kriedner (CDU/CSU)'),
    ('Koschyk (CDU/CSU)', 'Hartmut Koschyk (CDU/CSU)'),
    ('Koschnick (SPD)', 'Hans Koschnick (SPD)'),
    ('Kohn (FDP)', 'Roland Kohn (FDP)'),
    ('Klose (SPD)', 'Hans-Ulrich Klose (SPD)'),
    ('Klinkert (CDU/CSU)', 'Ulrich Klinkert (CDU/CSU)'),
    ('Kleinert (Hannover) (FDP)', 'Detlef Kleinert (Hannover) (FDP)'),
    (u'Klein (München) (CDU/CSU)', u'Hans Klein (München) (CDU/CSU)'),
    ('Kalb (CDU/CSU)', u'Bartholomäus Kalb (CDU/CSU)'),
    ('Kittelmann (CDU/CSU)', 'Peter Kittelmann (CDU/CSU)'),
    ('Jagoda (CDU/CSU)', 'Bernhard Jagoda (CDU/CSU)'),
    (u'Jäger (CDU/CSU)', u'Claus Jäger (CDU/CSU)'),
    ('Irmer (FDP)', 'Ulrich Irmer (FDP)'),
    ('Gres (CDU/CSU)', 'Joachim Gres (CDU/CSU'),
    (u'Graf von Schönburg-Glauchau (CDU/CSU', u'Joachim Graf von Schönburg-Glauchau (CDU/CSU'),
    ('Glos (CDU/CSU)', 'Michael Glos (CDU/CSU)'),
    ('Gibtner (CDU/CSU)', 'Horst Gibtner (CDU/CSU)'),
    (u'Großmann (SPD)', u'Achim Großmann (SPD)'),
    ('Gerster (Mainz) (CDU/CSU)', 'Johannes Gerster (Mainz) (CDU/CSU)'),
    ('Eckart Pick', 'Eckhart Pick'),
    ('Catenhusen', 'Wolf-Michael Catenhusen'),
    (u'Büttner (Ingolstadt) (SPD)', u'Hans Büttner (Ingolstadt) (SPD)'),
    ('Eimer', 'Norbert Eimer'),
    (u'Dreßler', u'Rudolf Dreßler'),
    ('de With', 'Hans de With'),
    ('Cronenberg', 'Dieter-Julius Cronenberg'),
    ('Elmer', 'Conrad Elmer'),
    ('Feige', 'Klaus-Dieter Feige'),
    ('Eylmann', 'Horst Eylmann'),
    ('Esters', 'Helmut Esters'),
    ('Briefs', 'Ulrich Briefs'),
    ('Brecht', 'Eberhard Brecht'),
    ('Braband', 'Jutta Braband'),
    (u'Bötsch', u'Wolfgang Bötsch'),
    (u'Börnsen', u'Arne Börnsen'),
    ('Borchert (CDU/CSU)', 'Jochen Borchert (CDU/CSU)'),
    ('Bohl', 'Friedrich Bohl'),
    (u'Blüm', u'Norbert Blüm'),
    ('Blank (CDU/CSU)', 'Joseph-Theodor Blank (CDU/CSU)'),
    ('Bindig', 'Rudolf Bindig'),
    ('Bierling', 'Hans-Dirk Bierling'),
    ('Beucher', 'Friedhelm Julius Beucher'),
    (u'Bernrath', u'Hans Gottfried Bernrath'),
    ('Becker (Nienberge) (SPD)', 'Helmuth Becker (Nienberge) (SPD)'),
    ('Baum', 'Gerhart Rudolf Baum'),
    ('Bachmaier', 'Hermann Bachmaier'),
    ('Austermann', 'Dietrich Austermann'),
    ('Andres', 'Gerd Andres'),
    (u'Schäfer, Staatsminister im Auswärtigen Amt', u'Helmut Schäfer, Staatsminister im Auswärtigen Amt'),
    ('Waffenschmidt', 'Horst Waffenschmidt'),
    (u'Schmidbauer, Parl. Staatssekretär beim Bundesminister für Umwelt, Naturschutz und Reaktorsicherheit', u'Bernd Schmidbauer, Parl. Staatssekretär beim Bundesminister für Umwelt, Naturschutz und Reaktorsicherheit'),
    ('Riedel', 'Erich Riedel'),
    (u'Repnik, Parl. Staatssekretär', u'Hans-Peter Repnik, Parl. Staatssekretär'),
    ('Lintner', 'Eduard Lintner'),
    ('Kampeter', 'Steffen Kampeter'),
    ('Hintze', 'Peter Hintze'),
    ('Echternach', u'Jürgen Echternach'),
    ('Diller', 'Karl Diller'),
    (u'Carstens, Parl. Staatssekretär beim Bundesminister der Finanzen', u'Manfred Carstens, Parl. Staatssekretär beim Bundesminister der Finanzen'),
    ('Spranger', 'Carl-Dieter Spranger'),
    ('Seiters', 'Rudolf Seiters'),
    ('Riesenhuber', 'Heinz Riesenhuber'),
    (u'Krause, Bundesminister für Verkehr', u'Günther Krause, Bundesminister für Verkehr'),
    ('Freiherr von Schorlemer (CDU/CSU)', 'Reinhard Freiherr von Schorlemer (CDU/CSU)'),
    ('Kiechle', 'Ignaz Kiechle'),
    ('Ullmann (B', 'Wolfgang Ullmann (B'),
    ('Vogel (SPD)', 'Hans-Jochen Vogel (SPD)'),
    ('Dregger', 'Alfred Dregger'),
    ('Vogel (SPD)', 'Hans-Jochen Vogel'),
    ('Voigt', 'Hans-Peter Voigt'),
    ('Modrow', 'Hans Modrow'),
    ('Freiherr von Stetten (CDU/CSU)', 'Wolfgang von Stetten (CDU/CSU)'),
    (u'Schäuble, Bundesminister des Innern', 
    u'Wolfgang Schäuble, Bundesminister des Innern'),
    ('Schwarz-Schilling', 'Christian Schwarz-Schilling'),
    (u'Müller (Düsseldorf) (SPD)', u'Michael Müller (Düsseldorf) (SPD)'),
    (u'Müller (CDU/CSU)', u'Günther Müller (CDU/CSU)'),
    (u'Schmidbauer, Parl. Staatssekretär ', u'Bernd Schmidbauer, Parl. Staatssekretär '),
    (u'Riedl, Parl. Staatssekretär', u'Erich Riedl, Parl. Staatssekretär')]

    
    for name_stub, full_name in l_name_stubs:
        if name.startswith(name_stub):
            name = u''.join([full_name, name.replace(name_stub, u'')])
            break

    name = name.replace('Dr.-Ing. ', '').replace('Frau ', '')
    
    if u' Parl. Staatssekretär' in name and not u', Parl. Staatssekretär' in name:
        name = name.replace(u' Parl. Staatssekretär', u', Parl. Staatssekretär')
    
    if name.startswith('. '):
        name = name[2:]
    return name


def line_speaker_match(line, d_speaker_short_long):
    #print 0, line
    line = line.replace('>', '').replace('    ', '')
    if re.match(u'^(Staatsminister(in)?\s|Minister(in)?\s)?(Abg\[bold\]\.\s)?(von\[bold\]\s+)?[A-ZÖÜÄ][a-zöüäß\-\']{2,}([A-ZÖÜÄ][a-zöüäß\-\']{2,})?\[bold\]', line) or re.match(u'^(Staatsminister(in)?\s|Minister(in)?\s)?([DO]r(\.-Ing)?(\[bold\])?\.\s{1,}){1,}(.*\[bold\]\s)*[A-ZÖÜÄ][a-zöüäß\-\']{2,}([A-ZÖÜÄ][a-zöüäß\-\']{2,})?(\[bold\])?', line) or re.match(u'^(Staatsminister(in)?\s|Minister(in)?\s)?(Dr\[bold\]\.\s{1,}){1,}h(\[bold\])?\.\s*c\[bold\]\.\s{1,}[A-ZÖÜÄ\'][a-zäüöß\-]{2,}(\[bold\])?', line) or re.match(u'^[A-Za-z]{,6}räsident.*:\[bold\]', line) or u', Parl. Staatssekretär:' in line:
        #print 1, line
        
        if line.endswith(')') and not('(') in line:
            return False

        maybe_speaker = line.split(':')[0]
        #if maybe_speaker.count('minister') > 1:
            #return False
        if not '[bold]' in maybe_speaker and not ':[bold]' in line:
            if not u', Parl. Staatssekretär' in maybe_speaker: 
                return False
        if len(maybe_speaker.split()) < 2:
            return False
        
        if '(' in maybe_speaker and not ')' in maybe_speaker or (re.match(u'.*\d{2,}.*', maybe_speaker) and not u'(bündnis 90' in maybe_speaker.lower()):
            return False
        for i in ['mitgeteil', 'gesagt', 'zitier', 'bekannt', 'agesordnung', 'Fortsetzung', '(TA)', '(UN', '(Dr.', 'Herr ', 'Sie ', ' ich ', 'So ', ' so ', ' wissen ', ' wir ', 'Wir ', 'und der', 'sprechen ', 'Ihnen,', ' man ', '?', '!', 'Brief[bold] des[bold]', ' habe', u'Präsidentschaft[bold]', u'erklärt', u'Wachstum[bold', u'Stichwort', 'Kollege', 'dennoch', 'wahr', ' CDU/CSU', '(alle', u'Ergänzung', 'TOP', ' stellen ', 'wollen', ' sein ', ' muss ', 'Inhalt', u'Überweisung', ' rufe ', '..', 'Anlage ', 'Beratung', 'Reden ', 'Herr[bold]', ' ja', ' hierzu', 'Stellung', ' nimmt', ' hat ', ' recht', ' USA', ' ist', ' zitier', 'Wort.', u'Änderung', '(II)', '(III)', 'Berichterstattung', ' mittei', 'Zusatzp', 'als', ' eine ', ' nennen', ' durch', u' heißt', ' dies', ' frag', ' sag', ' hin ', u' überwiesen', 'ZP', 'Nachtragshaushalt', ' hat', u'„', u'Ländern', 'Privilegien', u' muß', 'Solms Landwirtschaft', 'des Senats ', 'des Bundesrates ', 'seiner', u'geäußert', '  richtigen ', 'Gegenruf', 'Abgeordneten', ' einer ', ' wird ', 'Zitat', 'anderen', ' folgt', ' sind', ' wie', ' richtigen', ' einen', 'abweicht', 'Prozent', ' nur ', 'kommenden', u'Präsidentschaft']:
            if i in maybe_speaker.replace('[bold]', ''):
                return False

        if u'ekretär' in maybe_speaker and u'räsident' in maybe_speaker:
            return False
                
        if line.count('[') > line.count('[bold]'):
            return False
        #print 22
        if re.match(u'^.{3,}\(.+\)\s*(\[bold\]\s*)*$', maybe_speaker) or ',' in maybe_speaker or u'präsiden' in maybe_speaker.lower():
            #print 3
            if maybe_speaker.count(',') > 1 and not ('minister' in maybe_speaker.lower() or u'Staatssekretär' in maybe_speaker):
                #print 5
                return False
        
            if ',' in maybe_speaker:
                last_word_maybe_speaker = maybe_speaker.split(',')[0].split()[-1]
                if last_word_maybe_speaker[0].islower():
                    #print 6
                    return False
                if maybe_speaker.count(',') == 2:
                    maybe_title = ','.join(maybe_speaker.split(',')[1:])
                else:
                    
                    maybe_title = maybe_speaker.split(',')[1]
                if maybe_title and maybe_title.strip()[0].islower():
                    return False
                
                if '[bold]' in maybe_title:
                    if re.match(u'^.{3,}\(.+\)\s*(\[bold\])?', maybe_speaker) or u'Bundeskanzler' in maybe_title or u'minister' in maybe_title.lower():
                        #print 4
                        #print maybe_title, maybe_speaker
                        pass 
                    else:
                        #print 66
                        return False
            #print 77
            if '.' in maybe_speaker and not ('Dr[bold].' in maybe_speaker or 'Dr.-Ing[bold]' in maybe_speaker or 'Abg[bold].' in maybe_speaker or 'Dr.' in maybe_speaker or 'Or[bold].' in maybe_speaker or 'Parl.' in maybe_speaker or 'Parl[bold].' in maybe_speaker):
                b = False
                for i in  string.ascii_uppercase:
                    if '%s.' % i in maybe_speaker or '%s[bold].' %i in maybe_speaker:
                        b = True
                        break
                if not b:
                    return False

            if u'Parl. Staatssekretär' in maybe_speaker and maybe_speaker.endswith(')'):
                maybe_speaker = maybe_speaker.split('(')[0]
        
            if ',' in maybe_speaker:
                for i in [u'(BÜNDNIS 90/DIE GRÜNEN)', u'(BÜNDNIS 90/DIE GRÜ- NEN)', '(CDU/CSU)', '(SPD)', '(PDS)', '(DIE LINKE)', '(FDP)']:
                    if i in maybe_speaker:
                        maybe_speaker = maybe_speaker.replace(',', '')
                        break
            maybe_speaker = maybe_speaker.replace('[bold]', '')
            
            if maybe_speaker.startswith('Minister')and re.match(u'.+\(.+\)', maybe_speaker):

                maybe_speaker = maybe_speaker.replace('Minister', '')
                state = '(' + maybe_speaker.split('(')[1]
                maybe_speaker = maybe_speaker.split(' (')[0] + ', Minister' + state
            
            elif maybe_speaker.startswith('Staatsminister') and (re.match(u'.+\(.+\)', maybe_speaker) or ',' in maybe_speaker):
                
                first_word = maybe_speaker.split()[0].replace(',', '')

                maybe_speaker = maybe_speaker.replace(first_word, '').strip()
                if '(' in maybe_speaker:
                    state = '(' + maybe_speaker.split('(')[1]
                    #print state
                else:
                    state = '(' + maybe_speaker.split(',')[1] + ')'
                maybe_speaker = maybe_speaker.split(' (')[0] + ', ' + first_word + ' ' + state
                #print state, 2
                
            maybe_speaker = repair_name(maybe_speaker)
            if ',' in maybe_speaker:
                speaker_short = maybe_speaker.split(',')[0]
                if speaker_short in d_speaker_short_long:
                    maybe_speaker = d_speaker_short_long[speaker_short]
            if 'minister' in maybe_speaker and '(' in maybe_speaker and maybe_speaker.endswith(')') and not 'Staatsminister' in maybe_speaker:
                maybe_speaker = maybe_speaker.replace(' (', ', ')[:-1]
            return maybe_speaker.strip()
    
    return False
    
#print line_speaker_match(u'>Dr[bold]. Bertram[bold] Wieczorek[bold], Parl. Staatssekretär für Umwelt, Naturschutz und Reaktorsicherheit: Herr', {})

    

def mark_speakers(l_lines, pdf_name):
    l_no_bold_pdf = ['14192.pdf', '14169.pdf']
    index = 0
    l_lines_out = []
    d_speaker_short_long = {}
    
    
    while True:
        extra_index = False
        try:
            line = l_lines[index]
        except IndexError:
            break
        
        if line.endswith('.') and (not line.endswith('Parl.') and not line.endswith('Dr.')):
            index += 1
            l_lines_out.append(line)
            continue
        speaker = False
        line = line.replace('>', '').replace('    ', '')
        line = ' '.join(line.split())
        l_lines_out.append(line)
        if (re.match(u'^[A-ZÜÖÄ\'].+', line) or line.startswith('von')) and not line.startswith('('):

            if ':' in line:
                try: 
                    line_before = l_lines[index-1]
                    next_line = l_lines[index+1]
                    next_line_2 = l_lines[index+2]
                    
                    if (line_before.startswith('(') and not line_before.endswith(')')) or (next_line.endswith(')') and not next_line.startswith('(')) or (next_line_2.endswith(')') and not next_line.startswith('(')):
                        l_lines_out.append(line)
                        index += 1
                        continue
                    
                except IndexError:
                    pass
                speaker = line_speaker_match(line, d_speaker_short_long)
                if not speaker and pdf_name in l_no_bold_pdf:
                    speaker = no_bold_line_speaker_match(line, d_speaker_short_long)
                    
                if speaker:
                    if ',' in speaker:
                        speaker_short = speaker.split(',')[0]
                        if not speaker_short in d_speaker_short_long:
                            d_speaker_short_long[speaker_short] = speaker
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

                    if not line_speaker_match(next_line, d_speaker_short_long):
                        if pdf_name in l_no_bold_pdf:
                            if no_bold_line_speaker_match(next_line, d_speaker_short_long):
                                pass
                            else:
                                speaker = no_bold_line_speaker_match(combined_line,d_speaker_short_long)
                        else:
                            speaker = line_speaker_match(combined_line, d_speaker_short_long)

                    else:

                        speaker = False
                    if speaker:
                        
                        if ',' in speaker:
                            speaker_short = speaker.split(',')[0]
                            if not speaker_short in d_speaker_short_long:
                                d_speaker_short_long[speaker_short] = speaker
                        
                        text = combined_line.split(':')[1]
                        l_lines_out[-1] = ''.join(['|speaker', speaker, '|', text])
                        if extra_index:
                            index +=3
                        else:
                            index += 2
                        continue
                        
        if not speaker:
            #print 19
            if (u', Bundeskanzler' in line and u'(' in line) or u'Staatssekretär' in line or 'inister' in line:
                next_line_3 = ''
                #print 77
                try:
                    next_line = l_lines[index + 1].replace('>', '').replace('    ', '')
                    next_line_2 = l_lines[index + 2].replace('>', '').replace('    ', '')
                    next_line_3 = l_lines[index + 3].replace('>', '').replace('    ', '')
                except IndexError:
                    pass
                    
                next_line = ' '.join(next_line.split())
                next_line_2 = ' '.join(next_line_2.split())
                next_line_3 = ' '.join(next_line_3.split())
                combined_line = ' '.join([line, next_line, next_line_2])
                if '):' in next_line_2:
                    combined_line = combined_line.split('(')[0].strip() + combined_line.split(')')[1].strip() + ':'
                    if pdf_name in l_no_bold_pdf:
                            speaker = no_bold_line_speaker_match(combined_line, d_speaker_short_long)
                    else:
                        speaker = line_speaker_match(combined_line, d_speaker_short_long)
                elif ':' in next_line_2:
                    #print line, 5, combined_line
                    #print ' '.join([next_line, next_line_2]), 999
                    speaker = line_speaker_match(combined_line, d_speaker_short_long)
                    
                    if line_speaker_match(' '.join([next_line, next_line_2]).strip(), d_speaker_short_long):
                        #print 66666
                        speaker = False
                        index += 1
                        continue
                    #print speaker
                        
                if speaker and ':' in combined_line:
                    
                    if ',' in speaker:
                        speaker_short = speaker.split(',')[0]
                        if not speaker_short in d_speaker_short_long:
                            d_speaker_short_long[speaker_short] = speaker
                        
                    text = combined_line.split(':')[1].strip()
                    l_lines_out[-1] = ''.join(['|speaker', speaker, '|', text])

                    index += 3
                    continue
                elif ':' in next_line_3 and not line_speaker_match(next_line_3, d_speaker_short_long):
                    #print 5
                    four_combined_lines = ' '.join([line, next_line, next_line_2, next_line_3])
                    three_combined_lines = ' '.join([next_line, next_line_2, next_line_3]).strip()
                    
                    if line_speaker_match(three_combined_lines, d_speaker_short_long):
                        #print 7777
                        index += 1
                        continue
                    #print three_combined_lines, 3
                    speaker = line_speaker_match(four_combined_lines, d_speaker_short_long)
                    if speaker:
                        
                        if ',' in speaker:
                            speaker_short = speaker.split(',')[0]
                            if not speaker_short in d_speaker_short_long:
                                d_speaker_short_long[speaker_short] = speaker
                        
                        text = four_combined_lines.split(':')[1].strip()
                        l_lines_out[-1] = ''.join(['|speaker', speaker, '|', text])
                        #print speaker
                        index += 4
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


#l_lines = ['Dr. Carola Reimann', 'und darzustellen?', '', u'Bundesminister des Innern, Herr Seiters.', '', u'>Dr[bold]. Ullmann[bold] (Bündnis 90/GRÜNE): Meinen Sie, daß', u'Präsidentin! Meine Da', 'kjhkjh kjkj', 'uuz']
#print mark_speakers(l_lines, '19169.pdf')


def clean_lines(l_lines):

    l_lines = [re.sub(u'\([A-Z]\)', u'', line)  for line in l_lines]
    l_lines = [line.replace(u'(cid:228)', u'ä') for line in l_lines]
    l_lines = [line.replace(u'(cid:252)', u'ü').replace(u'(cid:223)', u'ß').replace(u'(cid:150)', u'–').replace(u'(cid:220)', u'Ü').replace(u'(cid:246)', u'ö').replace(u'(cid:132)', u'„').replace(u'(cid:147)', u'“').replace(u'(cid:133)', u'...').replace(u'(cid:214)', u'Ö').replace(u'(cid:146)', u"'").replace(u'(cid:240)', u'ğ') for line in l_lines]

    for index, line in enumerate(l_lines):
        while '--' in l_lines[index]:
            l_lines[index] = l_lines[index].replace('--', '-')
    
    l_lines = [' '.join([word.strip() for word in line.split()]) for line in l_lines]
    
    l_lines = [line.replace(',,', ',').replace(">'", ">").replace(u'    —', '    ').replace(u'President', u'Präsident'). replace(u'>Präsident Dr[bold].', u'>Präsident[bold] Dr[bold].').replace(');', '),').replace('{', '(').replace(' :', ':').replace(' .', '.').replace('(F.D.P.)', '(FDP)').replace(' rt', 'rt').replace(' tt', 'tt').replace('Parl:', 'Parl.').replace('): ):', '):').replace(u' und -', u' und ').replace('K r', 'Kr').replace(',)', '.)').replace('Sch ', 'Sch').replace(' rl', 'rl').replace('Pari. Staatsse', u'Parl. Staatsse').replace(', Pari.', ', Parl.').replace(' rz', 'rz').replace(' rf', 'rf').replace(' lr', 'Ir').replace(' rl', 'rl').replace('F. D. P.', 'FDP').replace('Sch ', 'Sch').replace('sCh', 'sch').replace(' ria ', 'ria ').replace('gI', 'gi').replace(' ft', 'ft').replace(' rz', 'rz').replace(' rr', 'rr').replace('CDUCSU', 'CDU/CSU').replace('CDU/-CSU', 'CDU/CSU').replace('CDU/CDU', 'CDU/CSU').replace(' rich ', 'rich ').replace('( ', '(').replace(' )', ')').replace('Frauen - und Jugend', 'Frauen und Jugend') for line in l_lines]

    von_start = False
    l_lines2 = []
    for index, line in enumerate(l_lines):

        if von_start == True and 'ordneten' in line and not u'üßt):' in line:
            continue
        if (u'(von Abge' in line or '(mit' in line) and u'üßt):' in line:
            line = line.split(u'(von Abge')[0].split('(mit')[0] + u':' + line.split(u'üßt):')[1]
            try:
                #print l_lines2[-1], line, 4
                if not l_lines2[-1]:
                    #print 7
                    l_lines2.pop()
            except IndexError:
                pass
        elif (u'(von der' in line  or '(mit' in line) and u'üßt):' in line:
            line = line.split(u'(von der')[0].split('(mit')[0] + u':' + line.split(u'üßt):')[1]
            try:
               # print l_lines2[-1], line, 4
                if not l_lines2[-1]:
                    #print 7
                    l_lines2.pop()
            except IndexError:
                pass
        elif u'(von Abge' in line:
            line = line.split(u'(von Abge')[0]
        elif u'(von der' in line:
            #print line, 88
            line = line.split(u'(von der')[0]
            #print line
        elif u'(von[bold] der' in line:
            line = line.split('(von[bold] der')[0]
        elif '(mit' in line:
            line = line.split('(mit')[0]
        elif u'üßt):' in line:
            line = u':' + line.split(u'üßt):')[1]
            von_start = False
            try:
                #print l_lines2[-1], 6
                if not l_lines2[-1] or (u'Beifall' in l_lines2[index-1] and not '(mit' in l_lines2[index-1]):
                    #print 7
                    l_lines2.pop()
            except IndexError:
                pass
        elif u'üßt)[bold]:' in line:
            line = u':' + line.split(u'üßt)[bold]:')[1]
            try:
                #print l_lines2[-1], 6
                if not l_lines2[-1] or (u'Beifall' in l_lines2[index-1] and (not '(mit' in l_lines2[index-1] and not l_lines2[index-1].startswith('(Beifall'))):
                    #print 7
                    l_lines2.pop()
                    von_start = False
            except IndexError:
                pass
        elif re.match(u'.*Zurufe von der .+\):.*', line):
            #print line, 5
            line = u':' + line.split(u'):')[1]
            #print line
        
        elif re.match(u'\(Zurufe von der .+\)', line):
            #print line, 5
            line = ''
            #print line        
            
        elif '(von' in line:
            #print line, 77
            line = line.split('(von')[0]
            von_start = True
                    
                 
        l_lines2.append(line)
            
    
    return l_lines2

#l_lines = [u'Riester das Wort.', '', u'>Walter[bold] Riester[bold], Bundesminister für Arbeit und', u'Sozialordnung (von der SPD sowie von Abgeordneten des', u'BÜNDNISSES 90/DIE GRÜNEN mit Beifall begrüßt):', u'Herr Präsident! Meine sehr verehrten Damen und Herren!', u'Herr Abgeordneter  Weiß,  ich  weiß  nicht  genau,  gegen']

#print clean_lines(l_lines)
    
    
def clean_lines_2(l_lines):
    
    l_lines = [line.replace('(', ' (') for line in l_lines]
    
    l_lines = [line.replace(' :', ':').replace('[bold]', '').replace(u'GRÜ- NEN', u'GRÜNEN').replace('- ', '-').replace('-und ', '- und ').replace('-oder ', '- oder ').replace('/ ', '/').replace('F.D.P.', 'FDP').replace('F.D.P', 'FDP').replace('CDU/CDU', 'CDU/CSU').replace('>', '') for line in l_lines]
    
    l_replacement_tuples = [
        ('Bundes-republik', 'Bundesrepublik'),
        ('epu-blik', 'epublik'),
        (u'RenØ', u'René'),
        ('Bri-gitte', 'Brigitte'),
        (' Li-ste', ' Liste'),
        (u'Außenund ', u'Außen- und '),
        ('Kri-stin ', 'Kristin '),
        ('Hart-mann', 'Hartmann'),
        ('Buenos Ai-res', 'Buenos Aires'),
        (u'Djindjic', u'Djindjić'),
        (u'Kurnaz', u'Kurnaź'),
        (' Len-kert', ' Lenkert'),
        (' Hau-er', ' Hauer'),
        ('Dagdelen', u'Dağdelen'),
        (u'Dagğelen', u'Dağdelen'),
        (u'Da_delen', u'Dağdelen'),
        ('Abu Ghureib', 'Abu Ghraib'),
        ('Abu Ghuraib', 'Abu Ghraib'),
        (' get r', ' getr'),
        ('Mate rial', 'Material'),
        ('Iund', 'I und'),
        ('grafi', 'graphi'),
        ('kleine Anfrage', 'Kleine Anfrage'),
        ('Ir an ', 'Iran '),
        (' lich ', 'lich '),
        ('( ', '('),
        (' )', ')'),
        ('Nato ', 'NATO ')]
    
    for index, line in enumerate(l_lines):
        l_lines[index] = line.replace(u'In nern', u'Innern').replace(u'Bundes kanzler', u'Bundeskanzler').replace(u'Bun des', u'Bundes').replace(u'Bun- d', u'Bund').replace(u'Bundes- m', u'Bundesm').replace(u'Finan- zen', u'Finanzen').replace(u'Um- welt', u'Umwelt').replace(u'Ver- braucher', u'Verbraucher').replace(u'In- nern', u'Innern').replace(u'Bundes- ka', u'Bundeska').replace(' .', '.').replace('Ab schiebung', 'Abschiebung').replace(u'\xad ', '').replace(u'\xad', '-').replace(u'˜nderung', u'Änderung').replace(u'BÜND-NIS', u'BÜNDNIS').replace('Bundesministererin', 'Bundesministerin').replace('Fami lie', 'Familie').replace('B Bundesminister der u d n', 'Bundesminister der').replace('B u d ', '').replace(' ll', 'll').replace('Ge rich', 'Gerich').replace(' -schaft', 'schaft').replace('tt hias', 'tthias').replace('W irt', 'Wirt').replace('Bun-des', 'Bundes').replace('SchmI', 'Schmi').replace(' rn', 'rn').replace(' i m ', ' im ').replace(u'Auswärtigen -Amt', u'Auswärtigen Amt').replace(' tion', 'tion').replace(' ff', 'ff').replace('Annelle', 'Annellie').replace(u'Cern Özdemir', u'Cem Özdemir').replace(u'Asylkompromifi', u'Asylkompromiß').replace('. und', ' und').replace(',.', ', ').replace(u'-für ', u' für ').replace(' und -', ' und ').replace(' g ', ' ').replace('..', '.').replace('[', '(').replace(']', ')').replace('Bu ry', 'Bury').replace('Hans Josef', 'Hans-Josef').replace('Hans-Martin', 'Hans Martin').replace('Hans Eberhard', 'Hans-Eberhard').replace('Kurt. J. Rossmanith', 'Kurt J. Rossmanith').replace(u'Städ tebau', u'Städtebau').replace('Otty Schily', 'Otto Schily').replace('Lo re ', 'Lore').replace('Wolf gang', 'Wolfgang').replace('Ing rid',
        'Ingrid').replace('Harmut', 'Hartmut').replace('Bundes minister', 'Bundesminister').replace(u'Reak torsicherheit', u'Reaktorsicherheit').replace('Bundes--min', 'Bundesmin').replace('Bundesmi nis', 'Bundesminis').replace(' schaft', 'schaft').replace('Fi-nanz', 'Finanz').replace('Wort-meldung', 'Wortmeldung').replace('Ra-', 'Ra').replace('Parl.S', 'Parl. S').replace('ministser', 'minister').replace('al-Qaida', 'Al-Qaida')
        
        for word, replacement in l_replacement_tuples:
            l_lines[index] = l_lines[index].replace(word, replacement)
        
        l_lines[index] = re.sub(u'(\s)(\-\w+)', lambda x: x.groups()[1], l_lines[index]) 
        
        l_lines[index] = re.sub(u'(\s[A-Z])(\s)', lambda x: x.groups()[0], l_lines[index])
        
        l_lines[index] = re.sub(u'(Nato)([\s:.,\)])', lambda x: x.groups()[0].upper() + x.groups()[1], l_lines[index]) 
    
    l_lines = [u' '.join(line.split()) for line in l_lines]
    
    return l_lines
    
#print clean_lines_2(['Ir an hjkjhk', 'Nato jljlkj', 'hjhgNato.'])
    
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
                #print line
                next_line = l_lines[index + 1]
                combined_line = ' '.join([line, next_line])
                #print combined_line
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
        if page_header and len(line) > 100:
            page_header = False
            continue
        if page_header:
            #print line, 1
            if not line or re.match(u'[1-90]+', line):
                
                continue
            elif (',' in line or '(' in line or '.' in line) and not ('Berlin,' in line or 'Bonn,' in line):
                #print 2, line
                try:
                    if l_lines_in[index].startswith('('):
                        combi_line = ''
                    else:
                        combi_line = ' '.join([line, l_lines_in[index]])
                except IndexError:
                    combi_line = ''
                #if 'Bertram' in combi_line:
                    #print 99999, combi_line
                if ':' in combi_line and line_speaker_match(combi_line, {}): #and not line_speaker_match(line, {}):
                    #print 77777, line
                    l_lines_out.append('')
                    l_lines_out.append(line)
                    
                page_header = False
            elif re.match(u'.*Deutscher.*Bundestag.*Wahlperiode.*Sitzung.*[1-90]{4}.*', line):
                #print line, 3
                continue
            else:
                #print line, 4
                if line[0] == '>': 
                    l_lines_out.append('')
                    l_lines_out.append(line)
                page_header = False
                #print 6, line
                continue
        else:  
            #print 5, line      
            if l_lines_out[-1] and line.startswith('>'):
                l_lines_out.append('')
            l_lines_out.append(line)
            
    return l_lines_out


#l_lines = [u'|page10|', '', 'Deutscher Bundestag – 17. Wahlperiode – 24. Sitzung. Berlin, Donnerstag, den 25. Februar 2010', 'Präsident[bold] Dr[bold]. Norbert[bold] Lammert[bold]', 'Überweisungsvorschlag:', 'Ausschuss für wirtschaftliche Zusammenarbeit und', 'Entwicklung (f)', 'Auswärtiger Ausschuss', 'Ausschuss für Menschenrechte und Humanitäre Hilfe', 'Haushaltsausschuss', '>b) Beratung des Antrags der Abgeordneten Thilo']

#print take_out_page_headers(l_lines)

def add_date(l_lines):
    
    l_months = ['', 'Januar', 'Februar', u'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']
    
    for line in l_lines:
        if re.match(u'.*Deutscher.*Bundestag.*Wahlperiode.*Sitzung.*(Berlin|Bonn).*den.*[1-90]{4}.*', line):
            raw_date = line.split('den')[-1].replace('[bold]', '').replace('.', '')
            day, month, year = raw_date.split()
            month = str(l_months.index(month)).zfill(2)
            try:
                date = '/'.join([year, month, day])
            except ValueError:
                continue
            
            return date
        elif re.match(u'.*(Berlin|Bonn).*,.*,\s+den.*[1-90]{4}.*', line):
            # print line, 9
            raw_date = line.split('den')[-1].replace('[bold]', '').replace('.', '')
            try:
                day, month, year = raw_date.split()
                month = str(l_months.index(month)).zfill(2)
                date = '/'.join([year, month, day])
            except ValueError:
                continue
            return date
            

    print 'no date found'
       
# print add_date(l_lines)
            
def cut_end(l_lines):
    #print len(l_lines), 'len uncut'

    cut_lines = []
    before_end = False
    
    for line in l_lines[::-1]:
        #if 'Auf der Basis dieser Defintion' in line:
            #print 777
        #if line.startswith('(Schluss'):
            #print 777
        if not before_end and (re.match(u'.*Die\sSitzung\sist\sgeschlossen\.', line) or re.match(u'.*\(Schlu(ss|ß).*(:|\.).*Uhr.*\).*', line)) or u'w(cid:252)rfe auf den Drucksachen 14/5345 und 14/6718 an die' in line:# letzte Bedingung wegen fehlendemm ende von 14192.pdf
            #print line, 99
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
        elif line.count('|') == 4 and '||' in line and '|page' in line and line.endswith('|'):
            line = '|' + line.split('|')[3] + '|'
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
        if line and line[-1] not in '.:?!|)' and not 'usschuss' in line and not line.endswith(')[bold]'):
            line_not_finished = True
            try:
                next_line = l_lines[index + 1]
                if next_line[0] in '123456789' or (len(line) > 9 and line[1] == ')'):
                    line_not_finished = False
            except IndexError:
                pass
            
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
    page = False
    for line in l_lines:
        page_str = re.findall(u'\|page\d+\|', line)

        if page_str:
            page = str(int(page_str[0].split('e')[1][:-1]) - 1)
            break
    
    l_new_lines = []#'|page%s|' % prev_page]
    
    for line in l_lines:
        
        page_str = re.findall(u'\|page\d+\|', line)
        if page_str:
            #print 7
            page = str(int(page_str[0].split('e')[1][:-1]))
            line = re.sub(u'\|page\d+\|', u'', line)
        if not page:
            page = str(1)
        if line:
            #print 5
            line = ''.join([line, '+page', page])
        #print line
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
    #print xml_path, 1
    if not os.path.exists(xml_path):
        #print 2
        bash_command = 'pdf2txt.py -o %s -t xml %s' %(xml_path, pdf_path)
        print xml_path, 'xml path'
        #print bash_command
        os.system(bash_command)
        
    l_lines = general_ordering(xml_path)
    
    #print len(l_lines), 1
    l_lines = cut_end(l_lines)
    #for line in l_lines:
    #    if u'Dann brauchen Sie sich nicht zu wundern, dass es inzwi' in line:
    #        print 5555
    #        break
    l_lines = correct_split_words(l_lines)
    #print len(l_lines), 2
    
    
    l_lines = clean_lines(l_lines)

    date = add_date(l_lines)
    #print date
    #print len(l_lines), 3

    l_lines = take_out_page_headers(l_lines)
    #print len(l_lines), 4
    l_lines = correct_split_words(l_lines)
    
    #print len(l_lines), 5
    l_lines = repair_faulty_lines(pdf_name, l_lines)
    #print len(l_lines), 6, pdf_name
    l_lines = delete_useless_empty_lines(l_lines)
    #print len(l_lines), 7
    l_lines = mark_speakers(l_lines, pdf_name)
    
    #print len(l_lines), 8
    l_lines = cut_beginning(l_lines)
    #print len(l_lines), 9
    
    l_lines = unite_lines(l_lines)
    #print len(l_lines), 10
    l_lines = take_out_interruptions(l_lines)
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
    
    
    output_dir = os.path.dirname(output_path)
    #print local_dir
    if os.path.exists(output_dir) == False:
        os.makedirs(output_dir)
    list_to_file(l_lines, output_path)
    return True
        

#transform_pdf('13009.pdf')


def transform_wahlperiode(wahlperiode):
    
    wahlperioden_dir = '/'.join([project_directory.split('/federal')[0], 'app', 'pdfs', 'plenarprotokolle', wahlperiode])
    
    l_pdf_names = sorted([f for f in listdir(wahlperioden_dir)])
    
    for pdf_name in l_pdf_names[175:]:
        transform_pdf(pdf_name)
        print
        
#transform_wahlperiode('12')
