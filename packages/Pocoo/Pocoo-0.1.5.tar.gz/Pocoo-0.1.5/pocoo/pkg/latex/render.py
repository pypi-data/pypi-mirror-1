# -*- coding: utf-8 -*-
"""
    pocoo.pkg.latex.render
    ~~~~~~~~~~~~~~~~~~~~~~

    Render LaTeX and create images. Needs dvipng.
    And documentation.


    :copyright: 2006 by Georg Brandl.
    :license: GNU GPL, see LICENSE for more details.
"""

import sha, os
from os import path
import tempfile
import shutil


#: The skeleton in which to wrap the LaTeX markup.
DOCUMENT = r'''
\documentclass{article}
\usepackage[utf-8]{inputenc}
\usepackage{amsmath}
\usepackage{amsthm}
\usepackage{amssymb}
\usepackage{amsfonts}
\usepackage{bm}
\pagestyle{empty}
\begin{document}
\[ %s \]
\end{document}
'''

#: A list of LaTeX commands that aren't allowed in the markup.
BLACKLIST = ('include', 'def', 'command', 'loop', 'repeat',
             'open', 'toks', 'output', 'line', 'input', 'catcode',
             'mathcode', 'name', 'item', 'section')


class LatexRender(object):

    def __init__(self, fmlpath):
        self.fmlpath = fmlpath
        if not path.isdir(fmlpath):
            os.makedirs(fmlpath)

    def render(self, fml):
        """
        Render ``fml`` as LaTeX math mode markup and return a tuple
        ``(filename of PNG file, error message)``.
        """
        shasum = sha.new(fml).hexdigest()
        fn = "%s.png" % shasum
        fnpath = path.join(self.fmlpath, fn)

        if path.isfile(fnpath):
            return fn, ''

        # security measures
        for cmd in BLACKLIST:
            if "\\" + cmd in fml:
                return '', 'the %s command is blacklisted' % cmd
        if '^^' in fml or '\\$\\$' in fml:
            return '', '^^ and $$ are blacklisted'
        if len(fml) > 1000:
            return '', 'formula exceeds 1000 characters'

        fml = fml.replace("\n", "\\]\n\\[")

        tex = DOCUMENT % fml

        tf, texfile = tempfile.mkstemp('.tex')
        os.write(tf, tex)
        os.close(tf)

        basename = texfile[:-4]
        dirname = path.dirname(basename)

        ret = os.system('latex --interaction=nonstopmode --output-directory="%s" %s' %
                        (dirname, texfile))
        if ret != 0:
            self._cleanup(basename)
            return '', 'latex failed'

        cmd = "dvipng -T tight -x 1200 -z 9 -bg transparent " \
              + "-o %s.png %s.dvi" % (basename, basename)
        ret = os.system(cmd)
        if ret != 0:
            self._cleanup(basename)
            return '', 'dvipng failed'

        shutil.copyfile(basename+'.png', fnpath)
        self._cleanup(basename)
        return fn, ''

    def _cleanup(self, basename):
        """Delete temporary files."""
        for suffix in '.tex', '.aux', '.log', '.dvi', '.png':
            try:
                os.unlink(basename + suffix)
            except: pass
        return ''
