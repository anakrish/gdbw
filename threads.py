# Copyright (c) Anand Krishnamoorthi
# Licensed under the MIT License

from re import compile, search

from prompt_toolkit.layout import Dimension, ScrollOffsets
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.lexers.base import Lexer

from pygments.lexers import get_lexer_by_name, CLexer
from pygments.token import Token

from window import Window

class ThreadsLexer(Lexer):
    def __init__(self):
        super(ThreadsLexer, self).__init__()
        self.lexer = PygmentsLexer(CLexer, sync_from_start=False)

    def lex_document(self, document):
        lexer_lex_line = self.lexer.lex_document(document)
        def lex_line(lineno):
            line = document.lines[lineno]
            if len(document.lines)> 1 and len(line) > 1 and line[1] != ' ':
                parts = lexer_lex_line(lineno)
                if len(parts) > 0:
                    parts[-1] = ('bold fg:Olive', parts[-1][1])
                if line[0] == '*':
                    idx = 0 if lineno == 0 else 1
                    parts[idx] = ('reverse ' + parts[idx][0], parts[idx][1])
                        
                return parts
            else:
                return [('bold italic fg:DarkOliveGreen', document.lines[lineno])]
        return lex_line

class ThreadsWindow(Window):
    def __init__(self,
                 app=None,
                 show=False,
                 height=Dimension(preferred=5)):
        self.lexer = ThreadsLexer()
        scroll_offsets = ScrollOffsets(top=5,
                                       bottom=5)
        super(ThreadsWindow, self).__init__(app=app,
                                            show=show,
                                            title='[ Threads ]',
                                            scroll_offsets=scroll_offsets)

    def handle_info_threads(self, output):
        lines = []
        p = compile('(\d+)\s+Thread (.+)(\(.+\))(.+)\s+\(.*\)')
        for line in output.split('\n'):
            m = p.search(line)
            if m:
                ch = '*' if line.startswith('*') else ' '
                lines.append('{}{:<3} Thread {}{}{}'.format(ch, m[1], m[2],
                                                                m[3], m[4]))
                pat = line.find(' at ', m.lastindex)
                if pat > 0:
                    lines.append('    ' + line[pat:])

        if len(lines) > 0:
            text = '\n'.join(lines)
            self.buffer.text = text
            self.buffer.cursor_position = text.find('*')
        else:
            self.buffer.text = output

        
        self.fit_to_height()



    
