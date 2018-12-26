from PyQt5.QtWidgets import (QWidget, QSlider, QApplication,
                             QHBoxLayout, QVBoxLayout,
                             QPushButton)
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

    def __init__(self, frame_interval):
        """
        Initializes all app's parameters.
        """
        super().__init__()

        self.frame_interval = frame_interval

        self.simulation = Simulation(
            700, 700, 3,
            (350, 350), 0.05,
            2.5,
            -1, 100,
            200, 500
        )

        self.simulation_initialized = False

        self.init_ui()

    def init_ui(self):

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
        self.gravity_slider.setRange(0, 20)
        self.gravity_slider.setValue(5)
        self.gravity_slider.valueChanged.connect(self.gravity_slider_change)

        self.input_layout.addWidget(self.gravity_slider)

        self.canvas = CanvasWidget(
            700, 700,
            QColor(30, 30, 30),
            QColor(250, 250, 250),
            border=3,
            border_color=QColor(240, 0, 50)
        )

        self.main_layout.addLayout(self.input_layout)
        self.main_layout.addWidget(self.canvas)
        self.setLayout(self.main_layout)
        self.show()

        self.simulation_timer = QTimer(self)
        self.simulation_timer.timeout.connect(self.update_simulation)


    def start_simulation(self):
        print('start')
        if not self.simulation_initialized:
            self.simulation_initialized = True
            self.simulation.initialize_simulation()
            self.canvas.set_particles(self.simulation.solid_particles)
            self.canvas.repaint()
            
        self.simulation_timer.start(self.frame_interval)

    def stop_simulation(self):
        print('stop')
        self.simulation_timer.stop()

    def reset_simulation(self):
        self.stop_simulation()
        self.canvas.clear()
        self.canvas.repaint()
        self.simulation_initialized = False

    def gravity_slider_change(self, value):
        scalar = 10
        self.simulation.gravity_force = value / scalar

    def update_simulation(self):
        """
        Updates simulation state and repaints the canvas.
        :return:
        """
        if not self.simulation.update_particles():
            if not self.simulation.spawn_particles():
                self.stop_simulation()

        self.canvas.set_particles(
            self.simulation.new_solid_particles + self.simulation.moving_particles)

        self.canvas.repaint()

app = QApplication(sys.argv)
ex = App(40)
sys.exit(app.exec_())