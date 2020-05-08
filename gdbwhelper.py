#!/usr/bin/env python3
# Copyright (c) Anand Krishnamoorthi
# Licensed under the MIT License

# Intended to be sourced from GDB.
import gdb
from os import environ
from namedpipe import NamedPipe

def pretty(msg):
    return '\033[1m\033[38;1;95m%s\033[0m' % (msg)

def pprint(msg):
    gdb.write(pretty(msg) + '\n')
    gdb.flush()

def main():
    
    def prompt_hook(current_prompt):
        # Threads can be notified anywhere.
        post_command('info threads')
        
        # Notify frame change first 
        post_command('info frame')
        
        # Determine if program has been (re)run
        post_command('info inferiors')

        # Breakpoint must come before source and disassembly
        post_command('info breakpoints')

        # Args and Locals
        post_command('info args')
        post_command('info locals')
        
        # Disassembly
        post_command('disassemble')
        post_command('bt 64')
        post_command('info registers all')

        return current_prompt.replace('(gdb) ', pretty('(gdb) '))

    def log(msg):
        if log_pipe:
            log_pipe.write(str(msg) + '\n')

    def make_command(cmd):
        def execute_cmd():
            try:
                log('executing "%s"' % (cmd))
                result = gdb.execute(cmd, from_tty=False, to_string = True)
                log('result = ' + result)
                response = '%s\n%s' % (cmd, result)
                out_pipe.write(response)
                log('wrote obj to gdbw pipe.')
            except:
                pass
        return execute_cmd

    def post_command(cmd):
        gdb.post_event(make_command(cmd))

    var = 'GDBW_PIPES'
    try:
        pipes = environ[var].split()
        in_pipe = NamedPipe(pipes[0])
        out_pipe = NamedPipe(pipes[1])
        log_pipe = NamedPipe(pipes[2]) if len(pipes) == 3 else None
        pprint('Talking to gdbw via (%s, %s).' % (pipes[0], pipes[1]))
        if log_pipe:
            pprint('Logging to %s.' % log_pipe.path)
    except:
        pprint('Could not process environment variable %s.' % (var))
        return

    pprint('Turning off pagination...')
    gdb.execute('set pagination off')
    
    pprint('Starting command listener...')
    in_pipe.begin_reading(callback=post_command)

    pprint('Overriding GDB prompt...')    
    gdb.prompt_hook = prompt_hook

if __name__=='__main__':
    main()
