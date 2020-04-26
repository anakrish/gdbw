# Copyright (c) Anand Krishnamoorthi
# Licensed under the MIT License


from re import compile, search

from prompt_toolkit.layout import Dimension, ScrollOffsets
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.lexers.base import Lexer

from pygments.lexers import get_lexer_by_name, CLexer
from pygments.token import Token

from window import Window


class BreakpointsLexer(Lexer):
    def __init__(self):
        super(BreakpointsLexer, self).__init__()
        self.lexer = PygmentsLexer(CLexer, sync_from_start=False)

    def lex_document(self, document):
        lexer_lex_line = self.lexer.lex_document(document)
        def lex_line(lineno):
            line = document.lines[lineno]
            if line.strip().startswith('at'):
                return [('bold italic fg:DarkOliveGreen', document.lines[lineno])]
            parts = lexer_lex_line(lineno)
            for i in range(0, len(parts)):
                if parts[i][1] == '*':
                    parts[i] = (parts[i][0] + ' reverse ', parts[i][1])
                elif parts[i][1] == 'in':
                    parts[i+2] = ('bold fg:Olive', parts[i+2][1])
                elif parts[i][1] == 'hit':
                    parts[i+2] = ('bold ' + parts[i+2][0], parts[i+2][1])
            return parts
        return lex_line

class BreakpointsWindow(Window):
    def __init__(self,
                 app=None,
                 show=False,
                 height=Dimension(preferred=5)):
        self.lexer = BreakpointsLexer()
        self.breakpoints = {}
        self.changed = {}
        self.database = {}
        self.hits = {}
        scroll_offsets = ScrollOffsets(top=2,
                                       bottom=2)
        super(BreakpointsWindow, self).__init__(app=app,
                                                show=show,
                                                title='[ Breakpoints ]',
                                                scroll_offsets=scroll_offsets)

    def has_breakpoint(self, loc):
        return loc in self.database

    def _build_database(self, output):
        database = {}
        hits = {}
        changed = {}
        lines = output.strip().split('\n')
        hc = ''
        breakpoints = {}
        if len(lines) > 1:
            ptype = lines[0].find('Type')
            pdisp = lines[0].find('Disp', ptype)
            penb = lines[0].find('Enb', pdisp)
            paddress = lines[0].find('Address', penb)
            pwhat = lines[0].find('What', paddress)
            rebnum = compile('(\d+\.\d+)|(\d+)')
            reddr = compile('(0x.+)')
            rhc = compile('hit (\d+) time')
            bnum = ''
            for line in lines[1:]:
                m = rebnum.search(line)
                if m and m.start() == 0:
                    # breakpoint line
                    bnum = m[1] if m[1] else m[2]
                    typ = line[ptype:pdisp].strip()
                    disp = line[pdisp:penb].strip()
                    enb = line[penb:paddress].strip() == 'y'
                    address = line[paddress:pwhat].strip()
                    if address[0:1] == '0':
                        database[address] = True
                    what = line[pwhat:].strip()
                    hits[bnum] = ''
                    at = ''
                    pat = what.find('at ')
                    if pat > 0:
                        at = what[pat+3:]
                        database[at] = True
                        what = what[:pat].strip()
                    else:
                        if not what.startswith('in'):
                            at = what
                            what = ''
                    breakpoints[bnum] = (typ, disp, enb, address, what, at)
                else:
                    m = rhc.search(line)
                    if m:
                        hc = m[1]
                        hits[bnum] = hc
                        if hc != '':
                            if bnum not in self.hits or self.hits[bnum] != hc:
                                changed[bnum] = True
                        

        self.changed = changed
        self.breakpoints = breakpoints
        self.database = database
        self.hits = hits

                
    def handle_info_breakpoints(self, output):
        self._build_database(output)
        if len(self.breakpoints) == 0:
            self.buffer.text = output
            self.fit_to_height()
            return

        lines = []
        for (bnum, val) in self.breakpoints.items():
            ch = ' '
            if bnum in self.changed and self.changed[bnum]:
                ch = '*'
            line = ' {}{:<4} {:<10} {:<18} {}'.format(ch, bnum, val[0], val[3], val[4])
            if bnum in self.hits:
                hc = self.hits[bnum]
                if hc != '':
                    line += ' hit %s time' % hc
                    if hc != '1':
                        line += 's'
            lines.append(line)
            if val[5] != '':
                lines.append('       at ' + val[5])

        self.buffer.text = '\n'.join(lines)        

    def reset(self):
        self.buffer.text = ''
        self.database = {}
        self.hits = {}
        self.breakpoints = {}
        self.changed = {}
