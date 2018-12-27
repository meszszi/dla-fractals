from __future__ import division

from PyQt5.QtWidgets import (QWidget, QSlider,
                             QHBoxLayout, QVBoxLayout,
                             QPushButton, QLabel, QColorDialog)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor

class LabeledSlider(QWidget):
    """
    Custom slider widget that shows slider range boundaries and current value.
    """

    def __init__(self, label, range_min, range_max, parent,
                 label_width=200, slider_width=100, range_value_width=30,
                 widget_width=None):

        super().__init__(parent)
        self.label = label

        layout = QHBoxLayout(self)

        self.value_label = QLabel(self.label + " = " + str(range_min), self)
        self.value_label.setMinimumWidth(label_width)
        layout.addWidget(self.value_label)

        layout.addStretch()

        range_min_label = QLabel(str(range_min), self)
        range_min_label.setMinimumWidth(range_value_width)
        range_min_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(range_min_label)

        self.slider = QSlider(Qt.Horizontal, parent)
        self.slider.setRange(range_min, range_max)
        self.slider.setMinimumWidth(slider_width)
        layout.addWidget(self.slider)

        range_max_label = QLabel(str(range_max), self)
        range_max_label.setMinimumWidth(range_value_width)
        range_max_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(range_max_label)

        self.slider.valueChanged.connect(self.value_changed)

        if widget_width is not None:
            self.setFixedWidth(widget_width)

    def value_changed(self, value):
        self.value_label.setText(self.label + " = " + str(value))


class StatsLabel(QWidget):
    """
    Custom label widget that shows current parameter's value.
    """

    def __init__(self, label, init_value, parent,
                 label_width=200, value_width=50,
                 widget_width=None):

        super().__init__(parent)

        layout = QHBoxLayout(self)

        label_widget = QLabel(label + ":", self)
        label_widget.setMinimumWidth(label_width)
        layout.addWidget(label_widget)

        layout.addStretch()

        self.value_label = QLabel(str(init_value), self)
        self.value_label.setMinimumWidth(value_width)
        self.value_label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.value_label)

        if widget_width is not None:
            self.setFixedWidth(widget_width)


class ColorButton(QPushButton):
    """
    Custom color picker button.
    """

    colorChanged = pyqtSignal(QColor)

    def __init__(self, label, parent, initial_color=QColor(255, 255, 255)):

        super().__init__(label, parent)

        self.label = label
        self.color = initial_color
        self._set_colours()

        self.clicked.connect(self._pick_color)

    def _pick_color(self):
        self.color = QColorDialog.getColor()
        self._set_colours()
        self.colorChanged.emit(self.color)

    def _set_colours(self):
        back_color = self.color.name()

        luminance = (0.299 * self.color.red() +
                     0.587 * self.color.green() +
                     0.114 * self.color.blue()) / 255.

        font_color = "#FFFFFF" if luminance < 0.5 else "#000000"

        self.setStyleSheet("background-color:{};color:{};".
                           format(back_color, font_color))

