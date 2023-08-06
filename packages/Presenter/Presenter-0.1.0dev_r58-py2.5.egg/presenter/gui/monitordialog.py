import gtk
from presenter.gui.monitorwidget import MonitorWidget

class MonitorDialog(gtk.Dialog):
    def __init__(self, monitorinfo, current, *args, **kwargs):
        super(MonitorDialog, self).__init__(*args, **kwargs)

        self.monitor_widget = MonitorWidget(monitorinfo, current)
        self.monitor_widget.connect('monitor-selected', self._monitor_selected)

        self.vbox.add(self.monitor_widget)
        self.show_all()

        self.monitor = None

    def _monitor_selected(self, widget, index):
        self.monitor = index
        self.response(gtk.RESPONSE_OK)

