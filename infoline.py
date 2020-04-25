# Copyright (c) Anand Krishnamoorthi
# Licensed under the MIT License

from re import split

from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document
from prompt_toolkit.filters import Condition
from prompt_toolkit.layout import FormattedTextControl
from prompt_toolkit.layout.containers import ConditionalContainer, Window, VSplit
from prompt_toolkit.layout.controls import BufferControl
from prompt_toolkit.layout import Dimension, ScrollOffsets
from prompt_toolkit.lexers.base import Lexer
from prompt_toolkit.layout.margins import NumberedMargin
from pygments.styles import get_style_by_name
from prompt_toolkit.styles import style_from_pygments_cls
from prompt_toolkit.styles.named_colors import NAMED_COLORS as colors
from prompt_toolkit.widgets import Box,Frame,VerticalLine



class InfoLineLexer(Lexer):
    def __init__(self, window):
        self.window = window

    def lex_document(self, document):
        def lex_line(lineno):
            lchar = '\u2500'
            style = 'bold fg:DarkGoldenRod'
            info = [('', lchar*4)]
            p = 0
            line = document.lines[lineno]
            w = 4
            while p >= 0 and p < len(line):
                s = p
                p = line.find('[', s)
                if p >= 0:
                    n = p - s
                    w += n
                    info.append(('', lchar*n))
                    e = line.find(']',p)
                    if e > 0:
                        info.append(('', ' '))                        
                        info.append((style, line[p+1:e]))
                        info.append(('', ' '))
                        w += 2 + e - (p+1)
                    p = e
            if w < self.window.width:
                info.append(('', lchar* (self.window.width - w)))
            return info
        return lex_line
    
class InfoLine:
    def __init__(self, text='', width=80):
        self.width = width
        self.lexer = InfoLineLexer(self)
        self.buffer = Buffer(document=Document(), multiline=False)
        self.buffer.text = text
        self.control = BufferControl(self.buffer,
                                     focusable=False,
                                     lexer=self.lexer)
        self.window = Window(content=self.control,
                             height=1,
                             wrap_lines=False)

    def get_ui(self):
        return self.window

    def set_info(self, text):
        self.buffer.text =  text
        
