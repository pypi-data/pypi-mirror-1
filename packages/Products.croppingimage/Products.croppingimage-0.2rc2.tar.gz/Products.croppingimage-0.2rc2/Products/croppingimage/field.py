# Standard library imports
from cStringIO import StringIO
from types import StringType, DictType

# Archetypes imports
from Products.Archetypes.Field import ImageField, HAS_PIL, shasattr

# PIL imports
if HAS_PIL:
    import PIL


_marker = []

class CroppingImageField(ImageField):
    """XXX Document me!
    """
    _properties = ImageField._properties.copy()
    _properties.update({
        #'original_size': None,
        #'max_size': None,
        #'sizes' : {'thumb':(80,80)},
        'long_edge_size' : 600,
        'short_edge_size' : 400,
        'force_format': None,
        })

    def _resize(self, imagestrio, dwidth, dheight):
        #data, format = self.scale(imagestrio.read(), dwidth, dheight)
        # Parse data to an image again...
        imagestrio.seek(0)
        image = PIL.Image.open(imagestrio)
        format = image.format
        size=( int(dwidth), int(dheight) )
        image = image.resize(size=size)
        image.load()
        # We need to find out the new dimensions
        width, height = image.size
        data = StringIO()
        image.save(data, format)
        image.format = format
        data.seek(0)
        return data, image, width, height

    def rescaleOriginal(self, value, **kwargs):
        """rescales the original image and sets the data

        for self.original_size or self.max_size
        
        value must be an OFS.Image.Image instance
        """
        if not HAS_PIL:
            return data
        data = StringIO(str(value.data))
        image = PIL.Image.open(data)
        data.seek(0)
        width, height = image.size
        
        #check if any format is forced
        if self.force_format == 'landscape':
            is_landscape = True
        elif self.force_format == 'portrait':
            is_landscape = False
        else:
            # Figure out which way our image is oriented
            is_landscape = False
            if width >= height:
                is_landscape = True

        is_portrait = not is_landscape
        # Store this variable for use in other methods, like getAvailableSizes
        self.is_landscape = is_landscape
        # Apply the long and short edge settings to the correct dimensions
        if is_landscape:
            desired_width = self.long_edge_size
            desired_height = self.short_edge_size
        else:
            desired_width = self.short_edge_size
            desired_height = self.long_edge_size
        aspect_ratio = float(height) / float(width)
        desired_ratio = float(desired_height) / float(desired_width)
        if desired_ratio == aspect_ratio:
            # (Miraculously) The ratio is correct
            # Do we need to resize?
            if width != desired_width:
                # Yup, do the resize
                dwidth = desired_width
                dheight = desired_height
                data, image, width, height = self._resize(data, dwidth, dheight)
        elif is_landscape and desired_ratio < aspect_ratio:
            # Landscape is too tall
            # width is the short edge
            dwidth = desired_width
            dheight = desired_width*aspect_ratio
            data, image, width, height = self._resize(data, dwidth, dheight)
        elif is_landscape and desired_ratio > aspect_ratio:
            # Landscape is too short
            # height is the short edge
            dwidth = desired_height/aspect_ratio
            dheight = desired_height
            data, image, width, height = self._resize(data, dwidth, dheight)
        elif is_portrait and desired_ratio > aspect_ratio:
            # Portrait is too short
            # height is the short edge
            dwidth = desired_height/aspect_ratio
            dheight = desired_height
            data, image, width, height = self._resize(data, dwidth, dheight)
        elif is_portrait and desired_ratio < aspect_ratio:
            # Portrait is too tall
            # width is the short edge
            dwidth = desired_width
            dheight = desired_width*aspect_ratio
            data, image, width, height = self._resize(data, dwidth, dheight)
        # Crop if to tall...
        if height > desired_height:
            # Calculate how many pixels need to be removed from the height
            diff = height - desired_height
            # Remove them, half from top, half from bottom
            top_left = ( 0, diff/2 )
            bottom_right = ( width, height-(diff/2) )
            data, format = self.crop(image,
                                     top_left=top_left,
                                     bottom_right=bottom_right,
                                     default_format=image.format)
        # ... or too wide
        elif width > desired_width:
            # Calculate how many pixels need to be removed from the width
            diff = width - desired_width
            # Remove them, half from each side
            top_left = ( diff/2, 0 )
            bottom_right = ( width-(diff/2), height )
            # Perform the crop
            data, format = self.crop(image,
                                     top_left=top_left,
                                     bottom_right=bottom_right,
                                     default_format=image.format)
        # Return the raw image string
        data.seek(0)
        return data.read()

    def crop(self, data, top_left=(0,0), bottom_right=None, default_format='PNG'):
        """Crop out a box from the image, defined by the co-ordinates of
        bottom_left and top_right.
        
        Return that box.
        """
        if bottom_right is None:
            msg = "Must provide a 'bottom_right' two-tuple of co-ordinates for the crop box."
            raise Exception(msg)
        if isinstance(data, PIL.Image.Image):
            image = data
        else:
            original_image = StringIO(data)
            image = PIL.Image.open(original_image)
        format = image.format
        box = (top_left[0], top_left[1], bottom_right[0], bottom_right[1])
        new_image = image.crop(box=box)
        new_image.load()
        #image = new_image
        cropped_output = StringIO()
        format = format and format or default_format
        new_image.save(cropped_output, format, quality=self.pil_quality)
        cropped_output.seek(0)
        return cropped_output, format.lower()

    def getAvailableSizes(self, instance):
        """Get sizes

        Supports:
            self.sizes as dict
            A method in instance called like sizes that returns dict
            A callable
        """
        # Do essentially the same as ImageField.getAvailableSizes(...)
        sizes = self.sizes
        if type(sizes) is DictType:
            pass
        elif type(sizes) is StringType:
            assert(shasattr(instance, sizes))
            method = getattr(instance, sizes)
            data = method()
            assert(type(data) is DictType)
            sizes = data
        elif callable(sizes):
            sizes = sizes()
        elif sizes is None:
            sizes = {}
        else:
            raise TypeError, 'Wrong self.sizes has wrong type: %s' % type(sizes)
        # But now go over the dictionary, changing the order of the size two-tuples
        # to reflect whether we have a landscape- or portrait-oriented image.
        try:
            is_landscape = self.is_landscape
        except AttributeError:
            # No is_landscape attribute, so just return the sizes
            # XXX Should probably log a debug message here!
            return sizes
        for key in sizes.keys():
            width, height = sizes[key]
            if (is_landscape and width < height) or \
               (not is_landscape and width > height):
                # Swap them around so the larger dimension applies to the width
                sizes[key] = (height, width)
        return sizes
