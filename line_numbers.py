# Thomas Lécluse
# digirule 2A simulator
# Licence GNU General Public License v3.0

import tkinter as tk


class LineNumberCanvas(tk.Canvas):
    def __init__(self, text_field, *args, **kwargs):
        """
        Widget managing display of line numbers next to the text editor.

        :param text_field: text editor
        :param args:
        :param kwargs:
        """
        tk.Canvas.__init__(self, *args, **kwargs)
        self.text_widget = text_field

        for key in ("<MouseWheel>", "<ButtonRelease-1>", "<Motion>"):
            self.text_widget.bind(key, self.re_render)

    def re_render(self, event=None):
        """
        Re-render the line canvas
        """
        self.delete('all')  # To prevent drawing over the previous canvas

        temp = self.text_widget.index("@0,0")  # Start at the beginning
        while True:
            dline = self.text_widget.dlineinfo(temp)
            if dline is None:
                break
            y = dline[1]

            self.create_text(2, y, anchor="nw", text=str(temp).split(".")[0])

            temp = self.text_widget.index("%s+1line" % temp)
