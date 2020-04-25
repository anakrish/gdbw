# Copyright (c) Anand Krishnamoorthi
# Licensed under the MIT License

from re import compile, search

from prompt_toolkit.layout import Dimension, ScrollOffsets
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.lexers.base import Lexer

from pygments.lexers import get_lexer_by_name, CLexer
from pygments.token import Token

from window import Window

class CallstackLexer(Lexer):
    def __init__(self):
        super(CallstackLexer, self).__init__()
        self.lexer = PygmentsLexer(CLexer, sync_from_start=False)

    def lex_document(self, document):
        lexer_lex_line = self.lexer.lex_document(document)
        def lex_line(lineno):
            if lineno % 2 == 0:
                parts = lexer_lex_line(lineno)
                if len(parts) > 0:
                    parts[-1] = ('bold fg:Olive', parts[-1][1])
                return parts
            else:
                return [('italic fg:DarkOliveGreen', document.lines[lineno])]
        return lex_line

class CallstackWindow(Window):
    def __init__(self,
                 app=None,
                 show=False,
                 height=Dimension(preferred=20)):
        self.frame = None
        self.lexer = CallstackLexer()
        scroll_offsets = ScrollOffsets(top=5,
                                       bottom=5)
        super(CallstackWindow, self).__init__(app=app,
                                              show=show,
                                              title='[ Callstack ]',
                                              scroll_offsets=scroll_offsets)

    def handle_bt(self, output):
        output = output.replace(' at ', '\n       ')
        p = compile('\s*(\(.*\))')
        #output = p.sub(lambda m: '\n   ' + m[1], output)
        output = p.sub(lambda m: '', output)
        p = compile('#(\d+)')
        output = p.sub(lambda m: '  [%s]' % m[1], output)
        if self.frame:
            p = compile('(  \[%s\])' % self.frame)
            output = p.sub('=>[%s]' % self.frame, output)
            p = output.find('=>')
            self.buffer.cursor_position = p
        self.buffer.text = output
        self.fit_to_height()

    def handle_info_frame(self, output):
        m = search('Stack level (\d+)', output)
        self.frame = None
        if m:            
            self.frame = m[1]

    
