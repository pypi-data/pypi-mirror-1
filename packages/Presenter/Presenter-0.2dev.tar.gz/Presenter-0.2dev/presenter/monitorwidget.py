import gtk
import gobject

def gtk_colour_to_cairo(colour):
    r = colour.red / 65535.0
    g = colour.green / 65535.0
    b = colour.blue / 65535.0
    return (r, g, b)

class MonitorWidget(gtk.DrawingArea):
    """A widget which displays the current monitor layout, and
    updates itself upon changes to the monitor layout.
    
    This widget can be used to select a monitor."""

    def __init__(self, current):
        super(MonitorWidget, self).__init__()

        self.set_events(gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK)

        self.connect('realize', self.on_realize)
        self.connect('expose-event', self.expose)
        self.connect('button-release-event', self.mouse_down)

        # TODO: Make this relative to the widget size.
        self.pad_width = 5

        self.screen = None
        self.screen_size = None
        self.monitors = None

        self.selected = current

    def on_realize(self, widget):
        self.screen = widget.window.get_screen()
        self.screen.connect('size-changed', self.on_monitors_changed)

        # Get the initial monitor information.
        self.on_monitors_changed(None)

    def on_monitors_changed(self, event):
        # Get total screen size.
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        self.screen_size = (screen_width, screen_height)

        # Get monitor sizes.
        n_monitors = self.screen.get_n_monitors()
        self.monitors = map(self.screen.get_monitor_geometry, xrange(n_monitors))

        min_size = min(self.monitors, key=lambda (x, y, w, h): w*h)
        width_request = screen_width * 100 / float(min_size.width)
        height_request = screen_height * 100 / float(min_size.height)
        self.set_size_request(int(width_request), int(height_request))

        if self.selected >= n_monitors:
            self.selected = min([1, n_monitors - 1])

        self.queue_draw()

    def draw(self, context):
        # Get colours from gtk style.
        style = self.get_style()

        bg_stroke = gtk_colour_to_cairo(style.dark[gtk.STATE_NORMAL])
        bg_fill = gtk_colour_to_cairo(style.bg[gtk.STATE_NORMAL])

        fg_stroke = gtk_colour_to_cairo(style.fg[gtk.STATE_NORMAL])
        fg_fill = gtk_colour_to_cairo(style.light[gtk.STATE_NORMAL])

        fg_selected_stroke = gtk_colour_to_cairo(style.fg[gtk.STATE_SELECTED])
        fg_selected_fill = gtk_colour_to_cairo(style.bg[gtk.STATE_SELECTED])

        # Draw total screen size.
        context.set_line_width(2)
        size = (0, 0) + self.screen_size
        x, y, w, h = self.translate_size(size)
        x -= self.pad_width * 2
        y -= self.pad_width * 2
        w += self.pad_width * 4
        h += self.pad_width * 4
        context.rectangle(x, y, w, h)

        context.set_source_rgb(*bg_fill)
        context.fill_preserve()

        context.set_source_rgb(*bg_stroke)
        context.stroke()

        # Draw monitors.
        context.set_line_width(2)
        for i, size in enumerate(self.monitors):
            # Adjust monitor size to drawing size.
            x, y, w, h = self.translate_size(size)
            context.rectangle(x, y, w, h)

            if i == self.selected:
                fill = fg_selected_fill
            else:
                fill = fg_fill

            context.set_source_rgb(*fill)
            context.fill_preserve()

            if i == self.selected:
                stroke = fg_selected_stroke
            else:
                stroke = fg_stroke

            context.set_source_rgb(*stroke)
            context.stroke()

    def mouse_down(self, widget, event):
        for i, monitor in enumerate(self.monitors):
            x, y, w, h = map(int, self.translate_size(monitor))
            if event.x >= x and event.x < x + w and \
               event.y >= y and event.y < y + h:
                break
        else:
            i = None

        if i is not None:
            # A monitor was chosen.

            if self.selected != i:
                # A different monitor was chosen.

                if self.selected is not None:
                    # There was a previous monitor.
                    previous = self.translate_size(self.monitors[self.selected])
                    self.queue_draw_area(*map(int, previous))

                self.queue_draw_area(x, y, w, h)
                self.selected = i

    def translate_size(self, (x, y, w, h)):
        screen_width, screen_height = self.screen_size
        rect = self.get_allocation()

        widget_width = rect.width - self.pad_width * 2
        widget_height = rect.height - self.pad_width * 2

        zoom = max([
            float(screen_width) / widget_width, # Screen aspect.
            float(screen_height) / widget_height # Widget aspect.
        ])

        draw_width = screen_width / zoom
        draw_height = screen_height / zoom
        draw_x = (widget_width - draw_width) / 2.0 + self.pad_width
        draw_y = (widget_height - draw_height) / 2.0 + self.pad_width

        x /= zoom
        y /= zoom
        w /= zoom
        h /= zoom

        x += self.pad_width + draw_x
        y += self.pad_width + draw_y
        w -= self.pad_width * 2
        h -= self.pad_width * 2

        return (x, y, w, h)

    def expose(self, widget, event):
        context = widget.window.cairo_create()

        # Only update the invalidated region, by clipping.
        context.rectangle(event.area.x, event.area.y,
                          event.area.width, event.area.height)
        context.clip()

        self.draw(context)
        return False
