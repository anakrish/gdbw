# Copyright (c) Anand Krishnamoorthi
# Licensed under the MIT License

from re import compile, search, split

from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document
from prompt_toolkit.filters import Condition
from prompt_toolkit.layout import FormattedTextControl
from prompt_toolkit.layout.containers import ConditionalContainer, Window, VSplit, HSplit
from prompt_toolkit.layout.controls import BufferControl
from prompt_toolkit.layout import Dimension, ScrollOffsets
from prompt_toolkit.lexers.base import Lexer
from prompt_toolkit.lexers import DynamicLexer, PygmentsLexer, SyntaxSync
from prompt_toolkit.layout.margins import NumberedMargin
from prompt_toolkit.styles import style_from_pygments_cls
from prompt_toolkit.styles.named_colors import NAMED_COLORS as colors
from prompt_toolkit.widgets import Box,Frame,VerticalLine


from pygments.lexers import CLexer
from pygments.styles import get_style_by_name

from infoline import InfoLine


class Divider:
    def __init__(self, style='bg:DarkGrey', type='Wide',
                 width=2,show=lambda: True):
        if type == 'Wide':
            self.divider = Window(style='bg: DarkGrey', width=width)
        else:
            self.divider = VerticalLine()

        self.container = ConditionalContainer(
            content=self.divider,
            filter = Condition(show))

    def get_ui(self):
        return self.container
        
