from __future__ import division
import numpy as np


class Particle:
    """
    Represents a single particle that creates the fractal.
    """

    """Dict storing all collision masks of particles of given size."""
    outer_mask = {}

    """Dict storing all pixel stamps of particles of given size."""
    pixel_stamp = {}

    def __init__(self, pos_x=0, pos_y=0, radius=1, collision_eps=0.9):
        """
        Creates particle with given position and radius.
        Initial speed is set to 0.
        Initially the particle has non-solid state.
        """
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.radius = radius
        self.speed_x = 0
        self.speed_y = 0
        self.solid = False

        if radius not in Particle.outer_mask:
            angles = np.linspace(0, 2 * np.pi, 2 * np.pi * self.radius)
            mask = [
                ((np.cos(a) * (self.radius + collision_eps)),
                 (np.sin(a) * (self.radius + collision_eps)))
                for a in angles
            ]
            Particle.outer_mask[radius] = mask

    def check_pixel_collision(self, pixel_map):
        """
        Checks if the particle's circumference intersects with any
        marked pixel on given pixel_map.
        """
        height = len(pixel_map)
        width = len(pixel_map[0])

        for mx, my in Particle.outer_mask[self.radius]:
            x = int(round(self.pos_x + mx))
            y = int(round(self.pos_y + my))
            if x < 0 or x >= width or y < 0 or y >= height:
                continue

            if pixel_map[y][x] > 0:
                return True

        if (0 < self.pos_x < width) and (0 < self.pos_y < height):
            return pixel_map[int(self.pos_y)][int(self.pos_x)] > 0

        return False

    def make_pixel_stamp(self, pixel_map):
        """
        Marks all pixels within the particle's range on given pixel map.
        """
        height = len(pixel_map)
        width = len(pixel_map[0])

        left = max(0, int(self.pos_x - self.radius))
        right = min(width, int(round(self.pos_x + self.radius) + 1))
        top = max(0, int(self.pos_y - self.radius))
        bottom = min(height, int(round(self.pos_y + self.radius) + 1))

        for x in range(left, right):
            for y in range(top, bottom):
                if np.square(self.pos_x - x) + np.square(
                                self.pos_y - y) <= np.square(self.radius):
                    pixel_map[y][x] = 1

    def move(self, diff_x, diff_y):
        """
        Moves the particle by given vector.
        """
        self.pos_x += diff_x
        self.pos_y += diff_y

    def apply_force(self, force_x, force_y):
        """
        Adds given force vector to particle's speed.
        """
        self.speed_x += force_x
        self.speed_y += force_y

    def apply_gravity(self, source_x, source_y, force, eps=0.0000001):
        """
        Adds speed vector pointing towards the source point
        with given force value.
        """
        diff_x = source_x - self.pos_x
        diff_y = source_y - self.pos_y
        diff_length = np.sqrt(np.square(diff_x) + np.square(diff_y))

        if diff_length < eps:
            return

        scalar = force / diff_length
        self.apply_force(diff_x * scalar, diff_y * scalar)

    def set_gravity(self, source_x, source_y, force):
        """
        Sets speed vector pointing towards the source point
        with given force value.
        """
        diff_x = source_x - self.pos_x
        diff_y = source_y - self.pos_y
        diff_length = np.sqrt(np.square(diff_x) + np.square(diff_y))

        scalar = force / diff_length
        self.speed_x = diff_x * scalar
        self.speed_y = diff_y * scalar

    def get_random_step(self, step_length, boundaries=None):
        """
        Applies random step of given length to the particle.
        If the boundaries are specified, the step is selected so that
        after its application the particle stays within the bounded region.

        boundaries: 4-element tuple (left_x, top_y, right_x, bottom_y)
        """
        while True:
            direction = np.random.rand() * 2 * np.pi
            step_x = np.cos(direction) * step_length
            step_y = np.sin(direction) * step_length

            if boundaries is None:
                return step_x, step_y

            else:
                left, top, right, bottom = boundaries
                if (left <= self.pos_x + step_x <= right and
                                bottom <= self.pos_y + step_y <= top):
                    return step_x, step_y

    def apply_collision(self, pixel_map):
        if not self.check_pixel_collision(pixel_map):
            return False

        self.make_pixel_stamp(pixel_map)
        self.solid = True
        return True

    def make_step(self, pixel_map, random_step_length=0, boundaries=None):
        """
        Moves particle according to it's speed and adds random step
        of given length.
        """
        dx, dy = self.get_random_step(random_step_length, boundaries)
        dx += self.speed_x
        dy += self.speed_y
        v = np.sqrt(dx ** 2 + dy ** 2)

        prev_x = self.pos_x
        prev_y = self.pos_y

        for dv in np.linspace(0., 1., num=int(v / self.radius) + 1):
            self.pos_x = prev_x + dv * dx
            self.pos_y = prev_y + dv * dy
            if self.apply_collision(pixel_map):
                return

        self.pos_x = prev_x + dx
        self.pos_y = prev_y + dy
        self.apply_collision(pixel_map)
