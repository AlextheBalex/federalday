# -*- coding: utf-8 -*


def simple_dictionary(file_name):
    file_path = '/home/foritisiemperor/Music/transform_pdf/federalday/tools/data/%s' % file_name
    d = {}
    with open(file_path, 'r') as the_file:
        f = the_file.read().decode('utf-8')
        l_entries = f.split('\n')
        for entry in l_entries:
            try:
                l_entry = entry.split(' :: ')
                value = l_entry[0]
                key = l_entry[1]
                d[value] = key
            except IndexError:
                continue
    return d


def multi_option_dictionary(file_name):
    file_path = '/home/foritisiemperor/Music/transform_pdf/federalday/tools/data/%s' % file_name
    d = {}
    with open(file_path, 'r') as the_file:
        f = the_file.read().decode('utf-8')
        l_entries = f.split('\n')
        for entry in l_entries:
            l_entry = entry.split(' :: ')
            short_name = l_entry[0]
            try:
                full_name = l_entry[1]
            except IndexError:
                continue
            if short_name in d:
                if type(d[short_name]) == list:
                    d[short_name].append(full_name)
                else:
                    d[short_name] = [d[short_name], full_name]
            else:
                d[short_name] = full_name
    return d


def multi_option_dictionary_v_always_l(file_name):
    file_path = u'/home/foritisiemperor/Music/transform_pdf/federalday/tools/data/{0:s}'.format(file_name)
    d = {}
    with open(file_path, 'r') as the_file:
        f = the_file.read().decode('utf-8')
        l_entries = f.split('\n')
        for entry in l_entries:

            l_entry = entry.split(' :: ')
            short_name = l_entry[0]
            try:
                full_name = l_entry[1]
            except IndexError:
                continue
            if short_name in d:
                d[short_name].append(full_name)
            else:
                d[short_name] = [full_name]

    return d
