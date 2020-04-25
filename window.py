# Copyright (c) Anand Krishnamoorthi
# Licensed under the MIT License

from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document
from prompt_toolkit.filters import Condition
from prompt_toolkit.layout.containers import Window as PromptWindow
from prompt_toolkit.layout.containers import ConditionalContainer, VSplit, HSplit
from prompt_toolkit.layout.controls import BufferControl
from prompt_toolkit.layout import Dimension, ScrollOffsets
from prompt_toolkit.lexers.base import Lexer
from prompt_toolkit.lexers import DynamicLexer

from divider import Divider
from infoline import InfoLine

class Window:
    def __init__(self,
                 app=None,
                 show=False,
                 title='[ A Window ]',
                 show_divider=lambda:True,
                 get_lexer=lambda: None,
                 height=Dimension(preferred=1),
                 wrap_lines=False,
                 scroll_offsets=ScrollOffsets()):
        self.app = app
        self.show = show
        self.buffer = Buffer(document=Document(),
                             multiline=True)
        self.control = BufferControl(buffer=self.buffer,
                                     focusable=True,
                                     lexer=self.lexer,
                                     focus_on_click=True)
        self.window = PromptWindow(content=self.control,
                                   height=height,
                                   wrap_lines=wrap_lines,
                                   scroll_offsets=scroll_offsets)

        self.divider = Divider(self, show=show_divider)
        self.info = InfoLine(title, width=240)
        self.container = ConditionalContainer(
            content=VSplit([
                self.divider.get_ui(),
                HSplit([self.info.get_ui(), self.window])]),
            filter=Condition(lambda: self.show))
        
    def get_ui(self):
        return self.container
    
    def toggle_show(self):
        self.show = not self.show
        
    def fit_to_height(self):
        d = self.buffer.document
        l = len(d.lines)
        self.window.height = Dimension(preferred=l)
    
    def reset(self):
        self.buffer.text = ''
