# Copyright (c) Anand Krishnamoorthi
# Licensed under the MIT License

from os.path import basename
from re import search

from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document
from prompt_toolkit.filters import Condition
from prompt_toolkit.layout.containers import ConditionalContainer, Window, HSplit, VSplit
from prompt_toolkit.layout.controls import BufferControl
from prompt_toolkit.layout import Dimension, ScrollOffsets
from prompt_toolkit.lexers import DynamicLexer, PygmentsLexer, SyntaxSync
from prompt_toolkit.layout.margins import NumberedMargin
from prompt_toolkit.styles import style_from_pygments_cls
from prompt_toolkit.widgets import Frame, TextArea, HorizontalLine

from pygments.styles import get_style_by_name
from pygments.lexers import GasLexer

from infoline import InfoLine

class SourceWindow:
    default_title = "[ no source file ]"
    
    def __init__(self,
                 app=None,
                 show=True,
                 height=Dimension(preferred=60),
                 width=Dimension(preferred=1)): #80?                 
        self.app = app
        self.show = show
        self.basename = None
        self.filename = None
        self.current_line = -1
        self.handle_source_change = False
        self.lexer = None
        self.buffer = Buffer(document=Document(),
                             multiline=True) # TODO: Intelligent readonly lambda
        self.control = BufferControl(self.buffer,
                                     focusable=True,
                                     lexer=DynamicLexer(lambda: self.lexer),
                                     focus_on_click=True)
        self.window = Window(content=self.control,
                             height=height,
                             width=width,
                             wrap_lines=False,
                             left_margins=[NumberedMargin()],
                             scroll_offsets = ScrollOffsets(top=5, bottom=40),
                             get_line_prefix=self._get_line_prefix)
        
        self.info = InfoLine(text='', width=240)
        self.container = ConditionalContainer(
            content=HSplit([self.info.get_ui(),
                            self.window]),
            filter=Condition(lambda: self.show))

    def get_ui(self):
        return self.container

    def log(self, msg):
        self.app.log(msg)

    def reset(self):
        pass

    def toggle_show(self):
        self.show = not self.show

    def handle_info_source(self, output):
        self.log('*** Handling info source')
        self.handle_source_change = False
        m = search('Located in (.+)', output)
        if not m:            
            self.buffer.document = Document()
            self.filename = None
            self.handle_source_change = True
            self.info.set_info(self.default_title)
            return

        filename = m[1]
        if filename and filename != self.filename:
            self.log('***Opening %s\n' % (filename))
            with open(filename, "r") as f:
                self.info.set_info('[%s]' % filename)
                text = f.read().replace('\t', '    ')               
                self.lexer = PygmentsLexer.from_filename(
                    filename,
                    sync_from_start=False)
                    #syntax_sync=SyntaxSync())
                if filename.endswith('.s') or filename.endswith('.S'):
                    self.lexer = PygmentsLexer(GasLexer,
                                               sync_from_start=False)
                self.buffer.text = text
                self.basename = basename(filename)
                self.filename = filename                
                self.handle_source_change = True
                self._set_cursor(0)
                self.info.set_info('[ %s ]' % filename)
                #self.info.set_info('[ %s ]' % type(self.lexer))
        

    def handle_info_line(self, output):
        self.log('*** Here')
        m = search('Line (.+) of', output)
        if not m:
            return
        line = int(m[1]) - 1
        self.current_line = line
        self.log('*** Current line %d' % (self.current_line))
        render_info = self.window.render_info
        if render_info and not self.handle_source_change:
            fv_line = render_info.first_visible_line()
            lv_line = render_info.last_visible_line()
            if line <= fv_line or line >= lv_line - 1:
                self._set_cursor(line)
        else:
            self._set_cursor(line)
        self.handle_source_change = False

    def _set_title(self, title):
        self.title.text = []
    def _set_cursor(self, line):
        self.log('*** Cursor Line %d' % (line))
        pos = self.buffer.document.translate_row_col_to_index(line, 0)
        self.buffer.cursor_position = pos
    
    def _get_line_prefix(self, line, parts):
        loc = '%s:%d' % (self.basename, line+1)
        loc1 = '%s:%d' % (self.filename, line+1)
        if self.app.has_breakpoint(loc1): # fullpath
            prefix = 'X '
        elif self.app.has_breakpoint(loc):
            prefix = 'X'
        else:
            prefix = '  '
        if line == self.current_line:
            return prefix + '=>'
        else:
            return prefix + '  '
    
