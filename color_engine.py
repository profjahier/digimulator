# Thomas Lécluse

import tkinter as tk
from assemble import Assemble
import re

# tags
KEYWORDS_TAG = "KEYWORD"
COMMENTS_TAG = "COMMENT"
INTEGERS_TAG = "INTEGER"
LABELS_TAG = "LABEL"
DIRECTIVES_TAG = "DIRECTIVE"


# --- CONFIGURATION ---
def configure(text_field):
    """
    Configures the text field by adding the reserved words as tags to it

    :param text_field: main text edition field
    """

    text_field.tag_configure(KEYWORDS_TAG, foreground="lightblue")
    text_field.tag_configure(COMMENTS_TAG, foreground="grey")
    text_field.tag_configure(INTEGERS_TAG, foreground="lightgreen")
    text_field.tag_configure(LABELS_TAG, foreground="orange")
    text_field.tag_configure(DIRECTIVES_TAG, foreground="#d99afd")


# --- KEYWORDS methods ---
def get_tag_indexes(text):
    """
    Searches and marks all the found keywords in the specified line

    :param text: text to search
    :return: all the found keywords indexes
    :rtype: list(tuple)
    """
    keywords_list = []

    for k in Assemble("").get_keywords():
        keywords_list += [(m.start(), len(k)) for m in re.finditer(r'(\b%s\b)' % k, text.lower())]

    return keywords_list


# --- COMMENTS methods ---
def tag_as_comment(text_field, line_nb, idx_start):
    """
    Tags the text from the given index until the end of the specified line as a comment

    :param text_field: main text edition field
    :param line_nb: line number
    :param idx_start: begin index
    """
    begin = str(line_nb) + "." + str(idx_start)
    end = str(line_nb) + ".end"
    text_field.tag_add(COMMENTS_TAG, begin, end)


def get_comment_index(text):
    """
    Searches for a comment in the given string.

    :param text: text to search
    :return: index of the comment block start
    :rtype: int
    """
    return text.find("//")


# --- INTEGERS methods ---
def get_int_indexes(text):
    """
    Searches and marks all the found integers in the specified line, except in comments

    :param text: text to search
    :return: all the found integers indexes
    :rtype: list(tuple)
    """
    return [(m.start(), m.end()-m.start()) for m in re.finditer(r'(?i)(\b(0b|0x)?[0-9]+\b)', text.split("//")[0])]


# --- LABELS methods ---
def get_label_index(text):
    """
    Searches for a label in the given string.

    :param text: text to search
    :return: all the found labels
    :rtype: list(tuple)
    """
    # First possibility is the label declaration with ':'
    label_declaration = [(m.start(), m.end() - m.start()) for m in re.finditer(r'(^\s*:\w+)', text)]
    if len(label_declaration) > 0:
        return label_declaration

    # Second possibility is the reference to a previously declared label
    return []  # TODO


# --- DIRECTIVES methods ---
def get_directives_indexes(text):
    """
    Searches for directives in the given string (directives can either be %data or %define)

    :param text: text to search
    :return: all the found directives
    :rtype: list(tuple)
    """
    # There can only be one directive per line.
    return [(m.start(), m.end() - m.start()) for m in re.finditer(r'(?i)(^\s*%define\b|^\s*%data\b)', text)]


# --- Main methods ---
def tag_as(text_field, line_nb, idx_start, count, tag):
    """
    Given a line number and indexes in this line, marks the region with the given tag

    :param text_field: main text edition field
    :param line_nb: line number
    :param idx_start: begin index
    :param count: number of characters to tag from begin index
    :param tag: tag to use
    """
    begin = str(line_nb) + "." + str(idx_start)
    end = begin + "+" + str(count) + "c"

    text_field.tag_add(tag, begin, end)


def update_current_line(text_field):
    """
    Updates the currently edited line

    :param text_field: main text edition field
    """
    line_begin = text_field.index("insert").split(".")[0] + ".0"
    line_end = text_field.index("insert").split(".")[0] + ".end"

    # Removes the current line tags in order to update them
    clear_all_tags(text_field, line_begin, line_end)

    # Calls the update of all categories on the line
    update_line_colors(text_field, line_begin.split(".")[0], text_field.get(line_begin, line_end))


def update_line_colors(text_field, line_nb, line_text):
    """
    Performs all the colors updates on the specified line

    :param text_field: main text edition field
    :param line_nb: line number
    :param line_text: line text
    """
    # Identify labels
    for i, c in get_label_index(line_text):
        tag_as(text_field, line_nb, i, c, LABELS_TAG)

    # Mark all tags
    for i, c in get_tag_indexes(line_text):
        tag_as(text_field, line_nb, i, c, KEYWORDS_TAG)

    # Mark integers
    for i, c in get_int_indexes(line_text):
        tag_as(text_field, line_nb, i, c, INTEGERS_TAG)

    # Mark directives
    for i, c in get_directives_indexes(line_text):
        tag_as(text_field, line_nb, i, c, DIRECTIVES_TAG)

    # Check if the line as a comment, and marks it if so
    comment_index = get_comment_index(line_text)
    if comment_index >= 0:
        tag_as_comment(text_field, line_nb, comment_index)


def clear_all_tags(text_field, start, end):
    """
    Clears all the tags between the given indexes

    :param text_field: main text edition field
    :param start: begin index
    :param end: end index
    """
    text_field.tag_remove(KEYWORDS_TAG, start, end)
    text_field.tag_remove(INTEGERS_TAG, start, end)
    text_field.tag_remove(COMMENTS_TAG, start, end)
    text_field.tag_remove(LABELS_TAG, start, end)
    text_field.tag_remove(DIRECTIVES_TAG, start, end)


def format_all(text_field):
    """
    Performs a complete update on all the document's content

    :param text_field: main text edition field
    """
    start = "1.0"
    end = "end"

    # Clears the existing document
    clear_all_tags(text_field, start, end)

    # Iterates over each line
    line_nb = 0
    for line in text_field.get(start, end).split("\n"):
        line_nb += 1

        update_line_colors(text_field, line_nb, line)
