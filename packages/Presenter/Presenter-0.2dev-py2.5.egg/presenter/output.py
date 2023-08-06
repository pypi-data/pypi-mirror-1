import gtk

class OutputWindow(gtk.Window):
    """The window to put the presentation onto."""

    def __init__(self):
        super(OutputWindow, self).__init__()

        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("black"))

        # TODO: Use ControlWindow's AccelGroup.

        self.connect('key-press-event', self.on_key_press)
        self.connect('delete-event', self.hide_on_delete)
        self.fullscreen()

    def on_key_press(self, widget, event):
        if event.keyval == gtk.keysyms.Escape:
            self.hide()

    def clear(self):
        child = self.get_child()
        if child:
            self.remove(child)

    def change_output_widget(self, widget):
        # TODO: Work out transitions.

        # Add the new child.
        self.clear()
        self.add(widget)
        widget.realize()
        widget.show_all()

    def move_monitor(self, rect):
        """
        Relocate the output window to be fullscreen on the monitor whose
        bounds are given by rect.
        """
        visible = self.get_property('visible')

        if visible:
            self.hide()

        self.unfullscreen()
        self.move(rect.x, rect.y)
        self.resize(rect.width, rect.height)

        if visible:
            self.show()

        self.fullscreen()

