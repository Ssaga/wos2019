from enum import Enum
from PyQt5.QtWidgets import QDockWidget
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QSpacerItem
from PyQt5.QtWidgets import QWidget


class WosActionWidget(QDockWidget):
    class WidgetType(Enum):
        ACTION_CORE = 0
        ACTION_ADDON = 1
        COMMAND = 2
        AFTER_SPACER = 3

    def __init__(self, parent=None):
        QDockWidget.__init__(self, parent)

        self.setWindowTitle('Commands')

        widget = QWidget(self)
        self.setWidget(widget)
        self.layout = QGridLayout(widget)

        self.spacer = QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.layout.addItem(self.spacer)

        self.widgets = dict()
        self.widgets[WosActionWidget.WidgetType.ACTION_CORE] = list()
        self.widgets[WosActionWidget.WidgetType.ACTION_ADDON] = list()
        self.widgets[WosActionWidget.WidgetType.COMMAND] = list()
        self.widgets[WosActionWidget.WidgetType.AFTER_SPACER] = list()

    def add_widget(self, widget, widget_type):
        self.widgets[widget_type].append(widget)
        self.reorder_widgets()

    def append_widget(self, widget):
        self.layout.removeItem(self.spacer)
        self.layout.addWidget(widget, self.layout.rowCount(), 0, 1, self.layout.columnCount())
        self.layout.addItem(self.spacer)

    def remove_widget(self, widget):
        for widget_list in self.widgets.values():
            if widget in widget_list:
                widget_list.remove(widget)
        self.reorder_widgets()

    def reorder_widgets(self):
        self.layout.removeItem(self.spacer)

        for widget_list in self.widgets.values():
            for widget in widget_list:
                self.layout.removeWidget(widget)

        for widget in self.widgets[WosActionWidget.WidgetType.ACTION_CORE]:
            self.layout.addWidget(widget, self.layout.rowCount(), 0, 1, self.layout.columnCount())

        for widget in self.widgets[WosActionWidget.WidgetType.ACTION_ADDON]:
            self.layout.addWidget(widget, self.layout.rowCount(), 0, 1, self.layout.columnCount())

        for widget in self.widgets[WosActionWidget.WidgetType.COMMAND]:
            self.layout.addWidget(widget, self.layout.rowCount(), 0, 1, self.layout.columnCount())

        self.layout.addItem(self.spacer)

        for widget in self.widgets[WosActionWidget.WidgetType.AFTER_SPACER]:
            self.layout.addWidget(widget, self.layout.rowCount(), 0, 1, self.layout.columnCount())
