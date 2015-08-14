from PIL import Image
import os
from django.conf import settings


def make_image_sizes(filename):

    file, ext = os.path.splitext(filename)

    original = Image.open(filename)
    sizes = settings.IMAGE_SIZES
    for image_type in sizes:
        newimage = original.copy()
        newimage.thumbnail(image_type[1])
        newimage.save(file + "_" + image_type[0] + ext)
