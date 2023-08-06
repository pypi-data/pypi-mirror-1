import gtk
from presenter.monitorwidget import MonitorWidget

class MonitorDialog(gtk.Dialog):
    def __init__(self, current):
        super(MonitorDialog, self).__init__()

        self.monitor_widget = MonitorWidget(current)

        self.vbox.add(self.monitor_widget)

        ok_button = gtk.Button(stock=gtk.STOCK_OK)
        ok_button.connect('clicked', self.on_ok)

        self.vbox.add(ok_button)

        self.show_all()

        self.selected = None

    def on_ok(self, widget):
        self.selected = self.monitor_widget.selected
        self.response(gtk.RESPONSE_OK)

    def get_monitor(self, index):
        return self.monitor_widget.monitors[index]

