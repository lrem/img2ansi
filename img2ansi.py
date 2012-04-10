#!/usr/bin/env python
# -*- encoding: utf-8 -*

#
#   Copyright (c) 2011 Jakub Szafrański <samu@pirc.pl>
# 
#  All rights reserved.
# 
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions
#  are met:
#  1. Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#  2. Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
# 
#  THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND
#  ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#  ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE
#  FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#  DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
#  OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
#  HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
#  LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
#  OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#  SUCH DAMAGE.
#

"""
img2ansi - a simple image to coloured ASCII-art converter
"""

import sys
try:
    import Image
except:
    # Image is part of PIL and in my setup has to be imported like that
    from PIL import Image
import rgb256
import random

def tohex((r,g,b)):
    hexchars = "0123456789ABCDEF"
    return hexchars[r/16]+hexchars[r%16]+hexchars[g/16]+hexchars[g%16]+hexchars[b/16]+hexchars[b%16]

cprefix = "\033"

import argparse

parser = argparse.ArgumentParser(
        description = __doc__)
parser.add_argument('image', help = "the input image file")
parser.add_argument('width', help = "width of resulting art", type = int)
parser.add_argument('height', help = "height of resulting art", type = int)
parser.add_argument('--ansichar', default="0", 
        help = "the character used as the foreground of the output."
               "ignored when ascii is set to true (default: 0)")
parser.add_argument('--ansipalette', 
        default = ".,-_ivc=!/|\\~gjez2]/(YL)t[+T7VfmdK4ZGbNDXY5P*QW8KMA""#%$",
        help = "the palette of ascii characters that will be used"
               " if ansichar=random.")
parser.add_argument('--bgcolor', default = "0",
        help = "HEX representation of a color (without the leading '#' that"
               " will be transparent in the output (replaced by a whitespace.")
parser.add_argument('--ascii', action = 'store_true',
        help = "if set to true, the luminosity will be represented by"
               " a ascii character with a similar 'optical weight'.")
parser.add_argument('--randomansi', action = 'store_true',
        help = "will use a random character from ansipalette, instead of the"
               " ansichar value")
parser.add_argument('--echo', action = 'store_true',
        help = "if set to true, the output will converted to a string which"
               " can be copied into other print/echo commands.")
parser.add_argument('--revert', action = 'store_true',
        help = "if set to true, the greyscale charset collection will be"
               " reverted (might look better on brighter images).")
args = parser.parse_args()

img, width, height = args.image, args.width, args.height

# I'm too lazy to think about these 2.
_o = {}
args.o_echo = 0
args.bgcolor = args.bgcolor.upper()

if args.echo:
    cprefix="\\033"

try:
    im = Image.open(sys.argv[1])
except:
    print "Error while opening file %s" % sys.argv[1]

im = im.resize((width, height), Image.BILINEAR)

    
if args.ascii:
    from bisect import bisect
    greyscale = [
                " ",
                " ",
                ".,-",
                "_ivc=!/|\\~",
                "gjez2]/(YL)t[+T7Vf",
                "mdK4ZGbNDXY5P*Q",
                "W8KMA",
                "#%$"
                ]
    zonebounds=[36,72,108,144,180,216,252]
    im2 = Image.open(sys.argv[1])
    im2 = im2.resize((width, height), Image.BILINEAR)
    im2 = im2.convert("L")

if args.revert:
    greyscale.reverse()


for y in range(0, im.size[1]):
    line = ""
    for x in range(0, im.size[0]):
        hexcolor = tohex(im.getpixel( (x,y) ))
        if (hexcolor != args.bgcolor):
            if args.randomansi:  
                args.ansichar = args.ansipalette[random.randint(0,len(args.ansipalette)-1)]
            color = str(rgb256.rgb_to_256(hexcolor)).strip()
            if args.ascii:
                lum = 255 - im2.getpixel((x,y))
                row = bisect(zonebounds,lum)
                possibles = greyscale[row]
                args.ansichar = possibles[random.randint(0,len(possibles)-1)]
            line += cprefix+"[38;5;"+color+"m"+args.ansichar+"\033[0;0;0m"
        else:
            line += " "
    print line
