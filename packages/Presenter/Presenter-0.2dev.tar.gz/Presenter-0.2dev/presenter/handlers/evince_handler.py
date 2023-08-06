"""
Evince file handler, using libevview and libevdocument.

Requires the Python bindings for evince.
"""

from presenter.handlers.base import FileHandler

import gtk
import evince

class EvinceFileHandler(FileHandler):
    """
    A file handler class for Evince.
    """

    mime_types = [
        'application/pdf',
        'application/x-bzpdf',
        'application/x-gzpdf',
        'application/postscript',
        'application/x-bzpostscript',
        'application/x-gzpostscript',
        'image/x-eps',
        'image/x-bzeps',
        'image/x-gzeps',
        'application/x-dvi',
        'application/x-bzdvi',
        'application/x-gzdvi',
        'image/vnd.djvu',
        'image/tiff',
        'application/x-cbr',
        'application/x-cbz',
        'application/x-cb7',
        'image/*',
        'application/vnd.sun.xml.impress',
        'application/vnd.oasis.opendocument.presentation',
    ]

    def __init__(self, uri):
        super(EvinceFileHandler, self).__init__(uri)

        self.uri = uri

        self.outputs = []

    def make_viewer(self):
        """Create an EvView widget, and load the document into it."""
        viewer = evince.View()
        document = evince.factory_get_document(self.uri)
        viewer.set_document(document)
        viewer.set_screen_dpi(96)

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.add(viewer)

        def zoom_invalid(widget):
            """Translated from ev_window_set_view_size in ev-window.c"""
            allocation = scroll.get_allocation()
            width = allocation.width
            height = allocation.height

            if scroll.get_shadow_type() != gtk.SHADOW_NONE:
                style = viewer.get_style()
                width -= 2 * style.xthickness
                height -= 2 * style.ythickness

            vsb_requisition, hsb_requisition = scroll.size_request()

            scrollbar_spacing = scroll.style_get_property("scrollbar_spacing")

            viewer.set_zoom_for_size(
                max(1, width),
                max(1, height),
                vsb_requisition + scrollbar_spacing,
                hsb_requisition + scrollbar_spacing,
            )

        viewer.connect('zoom_invalid', zoom_invalid)

        return scroll, viewer, document

    def get_editor_control(self):
        """Create a new gtk.Widget to put in the editor notebook."""
        # Evince viewer widget.
        scroll, viewer, document = self.make_viewer()
        viewer.set_sizing_mode(evince.SIZING_BEST_FIT)
        scroll.set_shadow_type(gtk.SHADOW_IN)

        # Toolbar.
        toolbar = gtk.Toolbar()

        def go_back(widget):
            for viewer, doc in self.outputs:
                viewer.previous_page()
                page_index = doc.get_page_cache().get_current_page()
                document.get_page_cache().set_current_page(page_index)

        toolbutton_back = gtk.ToolButton(gtk.STOCK_GO_BACK)
        toolbutton_back.connect('clicked', go_back)
        toolbar.add(toolbutton_back)

        def update(widget):
            # Get the editor's page index.
            cache = document.get_page_cache()
            current_index = cache.get_current_page()

            # Set the current page of all outputs.
            for viewer, doc in self.outputs:
                cache = doc.get_page_cache()
                cache.set_current_page(current_index)

        toolbutton_update = gtk.ToolButton(gtk.STOCK_REFRESH)
        toolbutton_update.set_label("Update")
        toolbutton_update.connect('clicked', update)
        toolbar.add(toolbutton_update)

        def go_forward(widget):
            for viewer, doc in self.outputs:
                viewer.next_page()
                page_index = doc.get_page_cache().get_current_page()
                document.get_page_cache().set_current_page(page_index)

        toolbutton_forward = gtk.ToolButton(gtk.STOCK_GO_FORWARD)
        toolbutton_forward.connect('clicked', go_forward)
        toolbar.add(toolbutton_forward)

        # Layout in VBox.
        vbox = gtk.VBox()
        vbox.pack_start(toolbar, False)
        vbox.pack_start(scroll, True)
        return vbox

    def get_output_control(self):
        """Create a new gtk.Widget to put in the output window."""
        scroll, viewer, document = self.make_viewer()

        self.outputs.append((viewer, document))

        viewer.set_presentation(True)
        viewer.set_sizing_mode(evince.SIZING_BEST_FIT)

        return scroll

