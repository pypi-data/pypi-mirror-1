import os
import logging

from presenter.document.base import handlers

class UnknownFileType(Exception): pass

def load(filename):
    # Get the extension of the file, without the ".".
    ext = os.path.splitext(filename)[1]
    ext = ext.replace(os.path.extsep, '', 1)

    # Try each of the handlers in reverse order (last declared class first).
    for cls in handlers[ext][::-1]:
        return cls(filename)
    else:
        raise UnknownFileType('There is no handler for files of type "%s".'
                              % ext)

# File loaders.
modules = [
    'zippedimages',
    'pdfpoppler'
]

for name in modules:
    try:
        __import__('presenter.document.' + name)
    except ImportError:
        logging.info('Could not import %s.' % name)

