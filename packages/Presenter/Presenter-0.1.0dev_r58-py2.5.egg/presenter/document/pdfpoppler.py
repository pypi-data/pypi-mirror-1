import poppler

import gtk.gdk

from presenter.document.base import Document, Page

class PDFPage(Page):
    def __init__(self, page, title, *args, **kwargs):
        super(PDFPage, self).__init__(title, *args, **kwargs)

        self.page = page
        self.width, self.height = page.get_size()

    def render(self, context, width, height):
        scale = min([float(width) / self.width, float(height) / self.height])
        context.scale(scale, scale)

        self.page.render(context)

class PDFDocument(Document):
    type_name = 'PDF Documents'
    file_types = ['pdf']

    def __init__(self, filename, *args, **kwargs):
        super(PDFDocument, self).__init__(filename, *args, **kwargs)

        document = poppler.document_new_from_file('file://%s' % filename, None)

        for i in xrange(document.get_n_pages()):
            page = PDFPage(document.get_page(i), 'Page %d' % i)
            self.append(page)

