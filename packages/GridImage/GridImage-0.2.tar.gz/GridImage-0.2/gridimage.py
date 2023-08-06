#!/usr/bin/env python
"""

gridimg.py - command-line grid image generator.

Time-stamp: <2009-06-16 10:15:03 carljm gridimg.py>

"""
import sys
from optparse import OptionParser

usage = "usage: %prog [options] line-height column-width gutter-width"
parser = OptionParser(usage=usage)
parser.add_option("-g", "--gutter-color", dest="gutter_color",
                  default="#fcc",
                  help="use COLOR for gutter line (default #fcc)",
                  metavar="COLOR")
parser.add_option("-b", "--baseline-color", dest="baseline_color",
                  default="#999",
                  help="use COLOR for text baseline (default #999)",
                  metavar="COLOR")
parser.add_option("-f", "--output-file", dest="output_file",
                  default="grid_%l_%c_%g.png",
                  help="output grid image to FILE "
                  "(format autodetected from extension) "
                  "%l, %c, %g replaced with line-height, col-width, gutter-width "
                  "(default grid_%l_%c_%g.png)",
                  metavar="FILE")

def main():
    try:
        from PIL import Image, ImageDraw
        from PIL.ImageColor import getrgb
    except ImportError:
        print "Error: %s requires Python Imaging Library."
        print
        sys.exit(1)

    (options, args) = parser.parse_args()

    try:
        height, column, gutter = (int(i) for i in args)
    except ValueError:
        print "Error: line-height, column-width, and gutter-width are required."
        print "       All three must be integers."
        print
        parser.print_help()
        sys.exit(1)

    try:
        b_color = getrgb(options.baseline_color) + (255,)
    except ValueError:
        print "Error: Invalid baseline color '%s'." % (options.baseline_color,)
    try:
        g_color = getrgb(options.gutter_color) + (255,)
    except ValueError:
        print "Error: Invalid gutter color '%s'." % (options.gutter_color,)

    width = column + gutter

    trans_color = (0, 0, 0, 0)

    im = Image.new("RGBA", (width, height), trans_color)
    draw = ImageDraw.Draw(im)

    draw.rectangle(((width - gutter, 0), (width, height)), fill=g_color)
    draw.line(((0, height - 1), (width, height - 1)), fill=b_color)

    output_file = options.output_file.replace(
        '%l', str(height)).replace('%c', str(column)).replace('%g', str(gutter))

    im.save(output_file)

if __name__ == '__main__':
    main()
