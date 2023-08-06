from pkg_resources import resource_string

import pygtk
pygtk.require("2.0")
import gtk
import gtk.glade

sources = {}

class GladeWidget(object):
    _glade = None

    def __init__(self, *args, **kwargs):
        super(GladeWidget, self).__init__(*args, **kwargs)

        try:
            source = sources[self._glade]
        except KeyError:
            source = resource_string(__name__, self._glade)
            sources[self._glade] = source

        widget_name = self.__class__.__name__
        self._builder = gtk.glade.xml_new_from_buffer(source, len(source))
        self._builder.signal_autoconnect(self)
        self._widget = self._builder.get_widget(widget_name)

    def __del__(self):
        try:
            self._widget.destroy()
        except AttributeError:
            pass

    def __getattribute__(self, name):
        try:
            return super(GladeWidget, self).__getattribute__(name)
        except AttributeError:
            if not hasattr(self, '_widget'):
                raise

            try:
                return getattr(self._widget, name)
            except AttributeError:
                widget = self._builder.get_widget(name)
                if widget is None:
                    raise
                return widget

