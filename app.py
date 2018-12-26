from PyQt5.QtWidgets import (QWidget, QSlider, QApplication,
                             QHBoxLayout, QVBoxLayout,
                             QPushButton, QCheckBox)
from PyQt5.QtCore import QObject, Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QColor
import sys

from canvas import CanvasWidget
from simulation import Simulation
from particles import Particle

class Communicate(QObject):
    updateBW = pyqtSignal(int)

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
        self.main_layout = QHBoxLayout()

        self.start_button = QPushButton("Start", self)
        self.start_button.clicked.connect(self.start_simulation)
        self.input_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop", self)
        self.stop_button.clicked.connect(self.stop_simulation)
        self.input_layout.addWidget(self.stop_button)

        self.reset_button = QPushButton("Reset", self)
        self.reset_button.clicked.connect(self.reset_simulation)
        self.input_layout.addWidget(self.reset_button)

        self.gravity_slider = QSlider(Qt.Horizontal, self)
        self.gravity_slider.setRange(0, 100)
        self.gravity_slider.setValue(5)
        self.gravity_slider.valueChanged.connect(self.gravity_slider_change)
        self.input_layout.addWidget(self.gravity_slider)

        self.partrad_slider = QSlider(Qt.Horizontal, self)
        self.partrad_slider.setRange(1, 10)
        self.partrad_slider.setValue(3)
        self.partrad_slider.valueChanged.connect(self.partrad_slider_change)
        self.input_layout.addWidget(self.partrad_slider)

        self.steplength_slider = QSlider(Qt.Horizontal, self)
        self.steplength_slider.setRange(0, 10)
        self.steplength_slider.setValue(5)
        self.steplength_slider.valueChanged.connect(self.steplength_slider_change)
        self.input_layout.addWidget(self.steplength_slider)

        self.canvassize_slider = QSlider(Qt.Horizontal, self)
        self.canvassize_slider.setRange(100, 1000)
        self.canvassize_slider.setValue(500)
        self.canvassize_slider.valueChanged.connect(self.canvassize_slider_change)
        self.input_layout.addWidget(self.canvassize_slider)

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