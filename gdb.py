#!/usr/bin/env python3
# Copyright (c) Anand Krishnamoorthi
# Licensed under the MIT License

from subprocess import call
from sys import exit

# Check and automatically install prerequisites.
try:
    import prompt_toolkit
    import pygments
    import ptterm
except:
    try:
        print('Installing prerequisites...')
        print('Installing pygments...')
        call('pip3 install pygments', shell=True)
        print('Installing prompt_toolkit...')
        call('pip3 install prompt_toolkit', shell=True)
        print('Installing ptterm...')
        call('pip3 install ptterm', shell=True)

        import prompt_toolkit
        import pygments
        import ptterm
    except:
        print('Could not install prerequisited.')
        print('Install pygments, prompt_toolkit and ptterm via pip.')
        exit(1)

from application import Application

def main():
    app = Application()
    app.run()

if __name__ == '__main__':
    main()
