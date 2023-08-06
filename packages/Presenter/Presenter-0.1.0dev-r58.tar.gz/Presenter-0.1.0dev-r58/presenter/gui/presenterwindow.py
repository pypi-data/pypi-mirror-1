from presenter.gui import GladeWidget

import gtk
import gtk.gdk

import cairo

class PresenterWindow(GladeWidget):
    _glade = 'presenter.glade'
    def __init__(self, monitorinfo, document, *args, **kwargs):
        super(PresenterWindow, self).__init__(*args, **kwargs)

        self.slide.connect('expose-event', self.expose)

        monitorinfo.connect('monitors-changed', self.on_monitors_changed)
        self.monitorinfo = monitorinfo
        self.current_monitor = None

        self.document = document
        self.current_page = 0

        # Make the window and slide backgrounds black, to avoid flashing.
        black = gtk.gdk.Color(0, 0, 0)
        self.modify_bg(gtk.STATE_NORMAL, black)
        self.slide.modify_bg(gtk.STATE_NORMAL, black)

        self.realize()

        self.on_monitors_changed(monitorinfo.screen_size, monitorinfo.monitors)

    def draw(self, context, rect):
        if self.document is not None:
            slide = self.document[self.current_page]

            # Create a fake surface to render the slide onto.
            slide_surface = context.get_target().create_similar(
                cairo.CONTENT_COLOR_ALPHA,
                rect.width, rect.height
            )
            slide_context = gtk.gdk.CairoContext(cairo.Context(slide_surface))
            slide.render(slide_context, rect.width, rect.height)

            # Note: This is where we can do transitions with slides later.
            context.set_source_surface(slide_surface)
            context.paint()

    def next(self):
        if self.document:
            last = len(self.document) - 1
            self.current_page = min([last, self.current_page + 1])

    def previous(self):
        if self.document:
            self.current_page = max([0, self.current_page - 1])

    def on_monitors_changed(self, screen_size, monitors):
        n_monitors = len(monitors)
        if self.current_monitor is None or self.current_monitor < n_monitors:
            i = min([1, n_monitors - 1])
            self.set_monitor(i)

    def show(self, *args, **kwargs):
        self._widget.show(*args, **kwargs)
        self.set_monitor(self.current_monitor)

    def set_monitor(self, i):
        self.current_monitor = i

        visible = self.get_property('visible')

        if visible:
            self.unfullscreen()

        self.window.move_resize(*self.monitorinfo.monitors[i])

        if visible:
            self.fullscreen()

        self.queue_draw()

    def expose(self, widget, event):
        self.context = widget.window.cairo_create()
        rect = widget.get_allocation()

        self.context.rectangle(event.area.x, event.area.y,
                          event.area.width, event.area.height)
        self.context.clip()

        self.draw(self.context, rect)
        return False

    _current_page = 0
    def get_current_page(self):
        return self._current_page
    def set_current_page(self, page):
        self._current_page = page
        self.queue_draw()
    current_page = property(get_current_page, set_current_page)

    _document = None
    def get_document(self):
        return self._document
    def set_document(self, document):
        self._document = document
        self.current_page = 0
    document = property(get_document, set_document)

