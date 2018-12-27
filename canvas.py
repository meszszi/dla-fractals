from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPixmap, QColor


class CanvasWidget(QWidget):
    """
    Represents the canvas on which the particles are drawn
    during the simulation.
    """

    def __init__(self, width, height, bg_color, fg_color,
                 border=0, border_color=None,
                 antialiasing=False):
        """
        Initializes the widget with given size and particles list.
        """
        super().__init__()

        # static parameters
        self.width = width
        self.height = height
        self.border = border
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.border_color = border_color
        self.draw_moving_particles = True
        self.antialiasing = antialiasing

        # dynamic parameters
        self.particles = []
        self.pixmap = None

        self.initialize()

    def paintEvent(self, e):
        """
        Executed every time the widget is redrawn on the app window.
        """
        qp = QPainter()
        qp.begin(self)
        self.draw_widget(qp)
        qp.end()

    def init_ui(self):
        """
        Initializes widget's parameters.
        """
        self.setFixedSize(self.width + 2 * self.border, self.height + 2 * self.border)

    def initialize(self):
        """
        Creates initial canvas state.
        """
        self.init_ui()
        self.particles = []
        self.pixmap = QPixmap(
            self.width + 2 * self.border,
            self.height + 2 * self.border
        )
        self.pixmap.fill(QColor(0, 0, 0, 0))
        # qp = QPainter()
        # qp.begin(self)
        # self._draw_background(qp)
        # qp.end()

    def _draw_background(self, qp):
        qp.setRenderHint(QPainter.Antialiasing, self.antialiasing)

        qp.setBrush(self.border_color)
        qp.setPen(self.border_color)
        qp.drawRect(0, 0, self.width + 2 * self.border,
                    self.height + 2 * self.border)

        qp.setBrush(self.bg_color)
        qp.setPen(self.bg_color)
        qp.drawRect(self.border, self.border, self.width, self.height)

    def _draw_solid_particles(self, qp):
        """
        Draws all solid particles from self.particles onto self.pixmap.
        """
        qp.setRenderHint(QPainter.Antialiasing, self.antialiasing)

        qp.setClipRect(self.border, self.border, self.width, self.height)
        qp.setBrush(self.fg_color)
        qp.setPen(self.fg_color)

        for p in filter(lambda o: o.solid, self.particles):
            left = p.pos_x - p.radius
            top = self.width - (p.pos_y + p.radius)
            qp.drawEllipse(left, top, p.radius * 2, p.radius * 2)

    def _draw_moving_particles(self, qp):
        """
        Draws all moving particles from self.particles using given painter.
        """
        qp.setRenderHint(QPainter.Antialiasing, self.antialiasing)

        qp.setClipRect(self.border, self.border, self.width, self.height)
        qp.setBrush(self.fg_color)
        qp.setPen(self.fg_color)

        for p in filter(lambda o: not o.solid, self.particles):
            left = p.pos_x - p.radius
            top = self.width - (p.pos_y + p.radius)
            qp.drawEllipse(left, top, p.radius * 2, p.radius * 2)

    def draw_widget(self, qp):
        """
        Draws the widget by drawing permanent pixmap and adding every non-solid
        particle to the resulting image.
        """
        permanent_qp = QPainter(self.pixmap)

        self._draw_background(qp)

        self._draw_solid_particles(permanent_qp)
        qp.drawPixmap(0, 0, self.pixmap)

        if self.draw_moving_particles:
            self._draw_moving_particles(qp)

    def change_size(self, width, height, border=0):
        """
        Modifies the size of the canvas and updates all necessary structures.
        """
        self.width = width
        self.height = height
        self.border = border

        self.initialize()
