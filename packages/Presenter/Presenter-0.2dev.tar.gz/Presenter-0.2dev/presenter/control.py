import time

from presenter.interface import GtkBuilder
from presenter.output import OutputWindow
from presenter.monitordialog import MonitorDialog

from presenter.runsheet import Runsheet

from presenter import handlers

try:
    import gio
except ImportError:
    import fakegio as gio
import gtk
import gobject

from weakref import WeakValueDictionary

import pkg_resources
INTERFACE_FILE = pkg_resources.resource_stream(__name__, 'interface.glade')
INTERFACE_FILE = INTERFACE_FILE.read()

class AboutDialog(GtkBuilder):
    """
    Provides an About dialog box for Presenter.

    Loaded automatically from the glade file.
    """
    _glade_source = INTERFACE_FILE

class ControlWindow(GtkBuilder):
    """
    Provides the main Control window.

    Loaded automatically from the glade file.
    """
    _glade_source = INTERFACE_FILE

    TIMER_DELAY = 1000

    def __init__(self):
        super(ControlWindow, self).__init__()

        self.maximize()

        # Filename of the current runsheet.
        self.runsheet_file = None
        self.runsheet_file_etag = None

        self.handler_cache = WeakValueDictionary()

        # Clear the runsheet's liststore.
        model = self.runsheet_widget.get_model()
        self.runsheet = Runsheet(model)
        self.runsheet.new()

        # Clear the editor's tabs.
        for i in xrange(self.editor.get_n_pages()):
            self.editor.remove_page(0)

        # Create an output window.
        self.output = OutputWindow()
        self.output.connect(
            'show',
            lambda w: self.toolbutton_show.set_active(True)
        )
        self.output.connect(
            'hide',
            lambda w: self.toolbutton_show.set_active(False)
        )

        self.start_time = time.time()
        self.timer = gobject.timeout_add(self.TIMER_DELAY, self.timer_output)

    def get_handler(self, uri):
        if uri in self.handler_cache:
            return self.handler_cache[uri]

        gfile = gio.File(uri)
        gfileinfo = gfile.query_info(gio.FILE_ATTRIBUTE_STANDARD_CONTENT_TYPE)
        mime_type = gfileinfo.get_content_type()

        suitable_handlers = handlers.MIME_HANDLERS[mime_type]

        # TODO: Raise an (nice GUI) error if we can't find any suitable handlers.
        # TODO: Make a better way of choosing a handler.
        handler_class = suitable_handlers[0]

        handler = self.handler_cache[uri] = handler_class(uri)
        return handler

    def on_runsheet_new(self, menuitem):
        self.runsheet.new()

    def runsheet_open(self):
        def file_iter(f):
            l = f.read_line()
            while l:
                yield l
                l = f.read_line()

        fileobj = gio.DataInputStream(self.runsheet_file.read())
        self.runsheet.open(file_iter(fileobj))

        # Store the etag from the file (i.e.: modification time)
        self.runsheet_file_etag = self.runsheet_file.query_info(
            gio.FILE_ATTRIBUTE_ETAG_VALUE,
        ).get_etag()

    def on_runsheet_open(self, menuitem):
        dialog = gtk.FileChooserDialog(
            action=gtk.FILE_CHOOSER_ACTION_OPEN,
            buttons=(
                gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                gtk.STOCK_OPEN, gtk.RESPONSE_OK
            )
        )
        dialog.set_title('Open Runsheet')

        uri = None
        if dialog.run() == gtk.RESPONSE_OK:
            uri = dialog.get_uri()
        dialog.destroy()

        if uri:
            self.runsheet_file = gio.File(uri)
            self.runsheet_open()

    def runsheet_save(self):
        try:
            # File doesn't exist.
            fileobj = self.runsheet_file.create()
        except gio.Error:
            # File already exists, replace.

            # NOTE: This except: block isn't guaranteed to only be called for
            # files which already exist. The filename may be too long, and
            # there's a heap of other possibilities.

            etag = self.runsheet_file_etag
            if etag is None:
                etag = self.runsheet_file.query_info(
                    gio.FILE_ATTRIBUTE_ETAG_VALUE,
                ).get_etag()

            fileobj = self.runsheet_file.replace(etag, True)

            # TODO: Handle external programs writing to this file.
            # (The above line will raise a gio.Error)

        self.runsheet.save(fileobj)
        fileobj.close()

        # Store the etag from the file (i.e.: modification time)
        self.runsheet_file_etag = fileobj.get_etag()

    def on_runsheet_save(self, menuitem):
        if not self.runsheet_file:
            self.on_runsheet_saveas(menuitem)
        else:
            self.runsheet_save()

    def on_runsheet_saveas(self, menuitem):
        dialog = gtk.FileChooserDialog(
            action=gtk.FILE_CHOOSER_ACTION_SAVE,
            buttons=(
                gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                gtk.STOCK_SAVE, gtk.RESPONSE_OK
            )
        )
        dialog.set_title('Save Runsheet')

        uri = None
        if dialog.run() == gtk.RESPONSE_OK:
            uri = dialog.get_uri()
        dialog.destroy()

        if uri:
            self.runsheet_file = gio.File(uri)
            self.runsheet_save()

    def on_runsheet_editor(self, runsheet, path, col):
        row = self.runsheet[path]
        name = row['name']
        uri = row['uri']

        handler = self.get_handler(uri)
        control = handler.get_editor_control()

        name_label = gtk.Label(name)

        self.editor.append_page(control, name_label)
        self.editor.show_all()

    def on_runsheet_output(self, toggle, path):
        row = self.runsheet[path]
        uri = row['uri']

        handler = self.get_handler(uri)
        control = handler.get_output_control()

        # Put the output widget onto the output window.
        self.output.change_output_widget(control)

        # TODO: Update the toggle's "active" property. This may require a change
        # to our ListStore model.

    def on_browser_select(self, browser):
        """
        Called when the user selects an item from the file-browser.
        Adds the selected file to the runsheet.
        """
        uri = browser.get_uri()
        self.runsheet.append(uri=uri)

    def on_monitors_setup(self, menuitem):
        """Move the output window to a different monitor."""
        dialog = MonitorDialog(0)

        monitor = None
        if dialog.run() == gtk.RESPONSE_OK:
            monitor = dialog.get_monitor(dialog.selected)
        dialog.destroy()

        if monitor:
            self.output.move_monitor(monitor)

    def on_output_toggle(self, toggle):
        new_status = toggle.get_active()
        current_status = self.output.get_property("visible")

        if new_status != current_status:
            if new_status:
                self.output.show_all()
            else:
                self.output.hide()

    def on_output_blackout(self, toolitem):
        self.output.clear()

    def on_about(self, menuitem):
        """Load the about dialog for Presenter."""
        dialog = AboutDialog()
        dialog.run()
        dialog.destroy()

    def timer_output(self):
        diff = time.time() - self.start_time
        diff = int(round(diff))

        seconds = diff % 60
        diff /= 60
        minutes = diff % 60
        diff /= 60
        hours = diff

        label = '%d:%.2d:%.2d' % (hours, minutes, seconds)
        self.label_time.set_text(label)

        # Returns true to repeat the callback.
        return True

    def on_timer_reset(self, toolbutton):
        self.start_time = time.time()
        # Force an update.
        self.timer_output()
        # Restart the timer.
        gobject.source_remove(self.timer)
        self.timer = gobject.timeout_add(self.TIMER_DELAY, self.timer_output)

