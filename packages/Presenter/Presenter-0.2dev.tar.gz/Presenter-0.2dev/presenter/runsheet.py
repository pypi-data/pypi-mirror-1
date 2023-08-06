import csv

try:
    import gio
except ImportError:
    import fakegio as gio
import gtk

class Runsheet(object):
    RUNSHEET_COL_NAME, RUNSHEET_COL_ICON, RUNSHEET_COL_URI = xrange(3)
    COLUMNS = ['name', 'icon', 'uri']

    EXPORT_COLUMNS = ['uri']

    def __init__(self, model):
        self.model = model

    def new(self):
        self.model.clear()

    def open(self, fileobj):
        self.model.clear()

        csv_reader = csv.DictReader(fileobj)
        for row in csv_reader:
            self.append(**row)

    def save(self, fileobj):
        csv_writer = csv.writer(fileobj)
        csv_writer.writerow(self.EXPORT_COLUMNS)

        column_ids = [self.COLUMNS.index(col) for col in self.EXPORT_COLUMNS]

        row = self.model.get_iter_first()
        while row:
            row_values = self.model.get(row, *column_ids)
            csv_writer.writerow(row_values)
            row = self.model.iter_next(row)

    def __getitem__(self, path):
        rowiter = self.model.get_iter(path)
        fields = self.model.get(rowiter, *xrange(len(self.COLUMNS)))
        return dict(zip(self.COLUMNS, fields))

    def append(self, name=None, icon=None, uri=None, **kwargs):
        """
        Add an item to the run sheet.

        Columns values are given as keyword arguments, to protect against future
        changes to the runsheet model.
        """
        if uri:
            gfile = gio.File(uri)

            if not name:
                name = gfile.get_basename()

            if not icon:
                gfileinfo = gfile.query_info(gio.FILE_ATTRIBUTE_STANDARD_ICON)
                icon_names = gfileinfo.get_icon().get_names()

                # NOTE: There may be a better way to get the icon theme.
                icontheme = gtk.icon_theme_get_default()
                iconinfo = icontheme.choose_icon(icon_names, gtk.ICON_SIZE_DIALOG, 0)
                if iconinfo is not None:
                    icon = iconinfo.load_icon()

        row = [name, icon, uri]
        return self.model.append(row)

