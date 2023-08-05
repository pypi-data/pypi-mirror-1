#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Resize all JPEG images in a directory, writing them to another directory."""

from __future__ import with_statement
from glob import iglob
from optparse import OptionParser
import os
from sys import exit

from gallerize.gallerize import resize_image


if __name__ == '__main__':
    # Parse command-line arguments.
    parser = OptionParser(usage='%prog <source path> <target path>')
    parser.add_option('-s', '--size', dest='size', default='1024,1024',
         help='set the maximum size [default: 1024,1024]')
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

    # Check target directory and create it.
    if os.path.exists(target_path):
        exit('Target directory already exists, aborting.')
    os.mkdir(target_path)

    # Find all images in the source directory and resize them.
    for image in iglob(os.path.join(src_path, '*.JPG')):
        image_basename = os.path.basename(image)
        resize_image(src_path, image_basename, target_path, image_basename,
            size)
    
