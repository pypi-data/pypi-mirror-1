#!/usr/bin/env python

import sys
from PIL import Image

def crop_resize(image, size, exact_size=False):
    """
    Crop out the proportional middle of the image and set to the desired size.
    If the image is bigger than the sizes passed, this works as expected.
    If the image is smaller than the sizes passed, then behavior is dictated
    by the `exact_size` flag.  If the 

    """
    assert size[0] or size[1]

    size = list(size)

    image_ar = image.size[0]/float(image.size[1])
    crop = size[0] and size[1]
    if not size[1]:
        size[1] = int(image.size[1]*size[0]/float(image.size[0]) )
    if not size[0]:
        size[0] = int(image.size[0]*size[1]/float(image.size[1]) )
    size_ar = size[0]/float(size[1])

    if size[0] > image.size[0]:
        if size[1] > image.size[1]:
            if not exact_size:
                return image
        else:
            pass
            # raise NotImplementedError
    elif size[1] > image.size[1]:
        pass
    
    if crop:
        if image_ar > size_ar:
            # trim the width
            xoffset = int(0.5*(image.size[0] - size_ar*image.size[1]))
            image = image.crop((xoffset, 0, image.size[0]-xoffset, image.size[1]))
        elif image_ar < size_ar:
            # trim the height
            yoffset = int(0.5*(image.size[1] - image.size[0]/size_ar))
            image = image.crop((0, yoffset, image.size[0], image.size[1] - yoffset))

    return image.resize(size, Image.ANTIALIAS)

def main():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-W', '--width')
    parser.add_option('-H', '--height')
    parser.add_option('-e', '--exact-size', dest='exact', action='store_true', default=False)
    (options, args) = parser.parse_args()

    if not args:
        parser.print_help()
        sys.exit()

    width = int(options.width)
    height = int(options.height)

    for arg in args:
        image = Image.open(arg)
        new_image = crop_resize(image, (width, height), options.exact)
        new_image.show()

if __name__ == '__main__':
    main()
