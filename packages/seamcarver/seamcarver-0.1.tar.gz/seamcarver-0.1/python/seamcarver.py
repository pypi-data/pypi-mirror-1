#!/usr/bin/python

__all__ = ('SeamCarver', 'retarget_image')

from ctypes import create_string_buffer, POINTER, c_ubyte, cast, c_char
from _seamcarver import *

class SeamCarver(object):
    def __init__(self, rgb_data, width, height, energy_function):
        rgb_data = cast(create_string_buffer(rgb_data), POINTER(c_ubyte))
        self._sc = seamcarver_new(rgb_data, width, height, energy_function)
        self._width = width
        self._height = height
    def get_rgb_data(self):
        rgb_data = cast(seamcarver_get_rgb_data(self._sc), POINTER(c_char))
        return rgb_data[:3*self._width*self._height]
    def get_energy_data(self):
        energy = cast(seamcarver_get_energy_data(self._sc), POINTER(c_char))
        return energy[:3*self._width*self._height]
    def retarget(self, new_width, new_height):
        rgb_data = cast(seamcarver_retarget(self._sc, new_width, new_height),
                        POINTER(c_char))
        self._width = new_width
        self._height = new_height
        return rgb_data[:3*new_width*new_height]

def retarget_image(image, new_width, new_height):
    mode = image.mode
    if mode != 'RGB':
        image = image.convert(mode='RGB')
    width, height = im.size
    sc = SeamCarver(image.tostring(), width, height, 0)
    rgb_data = sc.retarget(new_width, new_height)
    image = Image.fromstring('RGB', (new_width, new_height), rgb_data)
    if mode != 'RGB':
        image = image.convert(mode=mode)
    return image

if __name__=='__main__':
    import sys
    import Image
    try:
        infile, outfile, new_width, new_height = sys.argv[1:]
        new_width, new_height = int(new_width), int(new_height)
    except ValueError:
        import os
        print 'Usage:'
        print '   %s inputimage outputimage new_widht new_height' \
              % os.path.basename(sys.argv[0])
        sys.exit(2)
    im = Image.open(infile)
    im = retarget_image(im, new_width, new_height)
    im.save(outfile)
