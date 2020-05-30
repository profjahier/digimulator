# Thomas Lécluse
# digirule 2A simulator
# Licence GNU General Public License v3.0

import tkinter as tk


class LineNumberWidget(tk.Text):
    def __init__(self, text_field, *args, **kwargs):
        """
        Widget managing display of line numbers next to the text editor.

        :param text_field: text editor
        :param args:
        :param kwargs:
        """
        tk.Text.__init__(self, *args, **kwargs)
        self.text_widget = text_field
        self.prev_posi = None

    def re_render(self, event=None):
        """
        Re-render the line canvas
        """
        self.config(state="normal")  # Authorize edition
        self.delete('1.0', 'end')  # To prevent drawing over the previous canvas

        nb_of_lines = len(self.text_widget.get('1.0', 'end').split("\n"))

        for line_nb in range(nb_of_lines - 1):  # Starts at 0, so we add one when display
            self.insert("end", str(line_nb + 1) + "\n")

        self.delete(str(nb_of_lines) + ".0", 'end')  # remove the last \n
        self.config(state="disabled")  # Disable edition
