from presenter.misc import DeclarativeMeta
from presenter.misc import EventHandler

from collections import defaultdict

class DocumentException(Exception): pass

handlers = defaultdict(list)

class Document(EventHandler):
    """To subclass, declare a file_types list of extensions your class handlers,
    and a type_name string with a printable version of the file type."""

    __metaclass__ = DeclarativeMeta

    type_name = 'Unknown file type'
    file_types = []

    def __classinit__(cls, new_attrs):
        if 'file_types' in new_attrs:
            for ft in new_attrs['file_types']:
                handlers[ft].append(cls)

    def __init__(self, filename, *args, **kwargs):
        super(Document, self).__init__(*args, **kwargs)
        self.pages = []

    def append(self, page):
        self.pages.append(page)
        self.emit('item-append', page)

    def insert(self, index, page):
        self.pages.insert(index, page)
        self.emit('item-insert', index, page)

    def remove(self, index):
        self.emit('item-remove', index)
        del self.pages[index]

    def __len__(self):
        return len(self.pages)

    def __iter__(self):
        return iter(self.pages)

    def __getitem__(self, index):
        return self.pages[index]

class Page(object):
    def __init__(self, title, *args, **kwargs):
        super(Page, self).__init__(*args, **kwargs)
        self.title = title

    def render(self, context, width, height):
        """Return the page onto the cairo context."""
        pass

