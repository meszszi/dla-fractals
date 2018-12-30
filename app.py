from PyQt5.QtWidgets import (QWidget, QSlider, QApplication,
                             QHBoxLayout, QVBoxLayout,
                             QPushButton, QCheckBox, QLabel)
from PyQt5.QtCore import QObject, Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QColor
import sys

from canvas import CanvasWidget
from simulation import Simulation
from customWidgets import LabeledSlider, StatsLabel, ColorButton

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

        self.primary_color = QColor(20, 20, 20)
        self.secondary_color = QColor(20, 20, 20)
        self._default_bg_color = QColor(200, 200, 200)

        self.canvas = CanvasWidget(
            self.default_canvas_size, self.default_canvas_size,
            self._default_bg_color,
            self.primary_color,
            border=1,
            border_color=QColor(0, 0, 0)
        )

        self.simulation = None
        self.simulation_initialized = False
        self.simulation_running = False

        self.color_scalar = 0

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

        input_layout = QVBoxLayout()
        input_layout.setStretch(2, 1)
        main_layout = QHBoxLayout()

        buttons_layout = QHBoxLayout()

        self.startstop_button = QPushButton("Start", self)
        #self.start_button.setFixedWidth(200)
        self.startstop_button.clicked.connect(self.manage_simulation)
        buttons_layout.addWidget(self.startstop_button)

        self.reset_button = QPushButton("Reset", self)
        #self.reset_button.setFixedWidth(200)
        self.reset_button.clicked.connect(self.reset_simulation)
        self.reset_button.setDisabled(True)
        buttons_layout.addWidget(self.reset_button)

        input_layout.addLayout(buttons_layout)

        sliders_label_width = 200
        sliders_width = 200

        gravity_sl = LabeledSlider("Gravity", 0, 100, self, sliders_label_width,
                                   slider_width=sliders_width, widget_width=500)
        self.gravity_slider = gravity_sl.slider
        self.gravity_slider.setValue(50)
        self.gravity_slider.valueChanged.connect(self.gravity_slider_change)
        input_layout.addWidget(gravity_sl)

        part_sl = LabeledSlider("Particle radius", 1, 10, self, sliders_label_width,
                                   slider_width=sliders_width, widget_width=500)
        self.partrad_slider = part_sl.slider
        self.partrad_slider.setValue(3)
        self.partrad_slider.valueChanged.connect(self.partrad_slider_change)
        input_layout.addWidget(part_sl)

        step_sl = LabeledSlider("Random step length", 0, 10, self, sliders_label_width,
                                   slider_width=sliders_width, widget_width=500)
        self.steplength_slider = step_sl.slider
        self.steplength_slider.setValue(5)
        self.steplength_slider.valueChanged.connect(self.steplength_slider_change)
        input_layout.addWidget(step_sl)

        part_limit_sl = LabeledSlider("Moving particles limit", 1, 200, self,
                                sliders_label_width,
                                slider_width=sliders_width, widget_width=500)
        self.partlimit_slider = part_limit_sl.slider
        self.partlimit_slider.setValue(100)
        input_layout.addWidget(part_limit_sl)

        spawn_range_sl = LabeledSlider("Particles spawn range", 0, 300, self,
                                      sliders_label_width,
                                      slider_width=sliders_width,
                                      widget_width=500)
        self.spawnrange_slider = spawn_range_sl.slider
        self.spawnrange_slider.setValue(100)
        input_layout.addWidget(spawn_range_sl)

        canvas_sl = LabeledSlider("Canvas size", 100, 900, self, sliders_label_width,
                                   slider_width=sliders_width, widget_width=500)
        self.canvassize_slider = canvas_sl.slider
        self.canvassize_slider.setValue(500)
        self.canvassize_slider.valueChanged.connect(self.canvassize_slider_change)
        input_layout.addWidget(canvas_sl)

        self.drawmoving_checkbox = QCheckBox("Show moving particles", self)
        self.drawmoving_checkbox.setChecked(True)
        self.drawmoving_checkbox.stateChanged.connect(self.drawmoving_checkbox_change)
        input_layout.addWidget(self.drawmoving_checkbox)

        back_color_button = ColorButton("Background color", self,
                                        initial_color=self._default_bg_color)
        back_color_button.colorChanged.connect(self.back_color_changed)
        back_color_button.setMaximumWidth(200)
        input_layout.addWidget(back_color_button)

        primary_color_button = ColorButton("Primary color", self,
                                           initial_color=self.primary_color)
        primary_color_button.colorChanged.connect(self.primary_color_changed)
        primary_color_button.setMaximumWidth(200)
        input_layout.addWidget(primary_color_button)

        secondary_color_button = ColorButton("Secondary color", self,
                                             initial_color=self.primary_color)
        secondary_color_button.colorChanged.connect(self.secondary_color_changed)
        secondary_color_button.setMaximumWidth(200)
        input_layout.addWidget(secondary_color_button)

        color_change_sl = LabeledSlider("Color change speed", 0, 100, self,
                                  sliders_label_width,
                                  slider_width=sliders_width, widget_width=500)
        self.color_slider = color_change_sl.slider
        self.color_slider.setValue(0)
        input_layout.addWidget(color_change_sl)

        input_layout.addStretch()

        statistics_layout = QVBoxLayout()

        solid_particles_label = StatsLabel("Solid particles", 0, self, label_width=100, widget_width=300)
        self.solid_particles_value = solid_particles_label.value_label
        statistics_layout.addWidget(solid_particles_label)

        fractal_radius_label = StatsLabel("Fractal radius", 0, self, label_width=100, widget_width=300)
        self.fractal_radius_value = fractal_radius_label.value_label
        statistics_layout.addWidget(fractal_radius_label)

        input_layout.addLayout(statistics_layout)

        main_layout.addLayout(input_layout)

        main_layout.addStretch()

        canvas_layout = QVBoxLayout()
        canvas_layout.addWidget(self.canvas)
        canvas_layout.addStretch()

        main_layout.addLayout(canvas_layout)
        #self.main_layout.addStretch()
        self.setLayout(main_layout)
        self.setWindowTitle("DLA fractals")
        self.show()

        self.simulation_timer = QTimer(self)
        self.simulation_timer.timeout.connect(self.update_simulation)
        self.clear_statistics()


    def manage_simulation(self):
        if not self.simulation_initialized:
            self.simulation_initialized = True
            self.simulation = Simulation(
                self.default_canvas_size,
                self.default_canvas_size,
                self.partrad_slider.value(),
                (self.default_canvas_size // 2, self.default_canvas_size // 2),
                self.gravity_slider.value() / 100,
                self.steplength_slider.value(),
                100
            )
            self.simulation.initialize()
            self.canvas.initialize()
            self.canvas.fg_color = self.primary_color
            self.canvas.particles = self.simulation.new_solid_particles
            self.canvas.repaint()
            self.canvassize_slider.setDisabled(True)
            self.reset_button.setEnabled(True)

        if self.simulation_running:
            self._stop_simulation()

        else:
            self.simulation_timer.start(self.frame_interval)
            self.simulation_running = True
            self.startstop_button.setText("Stop")

    def _stop_simulation(self):
        self.simulation_timer.stop()
        self.simulation_running = False
        self.startstop_button.setText("Start")

    def reset_simulation(self):
        self._stop_simulation()
        self.canvas.initialize()
        self.canvas.repaint()
        self.simulation_initialized = False
        self.canvassize_slider.setEnabled(True)
        self.reset_button.setDisabled(True)
        self.clear_statistics()
        self.color_scalar = 0

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
        self.canvas.repaint()

    def back_color_changed(self, color):
        self.canvas.bg_color = color
        self.canvas.repaint()

    def primary_color_changed(self, color):
        self.primary_color = color
        self.color_scalar = 0

    def secondary_color_changed(self, color):
        self.secondary_color = color
        self.color_scalar = 0
        
    def _calculate_new_color(self):
        dr = (self.secondary_color.red() - self.primary_color.red()) * self.color_scalar
        dg = (self.secondary_color.green() - self.primary_color.green()) * self.color_scalar
        db = (self.secondary_color.blue() - self.primary_color.blue()) * self.color_scalar

        next_color = QColor(
            self.primary_color.red() + int(dr),
            self.primary_color.green() + int(dg),
            self.primary_color.blue() + int(db),
        )

        self.color_scalar += self.color_slider.value() / 10000
        self.color_scalar = min(self.color_scalar, 1.)

        return next_color

    def update_simulation(self):
        """
        Updates simulation state and repaints the canvas.
        :return:
        """

        self.simulation.moving_particles_limit = self.partlimit_slider.value()
        self.simulation.spawn_radius = self.spawnrange_slider.value()

        if not self.simulation.update_particles():
            self.stop_simulation()

        self.canvas.particles = (
            self.simulation.new_solid_particles + self.simulation.moving_particles)

        self.update_statistics()

        self.canvas.fg_color = self._calculate_new_color()

        self.canvas.repaint()

    def update_statistics(self):
        solid_particles = self.simulation.count_solid_particles()
        self.solid_particles_value.setText(str(solid_particles))

        fractal_radius = self.simulation.fractal_radius
        self.fractal_radius_value.setText("{:.2f}".format(fractal_radius))

    def clear_statistics(self):
        self.solid_particles_value.setText(str(0))
        self.fractal_radius_value.setText("{:.2f}".format(0.))

app = QApplication(sys.argv)
ex = App(40)
sys.exit(app.exec_())