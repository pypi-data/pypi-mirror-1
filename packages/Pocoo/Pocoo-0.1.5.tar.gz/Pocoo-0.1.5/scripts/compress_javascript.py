#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Compress Javascript
    ~~~~~~~~~~~~~~~~~~~

    Uses the dojo rhino compressor to create on small javascript
    file.

    :copyright: 2006 by Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""
import pocoo
import optparse
from pocoo.utils.path import Path
from subprocess import Popen, PIPE

def main():
    parser = optparse.OptionParser()
    register = parser.add_option
    register('-p', '--to-stdout', action='store_true', dest='to_stdout',
             help='print compressed script to stdout instead of writing file.')
    register('-r', '--remove-existing', action='store_true', dest='remove',
             help='remove existing compressed lib and exit')
    register('-n', '--save-newlines', action='store_true', dest='newlines',
             help='Doesn\'t remove newline chars.')
    args, options = parser.parse_args()
    if args.remove:
        remove()
    else:
        compress(args.to_stdout, args.newlines)


def compress(to_stdout, save_newline):
    result = []
    rhino_cmd = ['java', '-jar',
                 Path(__file__).joinpath('../../pocoo/res/dojo_rhino.jar')
                     .realpath().__str__(), '-c']
    root = Path(pocoo.__file__).joinpath('../lib').realpath()
    for fn in root.walk('*.js'):
        cmd = rhino_cmd + [str(fn)]
        rhino = Popen(cmd, stdout=PIPE)
        src = rhino.stdout.read()
        if save_newline:
            result.append(src)
        else:
            lines = src.splitlines()
            result.append(''.join(lines))
        rhino.stdout.close()
    src = ''.join(result)
    if to_stdout:
        print src
    else:
        out = str(root.joinpath('compressed.js'))
        fp = file(out, 'w')
        fp.write(src)
        fp.close()
        print 'compressed file written to %r' % str(out)


def remove():
    fn = Path(pocoo.__file__).joinpath('../lib/compressed.js').realpath()
    if fn.exists():
        fn.remove()
        print 'removed compressed package.'
    else:
        print 'no package found'


if __name__ == '__main__':
    main()
