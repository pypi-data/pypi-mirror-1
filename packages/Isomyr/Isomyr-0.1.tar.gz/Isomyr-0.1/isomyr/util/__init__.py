import os
from glob import glob

from pygame import image


class ImageLoader(object):

    def __init__(self, basedir=".", transparency=None):
        self.basedir = os.path.abspath(basedir)
        self.transparency = transparency

    def load(self, image_names=None, image_glob=None):
        """Loads a list of images.

        image_names: The filenames of the images to load: list of string
        """
        if image_glob and not image_names:
            match = os.path.join(self.basedir, image_glob)
            image_names = sorted(glob(match))
        elif not isinstance(image_names, list):
            image_names = [image_names]
        images = []
        for file_name in image_names:
            full_path = os.path.join(self.basedir, file_name)
            loaded_image = image.load(full_path).convert()
            # Load images using a colorkey transparency, if provided.
            if self.transparency:
                loaded_image.set_colorkey(self.transparency)
            images.append(loaded_image)
        return(images)
