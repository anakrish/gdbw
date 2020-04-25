# Copyright (c) Anand Krishnamoorthi
# Licensed under the MIT License

from re import search

from prompt_toolkit.filters import Condition
from prompt_toolkit.layout.containers import ConditionalContainer, HSplit
from prompt_toolkit.layout import Dimension

from lineitemswindow import LineItemsWindow

class ArgsnLocalsWindow:
    def __init__(self,
                 app=None,
                 show=False,
                 height=Dimension(preferred=20)):

        self.frame = None
        self.app = app
        self.show = show
        self.args = LineItemsWindow(app=app,
                                    show=show,
                                    title ='[ Args ]',
                                    show_divider=self._show_divider)
        self.locals = LineItemsWindow(app=app,
                                      show=show,
                                      title ='[ Locals ]',
                                      show_divider=self._show_divider)

        self.container = ConditionalContainer(
            content=HSplit([
                self.args.get_ui(),
                self.locals.get_ui()
                ]),
            filter=Condition(lambda: self.show))

    def get_ui(self):
        return self.container

    def toggle_show(self):
        self.show = not self.show
        self.args.toggle_show()
        self.locals.toggle_show()
        
    def handle_info_args(self, output):
        self.args.handle_output(output)
        self.args.fit_to_height()        
        
    def handle_info_locals(self, output):
        self.locals.handle_output(output)
        self.locals.fit_to_height()

    def handle_frame_change(self):
        self.args.reset()
        self.locals.reset()
        
    def _show_divider(self):
        return self.app.source.show

    def reset(self):
        self.args.reset()
        self.locals.reset()
