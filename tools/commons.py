# -*- coding: utf-8 -*


def clean_text(text):
    clean_text = ''.join([letter for letter in text if letter and letter.isalpha()]).strip()
    clean_text = u' '.join(clean_text.split())
    return clean_text

def clean_text_add_spaces(text):
    clean_text = text.replace(u' ', ' ').replace('|', ' ')
    clean_text = ''.join([letter for letter in clean_text if letter and letter.isalpha() or letter in ' -']).strip()
    clean_text = u' '.join(clean_text.split())
    clean_text = ''.join([' ', clean_text, ' '])
    return clean_text

def l_of_words(text):
    clean_text = text.replace(u' ', ' ').replace('|', ' ')
    clean_text = ''.join([letter for letter in clean_text if letter and letter.isalpha() or letter in ' -']).strip()
    return clean_text.split()