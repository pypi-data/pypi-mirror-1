from presenter.gui import GladeWidget
import gtk
import gtk.gdk

from presenter import document

from presenter.gui.monitorinfo import MonitorInfo
from presenter.gui.monitordialog import MonitorDialog

from presenter.gui.presenterwindow import PresenterWindow

from presenter.gui.documentstore import DocumentStore

class MainWindow(GladeWidget):
    _glade = 'presenter.glade'
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.running = False
        self.presenter = None
        self.document = None
        self.store = None

        self.connect('realize', self.realize)

    def realize(self, event):
        self.monitorinfo = MonitorInfo(self)
        self.presenter = PresenterWindow(self.monitorinfo, self.document)

#        self.presenter.set_transient_for(self._widget)

        def presenter_key_press(widget, event):
            self.emit('key-press-event', event)

        def presenter_close(window, event):
            self.running = False
            return True # Prevent window from closing.

        self.presenter.connect('key-press-event', presenter_key_press)
        self.presenter.connect('delete-event', presenter_close)

    def change_monitor(self, *args):
        dialog = MonitorDialog(self.monitorinfo,
                               self.presenter.current_monitor,
                               'Choose Monitor', parent=self._widget)

        try:
            if dialog.run() == gtk.RESPONSE_OK:
                self.presenter.set_monitor(dialog.monitor)
        finally:
            dialog.destroy()

    def open_file(self, widget):
        # Open file dialog
        dialog = gtk.FileChooserDialog(
            title='Load presentation',
            parent=self._widget,
            action=gtk.FILE_CHOOSER_ACTION_OPEN,
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                     gtk.STOCK_OPEN, gtk.RESPONSE_OK)
        )

        if not document.handlers:
            raise Exception("No file handlers are available to load the file.")

        # All files filter
        for ext in document.handlers:
            handler = document.handlers[ext][-1]

            filter = gtk.FileFilter()
            filter.set_name(handler.type_name)
            filter.add_pattern("*.%s" % ext)
            dialog.add_filter(filter)

        try:
            if dialog.run() == gtk.RESPONSE_OK:
                # Load file.
                filename = dialog.get_filename()
                self.document = document.load(filename)

                # Make a document store for the icon view.
                self.store = DocumentStore(self.document)
                self.iconview.set_model(self.store)
        finally:
            dialog.destroy()

    # Slide control.
    def on_back(self, widget):
        self.presenter.previous()

    def on_forward(self, widget):
        self.presenter.next()

    def on_iconview_item_activated(self, widget, iter):
        index = iter[0] # Note: this is specific to gtk.ListStore.
        self.presenter.current_page = index

    # Live control.
    def on_live_toggled(self, *args):
        self.running = not self.running

    # Properties

    _document = None
    def get_document(self):
        return self._document
    def set_document(self, document):
        self._document = document
        if self.presenter is not None:
            self.presenter.document = document
    document = property(get_document, set_document)

    __running = False

    def get_running(self):
        return self.__running

    def set_running(self, state):
        if state == self.__running:
            return

        if self.toolbar_live.get_active() != state:
            self.toolbar_live.set_active(state)

        self.__running = state

        if state:
            self.presenter.show()

            self.menu_live_image.set_from_stock('gtk-media-stop',
                                                gtk.ICON_SIZE_MENU)
            self.menu_live.get_child().set_text('Stop Live')

            self.toolbar_live.set_stock_id('gtk-media-stop')
            self.toolbar_live.set_label('Stop Live')
        else:
            self.presenter.hide()

            self.menu_live_image.set_from_stock('gtk-media-play',
                                                gtk.ICON_SIZE_MENU)
            self.menu_live.get_child().set_text('Live Mode')

            self.toolbar_live.set_stock_id('gtk-media-play')
            self.toolbar_live.set_label('Live Mode')

    running = property(get_running, set_running)

    # This is the main window.
    def on_destroy(self, *args):
        gtk.main_quit()
 
