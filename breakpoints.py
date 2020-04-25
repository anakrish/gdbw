# Copyright (c) Anand Krishnamoorthi
# Licensed under the MIT License

from re import compile, search, split, match

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


class BreakpointsLexer(Lexer):
    def __init__(self, window):
        self.window = window

    def lex_document(self, document):
        def get_what(what):
            parts = []
            if what.startswith('in '):
                parts.append(('', 'in '))
                pf = 3
                ps = what.find(' ', pf)
                if ps > 0:
                    parts.append(('Olive', what[pf:ps]))
                    pat = what.find(' at ', ps)
                    if pat > 0:
                        parts.append(('', ' at '))
                        parts.append(('Olive', what[ps+4:]))
                else:
                    parts.append(('Olive', what[pf:]))
            return parts
            
        def lex_line(lineno):
            line = document.lines[lineno]
            formatted_line = None
            try:
                if lineno == 0:
                    return [('fg:%s bold' % colors['LightSlateGrey'], line)]
                else:
                    ptype = document.lines[0].find('Type')
                    pdisp = ptype + 11
                    penb = pdisp + 5
                    phits = penb + 4
                    paddress = phits + 5
                    pwhat = paddress + 19

                    parts = [(colors['DodgerBlue'], line[0:ptype]),
                             (colors['Green'], line[ptype:pdisp]),
                             (colors['Green'], line[pdisp:penb]),
                             (colors['DarkKhaki'], line[penb:paddress]),
                             (colors['DodgerBlue'], line[paddress:pwhat])]

                    what = line[pwhat:]
                    parts += get_what(what)
                    
                    if self.window.changed[lineno]:
                        parts = [('bold fg:' + s, t) for (s, t) in parts]
                    return parts
            except:
                if formatted_line:
                    return formatted_line
                return [(colors['ForestGreen'], line)]
        return lex_line
            
    
class BreakpointsWindow:
    def __init__(self,
                 app=None,
                 show=False,
                 height=Dimension(preferred=20)):

        self.app = app
        self.show = show
        self.breakpoints = []
        self.hits = {}
        self.changed = []
        self.lexer = BreakpointsLexer(self)
        self.database = {}
        self.buffer = Buffer(document=Document(),
                             multiline=True)
        self.control = BufferControl(self.buffer,
                                     focusable=True,
                                     lexer=self.lexer,
                                     focus_on_click=True)
        self.window = Window(content=self.control,
                             height=height,
                             wrap_lines=True,
                             scroll_offsets = ScrollOffsets(top=5, bottom=5))

        divider = FormattedTextControl(text = [('Olive', ' \u2502' * 25)])
        divider = Window(content=divider,
                         wrap_lines=True,
                         width=2)
        divider = VSplit([VerticalLine()], style='Olive')
        self.container = ConditionalContainer(
            content=VSplit([divider,
                            self.window]),
            filter=Condition(lambda: self.show))

    def get_ui(self):
        return self.container
    
    def toggle_show(self):
        self.show = not self.show

    def reset(self):
        self.breakpoints = []
        self.changed = []
        self.hits = {}

    def has_breakpoint(self, loc):
        return loc in self.database

    def handle_info_breakpoints(self, output):
        output_lines = output.split('\n')
        lines = [output_lines[0]]
        hits = {}
        p1 = compile('(\d+).+')
        p2 = compile('\sbreakpoint already hit (\d+) time.*')
        bpnum = ''
        for line in output_lines[1:]:
            m = p1.match(line)
            if m:
                lines.append(line)
                bpnum = m[1]
            else:
                m = p2.match(line)
                if m:
                    hits[bpnum] = m[1]        

        # Populate database
        pos = lines[0].find('Address')
        p3 = compile('at (.+)')
        self.database = {}
        for line in lines[1:]:
            addr = line[pos:pos+2+16]
            self.database[addr] = True
            m = p3.search(line[pos:])
            if m:
                self.database[m[1]] = True

        # Insert hit counts also determine if hit counts changed.
        changed = [False] * len(lines)
        if len(self.database) > 0:
            lines[0] = '%sHits %s' % (lines[0][:pos], lines[0][pos:])
            for i in range(1, len(lines)):
                line = lines[i]
                m = p1.match(line)
                h = ''
                if m:
                    bpnum = m[1]                    
                    if line[len(bpnum)] != '.': # Ignore location line for multiple
                        if bpnum in hits:
                            h = hits[bpnum]
                            if not bpnum in self.hits or self.hits[bpnum] != h:
                                changed[i] = True

                lines[i] = '{}{:<5}{}'.format(line[:pos], h, line[pos:])

        # Trim
        pt = lines[0].find('Type')
        pd = lines[0].find('Disp')
        if pt > 0:
            for i in range(0, len(lines)):
                line = lines[i]
                ch = '>' if changed[i] else ' '
                lines[i] = '%c%s%s%s' %(ch,line[:pt-4], line[pt:pd-4], line[pd:]) 
        
        self.hits = hits
        self.changed = changed
        self.buffer.text = '\n'.join(lines) + str(self.changed)

