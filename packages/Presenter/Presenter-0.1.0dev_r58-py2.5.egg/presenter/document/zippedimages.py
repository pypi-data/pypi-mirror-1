from presenter.document.base import Document, Page

import zipfile
import gtk.gdk

class ZippedImagePage(Page):
    def __init__(self, zipfile, filename, *args, **kwargs):
        super(ZippedImagePage, self).__init__(filename, *args, **kwargs)

        self.filename = filename
        self.zipfile = zipfile

        self.image = None

    def render(self, context, width, height):
        # Cache images.
        if self.image is None:
            imgstr = self.zipfile.read(self.filename)
            loader = gtk.gdk.PixbufLoader()
            loader.write(imgstr)
            loader.close()
            self.image = loader.get_pixbuf()

        dest_width = float(width)
        dest_height = float(height)

        img_width = float(self.image.get_width())
        img_height = float(self.image.get_height())

        image_aspect = img_width / img_height
        box_aspect = dest_width / dest_height

        if image_aspect < box_aspect:
            # Gap on sides.
            dest_width = height * image_aspect
        else:
            # Gap on top/bottom.
            dest_height = width / image_aspect

        pixbuf = self.image.scale_simple(int(dest_width), int(dest_height),
                                         gtk.gdk.INTERP_BILINEAR)

        # Draw the pixbuf onto the cairo context.
        x = (width - dest_width) / 2.0
        y = (height - dest_height) / 2.0

        context.set_source_pixbuf(pixbuf, x, y)
        context.paint()

class ZippedImageDocument(Document):
    type_name = 'Zipped images'
    file_types = ['zip']

    def __init__(self, filename, *args, **kwargs):
        super(ZippedImageDocument, self).__init__(filename, *args, **kwargs)

        zip = zipfile.ZipFile(filename)

        for filename in sorted(zip.namelist()):
            page = ZippedImagePage(zip, filename)
            self.pages.append(page)

