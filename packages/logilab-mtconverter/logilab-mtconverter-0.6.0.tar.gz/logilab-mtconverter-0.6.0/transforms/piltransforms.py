"""PIL based transformations for images"""

from StringIO import StringIO

from PIL import Image

from logilab.mtconverter.transform import Transform

class PILTransform(Transform):

    format = None # override in subclasses (make pylint happy)
    
    def _convert(self, trdata):
        newwidth = trdata.get('width', None)
        newheight = trdata.get('height', None)
        pilimg = Image.open(StringIO(trdata.data))
        if self.format in ['jpeg', 'ppm']:
            pilimg.draft("RGB", pilimg.size)
            pilimg = pilimg.convert("RGB")
        if newwidth or newheight:
            pilimg.thumbnail((newwidth, newheight), Image.ANTIALIAS)
        stream = StringIO()
        pilimg.save(stream, self.format)
        return stream.getvalue()


class image_to_gif(PILTransform):
    name = "image_to_gif"
    inputs = ('image/*', )
    output = 'image/gif'
    format = 'gif'

class image_to_bmp(PILTransform):
    name = "image_to_bmp"
    inputs = ('image/*', )
    output = 'image/x-ms-bmp'
    format = 'bmp'

class image_to_jpeg(PILTransform):
    name = "image_to_jpeg"
    inputs = ('image/*', )
    output = 'image/jpeg'
    format = 'jpeg'

class image_to_pcx(PILTransform):
    name = "image_to_pcx"
    inputs = ('image/*', )
    output = 'image/pcx'
    format = 'pcx'

class image_to_png(PILTransform):
    name = "image_to_png"
    inputs = ('image/*', )
    output = 'image/png'
    format = 'png'

class image_to_ppm(PILTransform):
    name = "image_to_ppm"
    inputs = ('image/*', )
    output = 'image/x-portable-pixmap'
    format = 'ppm'

class image_to_tiff(PILTransform):
    name = "image_to_tiff"
    inputs = ('image/*', )
    output = 'image/tiff'
    format = 'tiff'

transform_classes = [c for c in globals().values()
                     if isinstance(c, type) and issubclass(c, PILTransform)
                     and not c is PILTransform]
