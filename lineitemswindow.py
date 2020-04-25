# Copyright (c) Anand Krishnamoorthi
# Licensed under the MIT License

from prompt_toolkit.layout import Dimension
from prompt_toolkit.lexers.base import Lexer
from prompt_toolkit.lexers import PygmentsLexer

from pygments.lexers import CLexer

from window import Window

class LineItemsLexer(Lexer):
    def __init__(self, window):
        self.window = window
        self.lexer = PygmentsLexer(CLexer, sync_from_start=False)
        super(LineItemsLexer, self).__init__()


    def lex_document(self, document):
        lexer_lex_line = self.lexer.lex_document(document)
        def lex_line(lineno):
            parts = lexer_lex_line(lineno)
            changed = self.window.changed
            if lineno < len(changed) and changed[lineno]:
                parts = [('bold fg:Olive', t) for (s, t) in parts]
            return parts
        return lex_line

class LineItemsWindow(Window):
    def __init__(self,
                 app=None,
                 show=False,
                 title='[Line Items]',
                 show_divider=lambda:True,
                 height=Dimension(preferred=1)):
        self.lexer = LineItemsLexer(self)
        self.lines = []
        self.changed = []

        super(LineItemsWindow, self).__init__(app=app,
                                              show=show,
                                              title=title,
                                              show_divider=show_divider,
                                              height=height)


    def handle_output(self, output):
        self.changed = [False] * 100
        lines = ['  ' + l for l in output.strip().split('\n')]
        for i in range(0, len(lines)):
            self.changed[i] = i < len(self.lines) and lines[i] != self.lines[i]
        self.lines = lines
        self.buffer.text = output

    def reset(self):
        self.lines = []
        self.changed = []
        self.buffer.text = ''
