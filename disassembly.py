# Copyright (c) Anand Krishnamoorthi
# Licensed under the MIT License

from re import search, split

from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document
from prompt_toolkit.filters import Condition
from prompt_toolkit.layout import FormattedTextControl
from prompt_toolkit.layout.containers import ConditionalContainer, Window, HSplit, VSplit
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout import Dimension, ScrollOffsets
from prompt_toolkit.lexers.base import Lexer
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.layout.margins import NumberedMargin
from pygments.styles import get_style_by_name
from prompt_toolkit.styles import style_from_pygments_cls
from prompt_toolkit.styles.named_colors import NAMED_COLORS as colors
from prompt_toolkit.widgets import Box,Frame,Shadow

from pygments.lexers import get_lexer_by_name, CObjdumpLexer

from infoline import InfoLine

class DisassemblyLexer(Lexer):
    def __init__(self, window):
        self.window = window
        self.lexer = PygmentsLexer(CObjdumpLexer, sync_from_start=False)

    def lex_document(self, document):
        lexer_lex_line = self.lexer.lex_document(document)
        def fixup(t):
            return t.replace('/', '$').replace('^', '#')
        def lex_line(lineno):
            parts = lexer_lex_line(lineno)
            parts = [(s, fixup(t)) for (s,t) in parts]
            return parts
        return lex_line
    
class DisassemblyWindow:
    def __init__(self,
                 app=None,
                 show=False,
                 height=Dimension(preferred=22),
                 width=Dimension(preferred=25)):
        self.app = app
        self.show = show
        self.cursor_line = 0
        self.lexer = DisassemblyLexer(self)
        self.buffer = Buffer(document=Document(),
                             multiline=True)
        self.control = BufferControl(buffer=self.buffer,
                                     focusable=True,
                                     lexer=self.lexer,
                                     focus_on_click=True)
        self.window = Window(content=self.control,
                             height=height,
                             wrap_lines=False,
                             scroll_offsets = ScrollOffsets(top=0))

        self.info = InfoLine('[Disassembly]', width=240)
        self.container = ConditionalContainer(
            content=HSplit([self.info.get_ui(), self.window]),
            filter=Condition(lambda: self.show))

    def log(self, msg):
        self.app.log(msg)
        
    def get_ui(self):
        return self.container
    
    def toggle_show(self):
        self.show = not self.show

    def reset(self):
        self.cursor_line = 0
        self.buffer.text = ''
        
    def handle_disassemble(self, output):
        m = search('Dump of assembler code for function (.+):', output)
        if m:
            self.info.set_info('[ Disassembly for function %s ]' % m[1])

        output = output.replace('$', '/').replace('#', '^')
        lines = output.replace('\t', ' ').split('\n')
        lines = lines[1:-2]
        cursor_line = 0
        for i in range(0, len(lines)):
            line = lines[i]
            if line.startswith('=>'):
                cursor_line = i
            addr = line[3:3+18]
            if self.app.has_breakpoint(addr):
                line = 'X ' + line
            else:
                line = '  ' + line
            lines[i] = line
        self.buffer.text = '\n'.join(lines) + '\n'
        self.log('*** Disassembly here')
        render_info = self.window.render_info
        if render_info:
            fv_line = render_info.first_visible_line()
            lv_line = render_info.last_visible_line()
            height = lv_line - fv_line
            if cursor_line <= fv_line or cursor_line > lv_line:
                self._set_cursor(cursor_line+height)
        else:
            self._set_cursor(cursor_line)

    def _set_cursor(self, line):
        self.log('*** Disassembly cursor Line %d' % (line))
        pos = self.buffer.document.translate_row_col_to_index(line, 0)
        self.buffer.cursor_position = pos
        
        
