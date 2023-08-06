from cStringIO import StringIO

import gtk.gdk
import gobject

import cairo

class DocumentStore(gtk.ListStore):
    def __init__(self, document):
        super(DocumentStore, self).__init__(gobject.TYPE_STRING,
                                            gtk.gdk.Pixbuf)

        self.document = document

        for page in self.document:
            self.append(page)

        self.document.connect('item-append', self.append)
        self.document.connect('item-insert', self.insert)
        self.document.connect('item-remove', self.remove)

    def page_to_record(self, page):
        width = height = 64

        # Render page onto cairo context.
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        context = gtk.gdk.CairoContext(cairo.Context(surface))
        page.render(context, width, height)
        context.paint()

        # Write ImageSurface data to Pixbuf loader
        data = StringIO()
        surface.write_to_png(data)

        loader = gtk.gdk.PixbufLoader()
        loader.write(data.getvalue())
        loader.close()

        return (page.title, loader.get_pixbuf())

    def append(self, page):
        record = self.page_to_record(page)
        super(DocumentStore, self).append(record)

    def insert(self, index, page):
        record = self.page_to_record(page)
        super(DocumentStore, self).insert(index, record)

    def remove(self, index):
        super(DocumentStore, self).remove(index)

