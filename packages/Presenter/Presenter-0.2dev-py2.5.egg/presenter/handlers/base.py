"""
Package for file handlers for presenter.
"""

try:
    import gio
except ImportError:
    import fakegio as gio

def load_file(uri):
    """Load the given uri using GVFS, and return a file-like object."""
    gfile = gio.File(uri)
    inputstream = gfile.read()
    return inputstream

class FileHandler(object):
    """
    An abstract base class (but only theoretically) for all file handlers (e.g.:
    Evince, XEmbed, Video).

    Subclasses should override get_editor_control and get_output_control.
    Also, the mime_types attribute should be defined as a list of mime-types
    which the handler can read.

    A convenience method load_file is provided for subclasses to load the file
    (without learning GVFS!).
    """

    def __init__(self, uri):
        """
        Initialise a handler for the file at uri - you should use
        FileHandler.load_file or GVFS to load the file.
        """
        pass

    def get_editor_control(self):
        """Create a new gtk.Widget to put in the editor notebook."""
        pass

    def get_output_control(self):
        """Create a new gtk.Widget to put in the output window."""
        pass

