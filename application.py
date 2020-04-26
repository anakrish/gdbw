# Copyright (c) Anand Krishnamoorthi
# Licensed under the MIT License

from re import search

from prompt_toolkit.application import Application as PromptApplication
from prompt_toolkit.key_binding.defaults import load_key_bindings
from prompt_toolkit.key_binding import (
    KeyBindings, merge_key_bindings)
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.styles import style_from_pygments_cls
from prompt_toolkit.widgets import Frame

from pygments.styles import get_style_by_name, get_all_styles

from argsnlocals import ArgsnLocalsWindow
from breakpoints import BreakpointsWindow
from callstack import CallstackWindow
from console import ConsoleWindow
from disassembly import DisassemblyWindow
from registers import RegistersWindow
from source import SourceWindow
from threads import ThreadsWindow

class Application:
    def __init__(self):
        self.style_name = 'trac'
        self.frame = None
        self.argsnlocals = ArgsnLocalsWindow(app=self)
        self.console = ConsoleWindow(app=self, callback = self._gdb_callback)
        self.source = SourceWindow(self)
        self.breakpoints = BreakpointsWindow(self, show=False)
        self.callstack = CallstackWindow(self, show=False)
        self.disassembly = DisassemblyWindow(self, show=False)
        self.registers = RegistersWindow(self, show=False)
        self.threads = ThreadsWindow(self, show=False)
        self.inferiors = ''


        self.col1 = HSplit([self.source.get_ui(),
                            self.disassembly.get_ui(),
                            self.console.get_ui()])

        self.col2 = HSplit([self.argsnlocals.get_ui(),
                            self.registers.get_ui(),
                            self.callstack.get_ui(),
                            self.threads.get_ui()])

        self.container = VSplit([self.col1, self.col2])
        self.layout = Layout(container=self.container,
                             focused_element=self.console.get_ui())

        self.style = style_from_pygments_cls(
            get_style_by_name(self.style_name))

        kb = self._get_key_bindings()

        self.app = PromptApplication(layout=self.layout,
                                     style=self.style,
                                     full_screen=True,
                                     mouse_support=True,
                                     key_bindings=kb)
        

    def run(self):
        self.log('*** Running application')
        self.app.run()

    def log(self, msg):
        self.console.log(msg)

    def has_breakpoint(self, loc):
        return self.breakpoints.has_breakpoint(loc)

    def _hide_tui(self):
        def hide(c):
            if c.show:
                c.toggle_show()
        hide(self.source)
        hide(self.disassembly)
        hide(self.argsnlocals)
        hide(self.registers)
        hide(self.callstack)
        hide(self.threads)
        hide(self.breakpoints)
        self.app.invalidate()
        
    def _get_key_bindings(self):
        kb = KeyBindings()
        @kb.add('c-up')
        def _(event):
            self.console.enter_copy_mode()

        @kb.add('c-x', 'a', eager=True)
        def _(event):
            self._hide_tui()
            self.app.invalidate()
            
        @kb.add('c-x', '1', eager=True)
        def _(event):
            self._hide_tui()
            self.source.show = True
            self.app.invalidate()
            
        @kb.add('c-x', '2', eager=True)
        def _(event):
            self._hide_tui()
            self.source.show = True
            self.disassembly.show = True

        @kb.add('c-x', 's', eager=True)
        def _(event):
            self.source.toggle_show()
            self.app.invalidate()
            
        @kb.add('c-x', 'd', eager=True)
        def _(event):
            self.disassembly.toggle_show()
            self.app.invalidate()
            
        @kb.add('c-x', 'c', eager=True)
        def _(event):
            self.callstack.toggle_show()
            self.app.invalidate()
            
        @kb.add('c-x', 'v', eager=True)
        def _(event):
            self.argsnlocals.toggle_show()
            self.app.invalidate()
            
        @kb.add('c-x', 'b', eager=True)
        def _(event):
            self.breakpoints.toggle_show()
            self.app.invalidate()
            
        @kb.add('c-x', 'r', eager=True)
        def _(event):
            self.registers.toggle_show()
            self.app.invalidate()
            
        @kb.add('c-x', 't', eager=True)
        def _(event):
            self.threads.toggle_show()

        @kb.add('c-s', eager=True)
        def _(event):
            self._next_style()
            
        @kb.add('c-l')
        def _(event):
            pass

        @kb.add('c-x')
        def _(event):
            pass

        @kb.add('s-right')
        def _(event):
            self.layout.focus_next()

        @kb.add('s-left')
        def _(event):
            self.layout.focus_previous()
            
        kb = merge_key_bindings([load_key_bindings(), kb])
        return kb

    def _handle_info_inferiors(self, output):
        m = search('process (\d+)', output)
        if m and m[1] != self.inferiors:
            # Program (re)run
            self.log('**match %s' % m[1])
            self.inferiors = m[1]
            self.breakpoints.reset()
            self.source.reset()
            self.disassembly.reset()
            self.registers.reset()
            self.frame = None

    def _handle_info_frame(self, output):
        self.callstack.handle_info_frame(output)
        m = search('frame at (0x.+):', output)
        frame = m[1] if m else None
        changed = frame != self.frame
        self.frame = frame
        if changed:
            self.argsnlocals.handle_frame_change()
            
    def _gdb_callback(self, response):
        self.log('***Received \n%s' % response)
        try:
            p = response.find('\n')
            cmd = response[:p]
            output = response[p+1:]
            if cmd.startswith('info source'):
                self.source.handle_info_source(output)
            elif cmd.startswith('info line'):
                self.source.handle_info_line(output)
                # This invalidate is needed to refresh source cursor properly.
                self.app.invalidate()
                
            elif cmd.startswith('info args'):
                self.argsnlocals.handle_info_args(output)            
            elif cmd.startswith('info locals'):
                self.argsnlocals.handle_info_locals(output)

            elif cmd.startswith('disassemble'):
                self.disassembly.handle_disassemble(output)
            elif cmd.startswith('info registers'):
                self.registers.handle_info_registers(output)

            elif cmd.startswith('info breakpoints'):
                self.breakpoints.handle_info_breakpoints(output)
                                
            elif cmd.startswith('bt '):
                self.callstack.handle_bt(output)

                
            elif cmd.startswith('info frame'):
                self._handle_info_frame(output)
            elif cmd.startswith('info inferiors'):
                self._handle_info_inferiors(output)

            elif cmd.startswith('info threads'):
                self.threads.handle_info_threads(output)
        except:
            self.log('***Exception %s' % (exec_info()[1]))


    def _next_style(self):
        styles = list(get_all_styles())
        for i in range(0, len(styles)):
            if styles[i] == self.style_name:
                if i+1 == len(styles):
                    self.style_name = styles[0]
                else:
                    self.style_name = styles[i+1]
                    break

        self.style = style_from_pygments_cls(
             get_style_by_name(self.style_name))
        self.app.style = self.style
        self.console.update_info()
        self.app.invalidate()
