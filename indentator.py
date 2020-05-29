# Thomas Lécluse
# digirule 2A simulator
# Licence GNU General Public License v3.0

import re


def indent(text_field):
    """
    Performs the indent operation on the cursors' position

    :param text_field: text widget
    """
    indent_size = 4  # number of blank spaces to add if a new indent is to be made

    # Get the previous line content
    line_nb = int(text_field.index("insert").split(".")[0])
    if line_nb > 1:
        old_line_nb = line_nb - 1
    else:
        old_line_nb = 1

    old_line_text = text_field.get(str(old_line_nb) + ".0", str(old_line_nb) + ".end")

    # First case: old line leads with a label --> new indentation (added to previous indentation)
    if leads_with_label(old_line_text):
        text_field.insert("insert", (get_leading_space(old_line_text) + indent_size) * " ")
    else:  # Second case: regular return, we add the same indentation as above
        text_field.insert("insert", get_leading_space(old_line_text) * " ")


def get_leading_space(text):
    """
    Gets the number of leading whitespaces of the previous line
    :param text: text to analyze
    :return: number of leading blank spaces
    :rtype: int
    """
    return [(m.start(), m.end() - m.start()) for m in re.finditer(r'^\s*', text)][0][1]


def leads_with_label(text):
    """
    Checks if the specified texts starts with a leading label.

    :param text: text to analyze
    :return: True if a label leads the line
    :rtype: bool
    """
    return len([(m.start(), m.end() - m.start()) for m in re.finditer(r'(^\s*:\w+)', text)]) > 0
