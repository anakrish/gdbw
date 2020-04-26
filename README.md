# gdbw
A `TUI (Text User Interface)` for `gdb` using [Python Prompt Toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit)

# Screenshots
![](images/screenshot_000.png)

# Installation

Clone the repository:
```bash
$ git clone https://github.com/anakrish/gdbw.git
```

**Prepend** gdbw root folder to `PATH` and make sure that `gdbw/gdb` appears before `/usr/bin/gdb`:
```bash
$ export PATH=~/gdbw:$PATH
$ which -a gdbw
~/gdbw/gdb
/usr/bin/gdb
```

# Run

Running `gdb` will automatically launch `gdbw`.

# Commands

   Keys              |          Action
---------------------|-----------------------------
`Ctrl-x 1`           | Show source code and console
`Ctrl-x 2`           | Show source code, disassembly and console
`Ctrl-x a`           | Show only console
`Ctrl-x b`           | Toggle show breakpoints
`Ctrl-x c`           | Toggle show callstack
`Ctrl-x d`           | Toggle show disassembly
`Ctrl-x r`           | Toggle show registers
`Ctrl-x s`           | Toggle show source
`Ctrl-x t`           | Toggle show threads
`Ctrl-x v`           | Toggle show variables (arguments and locals)
`Ctrl-up`            | Enter copy mode in console
`Ctrl-c`             | Exit copy mode or send interrupt to program
`Shift-left`         | Focus previous window

# Scrolling

Any window other than the console can be scrolled up or down by hovering the mouse
in the window and using a scroll gesture or mouse wheel.

The console can be scrolled by entering `copy mode` by pressing `Ctrl-up`.

# Selection

Any widow can be selected by double-clicking.