#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gallerize
~~~~~~~~~

Create a static XHTML/CSS image gallery from a bunch of images.

Features:

- Makes use of the great `Python Imaging Library`_ to create smooth thumbnails.

  - A separate script to resize a bunch of images is included.

- Uses clean, slim XHTML and CSS. Hence, it can easily be themed.

- Provides access keys for easy navigation.

- Comes with a little bit of animation, provided by `jQuery`_.

Python 2.5 or greater is required.

.. _Python Imaging Library:     http://www.pythonware.com/products/pil/
.. _jQuery:                     http://jquery.com/
"""

# Note: The code assumes images have the '.JPG' extension which is fine for my
#       purposes (processing images from my digital camera). If you want
#       lowercase extensions or other formats like PNG or GIF to be included,
#       you have to change the corresponding code. 

from __future__ import with_statement
from glob import iglob
from optparse import OptionParser
import os
from shutil import copy
from sys import exit

from genshi.template import TemplateLoader
# Optimized import.
import Image
import JpegImagePlugin
Image._initialized = 1


__author__ = 'Jochen Kupperschmidt'
__date__ = '11-Aug-2007'
__docformat__ = 'restructuredtext'
__license__ = 'MIT <http://www.opensource.org/licenses/mit-license.php>'
__url__ = 'http://homework.nwsnet.de/'
__version__ = '0.1'


PATH = os.path.dirname(os.path.abspath(__file__))
PATH_STATIC = os.path.join(PATH, 'static')
PATH_TEMPLATES = os.path.join(PATH, 'templates')


def debug(msg):
    print msg

def make_thumbnail_fn(fn):
    name, ext = os.path.splitext(fn)
    return name + '_t' + ext

def make_xhtml_fn(fn):
    return os.path.splitext(fn)[0] + '.html'

def resize_image(src_path, src_fn, target_path, target_fn, size):
    """Create a resized (and antialiased)version of an image."""
    debug('Processing %s...' % src_fn)
    im = Image.open(os.path.join(src_path, src_fn))
    im.thumbnail(size, Image.ANTIALIAS)
    im.save(os.path.join(target_path, target_fn))

def render_xhtml(name, vars):
    """Render and serialize the template and return the resulting string."""
    loader = TemplateLoader([PATH_TEMPLATES], variable_lookup='strict')
    stream = loader.load(name + '.html').generate(**vars)
    return stream.render('xhtml').strip()


class Gallery(object):

    def __init__(self, path, title):
        self.path = path
        self.images = map(os.path.basename, iglob(os.path.join(path, '*.JPG')))
        self.images.sort()
        self.title = title

    def create_thumbnail(self, src_fn, size, target_path):
        """Create a thumbnail from an image."""
        thumbnail_fn = make_thumbnail_fn(src_fn)
        resize_image(self.path, src_fn, target_path, thumbnail_fn, size)
        return thumbnail_fn

    def get_neighbors(self, image):
        """Return the images filenames before and after the given one."""
        pos = self.images.index(image)
        prev = (self.images[pos - 1] if (pos > 0) else None)
        next = (self.images[pos + 1] if (pos < (len(self.images) - 1)) else None)
        return prev, next

    def create_index_page(self, thumbnails, target_path):
        """Create XHTML index page."""
        xhtml = render_xhtml('index',
            dict(title=self.title, thumbnails=thumbnails))
        with open(os.path.join(target_path, 'index.html'), 'wb') as f:
            debug('Writing XHTML index page...')
            f.write(xhtml)



def gallerize(src_path, target_path, title, size):
    # Create target path if it doesn't exist.
    if not os.path.exists(target_path):
        os.mkdir(target_path)

    gallery = Gallery(src_path, title)

    # Process images.
    thumbnails = []
    for image in gallery.images:
        # Copy image.
        copy(os.path.join(src_path, image), os.path.join(target_path, image))

        # Create thumbnail.
        thumbnail_fn = gallery.create_thumbnail(image, size, target_path)

        # Create single picture page XHTML.
        xhtml_fn = make_xhtml_fn(image)
        context = dict(title=title, filename=image)
        prev_img, next_img = gallery.get_neighbors(image)
        if prev_img:
            context['prev_page'] = make_xhtml_fn(prev_img)
        if next_img:
            context['next_page'] = make_xhtml_fn(next_img)
        xhtml = render_xhtml('view', context)
        with open(os.path.join(target_path, xhtml_fn), 'wb') as f:
            debug('Writing XHTML page %s...' % xhtml_fn)
            f.write(xhtml)

        thumbnails.append((thumbnail_fn, xhtml_fn))

    gallery.create_index_page(thumbnails, target_path)

    # Copy additional static files.
    target_static_path = os.path.join(target_path, 'style')
    os.mkdir(target_static_path)
    for fn in os.listdir(PATH_STATIC):
        debug('Copying %s...' % fn)
        copy(os.path.join(PATH_STATIC, fn),
            os.path.join(target_static_path, fn))

    debug('Done.')

def main():
    # Parse command-line arguments.
    parser = OptionParser(
        usage='%prog [options] <image source path> <gallery target path>')
    parser.add_option('-s', '--size', dest='size', default='120,120',
         help='set the maximum thumbnail size [default: 120,120]')
    parser.add_option('-t', '--title', dest='title', default='Gallery',
         help='set the gallery title')
    opts, args = parser.parse_args()
    try:
        src_path, target_path = args
    except ValueError:
        parser.print_help()
        parser.exit()
    try:
        size = map(int, opts.size.split(',', 1))
    except ValueError:
        parser.error('Size must be two comma-separated numbers.')
    try:
        gallerize(args[0], args[1], opts.title, size)
    except KeyboardInterrupt:
        exit('Ctrl-C pressed, aborting.')


if __name__ == '__main__':
    main()
