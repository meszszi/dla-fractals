from PyQt5.QtWidgets import (QWidget, QSlider, QApplication,
                             QHBoxLayout, QVBoxLayout,
                             QPushButton, QCheckBox, QLabel)
from PyQt5.QtCore import QObject, Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QColor
import sys

from canvas import CanvasWidget
from simulation import Simulation

class LabeledSlider(QWidget):
    def __init__(self, label, range_min, range_max, parent, label_width=200):
        super().__init__(parent)
        self.label = label
        self.range_min = range_min
        self.range_max = range_max
        layout = QHBoxLayout(self)

        self.value_label = QLabel(self.label + " = " + str(range_min), self)
        self.value_label.setFixedWidth(label_width)
        layout.addWidget(self.value_label)
        layout.addWidget(QLabel(str(range_min), self))
        self.slider = QSlider(Qt.Horizontal, parent)
        self.slider.setRange(range_min, range_max)
        layout.addWidget(self.slider)
        layout.addWidget(QLabel(str(range_max), self))
        self.slider.valueChanged.connect(self.value_changed)

    def value_changed(self, value):
        self.value_label.setText(self.label + " = " + str(value))

class App(QWidget):
    """
    Main app's window.
    Contains the canvas widget on which the particles are drawn
    as well as all the widgets for user to interact with simulation.
    """

    def __init__(self,
                 frame_interval=40,
                 default_canvas_size=500):
        """
        Initializes all app's parameters.
        """
        super().__init__()

        self.frame_interval = frame_interval
        self.default_canvas_size = default_canvas_size

        self.canvas = CanvasWidget(
            self.default_canvas_size, self.default_canvas_size,
            QColor(250, 250, 250),
            QColor(20, 20, 20),
            border=1,
            border_color=QColor(0, 0, 0)
        )

        self.simulation = None
        self.simulation_initialized = False

        self.init_ui()

    def init_ui(self):
        """
        Creates interface layouts.

        Interactive widgets layout:
        - start button
        - stop button
        - reset button
        - gravity force slider (effective values: 0 -> 1)
        - particle radius slider (effective values: 1 -> 10)
        - random step length slider  (effective values: 0 -> 10)
        """

        self.input_layout = QVBoxLayout()
        self.input_layout.setStretch(2, 1)
        self.main_layout = QHBoxLayout()

        self.start_button = QPushButton("Start", self)
        #self.start_button.setFixedWidth(200)
        self.start_button.clicked.connect(self.start_simulation)
        self.input_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop", self)
        #self.stop_button.setFixedWidth(200)
        self.stop_button.clicked.connect(self.stop_simulation)
        self.input_layout.addWidget(self.stop_button)

        self.reset_button = QPushButton("Reset", self)
        #self.reset_button.setFixedWidth(200)
        self.reset_button.clicked.connect(self.reset_simulation)
        self.input_layout.addWidget(self.reset_button)

        sliders_label_width = 200

        gravity_sl = LabeledSlider("Gravity", 0, 100, self, sliders_label_width)
        self.gravity_slider = gravity_sl.slider
        self.gravity_slider.setValue(50)
        self.gravity_slider.valueChanged.connect(self.gravity_slider_change)
        self.input_layout.addWidget(gravity_sl)

        part_sl = LabeledSlider("Particle radius", 1, 10, self, sliders_label_width)
        self.partrad_slider = part_sl.slider
        self.partrad_slider.setValue(3)
        self.partrad_slider.valueChanged.connect(self.partrad_slider_change)
        self.input_layout.addWidget(part_sl)

        step_sl = LabeledSlider("Random step length", 0, 10, self, sliders_label_width)
        self.steplength_slider = step_sl.slider
        self.steplength_slider.setValue(5)
        self.steplength_slider.valueChanged.connect(self.steplength_slider_change)
        self.input_layout.addWidget(step_sl)

        canvas_sl = LabeledSlider("Canvas size", 100, 900, self, sliders_label_width)
        self.canvassize_slider = canvas_sl.slider
        self.canvassize_slider.setValue(500)
        self.canvassize_slider.valueChanged.connect(self.canvassize_slider_change)
        self.input_layout.addWidget(canvas_sl)

        self.drawmoving_checkbox = QCheckBox("Draw moving particles", self)
        self.drawmoving_checkbox.setChecked(True)
        self.drawmoving_checkbox.stateChanged.connect(self.drawmoving_checkbox_change)
        self.input_layout.addWidget(self.drawmoving_checkbox)

        self.input_layout.addStretch()

        self.main_layout.addLayout(self.input_layout)

        self.main_layout.addStretch()

        canvas_layout = QVBoxLayout()
        canvas_layout.addWidget(self.canvas)
        canvas_layout.addStretch()

        self.main_layout.addLayout(canvas_layout)
        self.main_layout.addStretch()
        self.setLayout(self.main_layout)
        self.show()

        self.simulation_timer = QTimer(self)
        self.simulation_timer.timeout.connect(self.update_simulation)


    def start_simulation(self):
        if not self.simulation_initialized:
            self.simulation_initialized = True
            self.simulation = Simulation(
                self.default_canvas_size,
                self.default_canvas_size,
                self.partrad_slider.value(),
                (self.default_canvas_size // 2, self.default_canvas_size // 2),
                self.gravity_slider.value() / 100,
                self.steplength_slider.value(),
                10
            )
            self.simulation.initialize()
            self.canvas.initialize()
            self.canvas.particles = self.simulation.new_solid_particles
            self.canvas.repaint()
            self.canvassize_slider.setDisabled(True)
            
        self.simulation_timer.start(self.frame_interval)

    def stop_simulation(self):
        self.simulation_timer.stop()

    def reset_simulation(self):
        self.stop_simulation()
        self.canvas.initialize()
        self.canvas.repaint()
        self.simulation_initialized = False
        self.canvassize_slider.setEnabled(True)

    def gravity_slider_change(self, value):
        if not self.simulation_initialized:
            return

        scalar = 100
        self.simulation.gravity_force = value / scalar

    def partrad_slider_change(self, value):
        if not self.simulation_initialized:
            return

        scalar = 1
        self.simulation.particle_radius = value / scalar

    def steplength_slider_change(self, value):
        if not self.simulation_initialized:
            return

        scalar = 1
        self.simulation.rand_step_length = value / scalar

    def canvassize_slider_change(self, value):
        self.canvas.width = value
        self.canvas.height = value
        self.canvas.initialize()
        self.canvas.repaint()
        self.default_canvas_size = value

    def drawmoving_checkbox_change(self, value):
        self.canvas.draw_moving_particles = value

    def update_simulation(self):
        """
        Updates simulation state and repaints the canvas.
        :return:
        """
        if not self.simulation.update_particles():
            if not self.simulation.spawn_particles():
                self.stop_simulation()

        self.canvas.particles = (
            self.simulation.new_solid_particles + self.simulation.moving_particles)

        self.canvas.repaint()

app = QApplication(sys.argv)
ex = App(40)
sys.exit(app.exec_())