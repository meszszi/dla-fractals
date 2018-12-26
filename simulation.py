from particles import Particle

from numpy.random import rand
import numpy as np


class Simulation:
    """
    Performs fractal generating simulation, responsible for spawning new
    random particles
    """

    def __init__(self,
                 width, height,
                 particle_radius,
                 gravity_center, gravity_force,
                 rand_step_length,
                 spawn_radius,
                 particles_limit=-1,
                 moving_particles_limit=100
                 ):
        """
        Initializes simulation parameters
        :param width:               simulation area width
        :param height:              simulation area height
        :param particle_radius:     size of a single particle
        :param gravity_center:      coordinates of gravity center
        :param gravity_force:       value of gravity force
        :param rand_step_length:    length of random step applied to each moving particle
        :param spawn_radius:        distance from the gravity center where the particles are created
        :param particles_limit:     number of all particles to be created during the simulation
        :moving_particles_limit:    maximal number of moving particles that can be simulated
        """

        # static parameters
        self.width = width
        self.height = height
        self.particle_radius = particle_radius

        self.gravity_center = gravity_center
        self.gravity_force = gravity_force

        self.rand_step_length = rand_step_length

        self.particles_limit = particles_limit
        self.moving_particles_limit = moving_particles_limit

        self.spawn_radius = spawn_radius

        # dynamic parameters
        self.collision_map = None

        self.moving_particles = []
        self.new_solid_particles = []
        self.particles_count = 0

        self.fractal_radius = 0

    def initialize(self):
        """
        Creates clear initial simulation state.
        """
        self.collision_map = np.zeros(shape=(self.height, self.width))

        center = Particle(
            self.gravity_center[0],
            self.gravity_center[1],
            self.particle_radius)
        center.solid = True

        center.make_pixel_stamp(self.collision_map)

        self.moving_particles = []
        self.new_solid_particles = [center]
        self.particles_count = 1
        self.fractal_radius = 0

    def _produce_particles(self):
        """
        Creates new particles set.
        Returns false if no more particles can be created.
        """
        count = min(
            self.particles_limit - self.particles_count,
            self.moving_particles_limit, len(self.moving_particles)
        )

        if self.particles_limit == -1:
            count = self.moving_particles_limit - len(self.moving_particles)

        def rand_particle():
            a = rand() * 2 * np.pi
            r = rand() * self.spawn_radius + self.fractal_radius
            return Particle(
                self.gravity_center[0] + np.cos(a) * r,
                self.gravity_center[1] + np.sin(a) * r,
                self.particle_radius
            )

        new_particles = [rand_particle() for _ in range(count)]
        self.moving_particles += new_particles
        return True

    def update_particles(self):
        """
        Moves all particles and checks collisions.
        Returns false if there are no particles to move, true otherwise.
        """
        self._produce_particles()

        if len(self.moving_particles) == 0:
            return False

        for p in self.moving_particles:
            p.apply_gravity(
                self.gravity_center[0],
                self.gravity_center[1],
                self.gravity_force
            )
            p.make_step(self.collision_map, self.rand_step_length)

        new_solid = [p for p in self.moving_particles if p.solid]
        new_moving = [p for p in self.moving_particles if not p.solid]

        for p in new_solid:
            fr = (p.pos_x - self.gravity_center[0])**2 + \
                 (p.pos_y - self.gravity_center[1])**2
            fr = np.sqrt(fr)
            if fr > self.fractal_radius:
                self.fractal_radius = fr

        self.moving_particles = new_moving
        self.new_solid_particles = new_solid

        return True
