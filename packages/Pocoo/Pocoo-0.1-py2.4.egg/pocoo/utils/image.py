# -*- coding: utf-8 -*-
"""
    pocoo.utils.image
    ~~~~~~~~~~~~~~~~~

    Basic Image Manipulation

    :copyright: 2006 by Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""
from __future__ import division
from colubrid.utils import FieldStorage
from pocoo.exceptions import PocooRuntimeError
from cStringIO import StringIO
from subprocess import Popen, PIPE
try:
    from PIL import Image
except ImportError:
    pil_installed = False
else:
    pil_installed = True


class _IMNotFound(Exception):
    pass


def is_supported_image(fp_or_data):
    """
    Check if the filetype is supported for resizing via
    `resize_image`.
    """
    if isinstance(fp_or_data, FieldStorage):
        fp = StringIO(fp_or_data.data)
    elif isinstance(fp_or_data, str):
        fp = StringIO(fp_or_data)
    else:
        fp = fp_or_data
    if pil_installed:
        try:
            Image.open(fp)
        except IOError, e:
            print e
            return False
        return True
    try:
        child = Popen(['identify', '-'], stdout=PIPE, stdin=PIPE,
                      stderr=PIPE)
        child.stdin.write(fp.read())
        child.stdin.close()
        child.stdout.close()
        child.stderr.close()
        return child.wait() == 0
    except (OSError, IOError):
        return False


def resize_image(fp_or_data, width, height=None,
                 filetype='image/png'):
    """
    Return a thumbnail of ``fp_or_data``.
    """
    if filetype not in ('image/png', 'image/gif', 'image/jpeg'):
        raise ValueError('unsupported mimetype %r' % filetype)
    if isinstance(fp_or_data, FieldStorage):
        fp = StringIO(fp_or_data.data)
    elif isinstance(fp_or_data, str):
        fp = StringIO(fp_or_data)
    else:
        fp = fp_or_data
    if pil_installed:
        return _resize_pil(fp, width, height or width, filetype)
    try:
        return _resize_im(fp, width, height or width, filetype)
    except _IMNotFound:
        raise PocooRuntimeError('neither ImageMagick nor PIL found')


def _resize_pil(fp, width, height, filetype):
    """
    Resize an Image using PIL. Don't call this function
    directly, it's just a helper for `resize_image`.
    """
    image = Image.open(fp)
    (x, y) = image.size
    if x > width and y > height:
        lfx = width / x
        lfy = height / y
        lf = min(lfx, lfy)
    elif x > width:
        lf = width / x
    elif y > height:
        lf = height / y
    else:
        lf = 1
    nx = int(x * lf)
    ny = int(y * lf)
    result = image.resize((nx, ny), Image.ANTIALIAS)
    fp.close()
    out = StringIO()
    if filetype == 'image/jpeg':
        result.save(out, 'JPEG', quality=80)
    elif filetype == 'image/png':
        result.save(out, 'PNG', optimize=True)
    else:
        result.save(out, 'GIF')
    return out.getvalue()


def _resize_im(fp, width, height, filetype):
    """
    Resize an image using ImageMagick. Don't call this function
    directly, it's just a helper for `resize_image`.
    """
    filetype = {
        'image/png':    'png',
        'image/gif':    'gif',
        'image/jpeg':   'jpeg'
    }[filetype]
    try:
        child = Popen(['convert', '-', '-resize', '%dx%d' % (width, height),
                       '%s:-' % filetype],
                      stdin=PIPE, stdout=PIPE, stderr=PIPE)
    except OSError, e:
        if e.errno == 2:
            raise _IMNotFound()
        raise
    child.stdin.write(fp.read())
    child.stdin.close()
    result = child.stdout.read()
    child.stdout.close()
    child.stderr.close()
    return result
