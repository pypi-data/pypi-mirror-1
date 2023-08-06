from presenter.misc import EventHandler

from collections import defaultdict

class MonitorInfo(EventHandler):
    """An object which provides information about the monitors available
    for a specific gtk.Window."""

    def __init__(self, window, *args, **kwargs):
        super(MonitorInfo, self).__init__(*args, **kwargs)

        self.window = window.window
        self.screen = window.get_screen()

        self.screen_size = None
        self.monitors = None

        self.screen.connect('size-changed', self.on_monitors_changed)

        self.on_monitors_changed(None)

    def on_monitors_changed(self, event):
        # Get the full screen area.
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        self.screen_size = (screen_width, screen_height)

        # Get the size of the individual monitors.
        n_monitors = self.screen.get_n_monitors()
        self.monitors = [self.screen.get_monitor_geometry(i)
                         for i in xrange(n_monitors)]

        self.emit('monitors-changed', self.screen_size, self.monitors)

