# Copyright (c) Anand Krishnamoorthi
# Licensed under the MIT License

from prompt_toolkit.layout import Dimension, ScrollOffsets

from lineitemswindow import LineItemsWindow
        
class RegistersWindow(LineItemsWindow):
    def __init__(self,
                 app=None,
                 show=False,
                 height=Dimension(preferred=22)):
        super(RegistersWindow, self).__init__(app=app,
                                              show=show,
                                              height=height,
                                              title='[ Registers ]',
                                              show_divider = self._show_divider)

    def handle_info_registers(self, output):
        self.handle_output(output)
        self.fit_to_height()

    def _show_divider(self):
        return self.app.source.show or self.app.disassembly.show
