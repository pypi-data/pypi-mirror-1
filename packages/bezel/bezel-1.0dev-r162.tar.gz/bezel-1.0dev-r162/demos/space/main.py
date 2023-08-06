#!/usr/bin/env python

import os, sys; os.chdir(os.path.dirname(sys.argv[0]))

from bezel.graphics.display import Display

import bezel.resources

from title import TitleScene

def main():
    bezel.resources.index('data')

    display = Display('Generic Space Game',
                      icon='data/logo32.png')
    display.add(TitleScene())
    display.run()

if __name__ == '__main__':
    try:
        import psyco
        psyco.full()
    except ImportError: pass

    main()

