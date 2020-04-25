#!/usr/bin/env python3
# Copyright (c) Anand Krishnamoorthi
# Licensed under the MIT License

from os import environ, getpid
from os.path import abspath, dirname
from subprocess import check_output
from sys import argv, exit

from prompt_toolkit.application import get_app
from prompt_toolkit.layout import Dimension
from prompt_toolkit.layout.containers import ConditionalContainer, Window, HSplit, VSplit
from prompt_toolkit.widgets import Box,Frame,Shadow
from ptterm import Terminal

from infoline import InfoLine
from namedpipe import NamedPipe

class ConsoleWindow:
    def __init__(self,
                 app,
                 height=Dimension(preferred=20),
                 width=Dimension(preferred=20),
                 callback=None):

        self.app = app
        gdb = self._get_gdb_path()
        self._create_pipes()
        self._update_pythonpath()

        gdbw_dir = self._get_gdbw_dir()
        source_cmd = 'source %s/gdbwhelper.py' % (gdbw_dir)
        gdb_run_cmd = [gdb, '-iex', source_cmd] + argv[1:]
        self.console = Terminal(gdb_run_cmd,
                                done_callback=self._done,
                                height=height,
                                width=width)
        self.info = InfoLine(text='', width=240)
        self.window = HSplit([self.info.get_ui(),
                              self.console])
        self.update_info()
        self.in_pipe.begin_reading(callback)

    def get_ui(self):
        return self.window

    def enter_copy_mode(self):
        self.console.enter_copy_mode()

    def exit_copy_mode(self):
        self.console.exit_copy_mode()
        
    def log(self, msg):
        if self.gdbw_log_pipe:
            self.gdbw_log_pipe.write(str(msg) + '\n')
    
    def _get_gdbw_dir(self):
        return dirname(abspath(__file__))

    def _get_gdb_path(self):
        gdbscript_path = self._get_gdbw_dir() + '/gdb'
        gdb_paths = check_output(['which', '-a', 'gdb'])
        gdb_paths = gdb_paths.decode('utf-8').strip().split('\n')
        for g in gdb_paths:
            g = check_output(['readlink', '-f', g]).decode('utf-8').strip()
            if g != gdbscript_path:
                return g
        print('Could not find gdb. Aborting.')
        exit(1)

    def _done(self):
        self.in_pipe.close()
        self.out_pipe.close()
        if self.log_pipe:
            self.log_pipe.close()
        if self.gdbw_log_pipe:
            self.gdbw_log_pipe.close()
        get_app().exit()


    def _create_pipes(self):
        pid = getpid()
        self.out_pipe = NamedPipe('/tmp/gdbh_in_pipe_%d' % (pid))
        self.in_pipe = NamedPipe('/tmp/gdbh_out_pipe_%d' % (pid))
        pipes_str = '%s\n%s' % (self.out_pipe.path, self.in_pipe.path)

        # Create logging pipes
        self.gdbw_log_pipe = None
        self.log_pipe = None
        try:
            if int(environ['GDBW_ENABLE_LOGGING']):
                self.gdbw_log_pipe = NamedPipe('/tmp/gdbw_log_%d' % (pid))
                self.log_pipe = NamedPipe('/tmp/gdbh_log_%d' % (pid))
                pipes_str += '\n' + self.log_pipe.path
        except:
            pass

        environ['GDBW_PIPES'] = pipes_str

    def _update_pythonpath(self):
        pp = 'PYTHONPATH'
        ppv = environ[pp] if pp in environ else ''
        gdbw_dir = self._get_gdbw_dir()
        environ[pp] = '%s:%s' % (ppv, gdbw_dir)

    def update_info(self):
        self.info.set_info('[ gdbw console / style:%s ]' % self.app.style_name)
        
        
            
