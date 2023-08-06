import pygtk
import gtk
pygtk.require("2.0")

GLOBAL_SIGNALS = {
    'gtk_main_quit': gtk.main_quit,
}

class GtkBuilder(object):
    """
    Loads a widget from a glade GtkBuilder file.
    Instanciating the class will load a new copy of the widget.
    
    Signals are automatically connected from GLOBAL_SIGNALS (providing
    gtk_main_quit), the subclasses' methods, and the instance's methods.

    Additionally, all child widgets are made attributes of the instance.
    Note: this may cause some fun with deleting widgets (due to the extra
    references).
    """
    def __init__(self):
        assert hasattr(self, '_glade_source'), 'A GtkBuilder file (from ' + \
        'Glade) must be specified as YourGuiClass._glade_source.'

        # Work out what glade object to use.
        try:
            self._glade_object
        except AttributeError:
            self._glade_object = self.__class__.__name__

        # Load the glade file.
        builder = gtk.Builder()
        source = self._glade_source
        builder.add_from_string(source, len(source))

        # Join class methods and global signals into one dict.
        signals = GLOBAL_SIGNALS.copy()
        for method in self.__class__.__dict__:
            signals[method] = getattr(self, method)
        signals.update(self.__dict__)
        builder.connect_signals(signals)

        # Set the glade object as self.widget, for __getattribute__ magic.
        self.widget = builder.get_object(self._glade_object)

        # Provide nice names.
        def add_children(toplevel, widget):
            """
            Recursivly visit the child widgets of widget, and connect them as
            attributes to toplevel.
            """
            # Bugfix: gtk.FileChooser doesn't like being investigated.
            if isinstance(widget, gtk.FileChooser):
                return

            for child in widget.get_children():
                if isinstance(child, gtk.Container):
                    add_children(toplevel, child)
                setattr(toplevel, child.get_name(), child)

        add_children(self, self.widget)

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            if name != 'widget':
                return getattr(self.widget, name)

def run_application(window):
    """
    Run window as a top-level application window.

    The method blocks until window is destroyed.
    """
    window.show_all()
    window.connect('destroy', gtk.main_quit)
    gtk.main()

