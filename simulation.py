from PyQt5.QtWidgets import (QWidget, QSlider, QApplication,
                             QHBoxLayout, QVBoxLayout)
from PyQt5.QtCore import QObject, Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QColor
import sys

from canvas import CanvasWidget
from particles import Particle

from numpy.random import rand
import numpy as np


class Communicate(QObject):
    updateBW = pyqtSignal(int)

class Example(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_particles)
        self.timer.start(40)

        self.p_size = 0.8
        self.gravity = 2

        sld = QSlider(Qt.Horizontal, self)
        sld.setFocusPolicy(Qt.NoFocus)
        sld.setRange(2, 100)
        sld.setValue(30)
        sld.setGeometry(130, 40, 250, 30)
        #sld.setMinimumSize(300, 100)
        self.setMinimumSize(500, 500)

        self.c = Communicate()

        black = QColor(30, 30, 30)
        grey = QColor(250, 250, 250)
        green = QColor(240, 0, 50)
        self.pixel_map = np.zeros(shape=(500, 500))

        self.wid = CanvasWidget(500, 500, grey, green, border=3, border_color=black)
        self.boundaries = (0, 500, 500, 0)


        self.moving_particles = [Particle(rand() * 500, rand() * 500, self.p_size) for _ in range(500)]
        central = Particle(250, 250, self.p_size)
        central.solid = True
        central.make_pixel_stamp(self.pixel_map)
        self.solid_particles = [central]

        self.wid.set_particles(self.moving_particles + [central])
        #self.c.updateBW[int].connect(self.wid.setValue)

        sld.valueChanged[int].connect(self.changeValue)
        hbox = QHBoxLayout()
        hbox.addWidget(self.wid)
        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

        self.setGeometry(300, 300, 600, 600)
        self.setWindowTitle("test")
        self.show()

    def changeValue(self, value):
        self.gravity = value / 10

    def update_particles(self):
        #self.wid.setValue(value)#self.c.updateBW.emit(value)

        #if len(self.solid_particles) > 100:
        #    old = self.solid_particles[:50]
        #    self.solid_particles = self.solid_particles[50:]
        #    self.old_particles = old



        if len(self.moving_particles) < 100:
            xdd = [Particle(rand() * 500, rand() * 500, self.p_size) for _ in range(100)]
            self.moving_particles += xdd

        for p in self.moving_particles:
            p.make_step(self.pixel_map, 2, self.boundaries)

        new_solid = [p for p in self.moving_particles if p.solid]
        new_moving = [p for p in self.moving_particles if not p.solid]

        #new_solid = [p for p in self.moving_particles if p.check_pixel_collision(self.pixel_map, 500, 500)]
        #new_moving = [p for p in self.moving_particles if not p.check_pixel_collision(self.pixel_map, 500, 500)]

        #new_solid = [p for p in self.moving_particles if p.collides(self.solid_particles)]
        #new_moving = [p for p in self.moving_particles if not p.collides(self.solid_particles)]

        #for p in new_solid:
        #    p.solid = True
        #    p.make_pixel_stamp(self.pixel_map, 500, 500)

        for p in new_moving:
            p.apply_gravity(250, 250, self.gravity)

        self.solid_particles = new_solid
        self.moving_particles = new_moving



        self.wid.set_particles(self.solid_particles + self.moving_particles)
        self.wid.repaint()


app = QApplication(sys.argv)
ex = Example()
sys.exit(app.exec_())