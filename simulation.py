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
                 spawns, particles_per_spawn,
                 min_spawn_radius, max_spawn_radius,
                 destroy_radius=None
                 ):
        """
        Initializes simulation parameters
        :param width:               simulation area width
        :param height:              simulation area height
        :param particle_radius:     size of a single particle
        :param gravity_center:      coordinates of gravity center
        :param gravity_force:       value of gravity force
        :param rand_step_length:    length of random step applied to each moving particle
        :param spawns:              number of spawns that will be simulated
        :param particles_per_spawn: number of particles spawned in each single spawn
        :param min_spawn_radius:    minimal distance from gravity center to newly spawned particle
        :param max_spawn_radius:    maximal distance from gravity center to newly spawned particle
        :param destroy_radius:      radius limiting the area outside which all the particles are destroyed
        """

        self.width = width
        self.height = height
        self.particle_radius = particle_radius

        self.gravity_center = gravity_center
        self.gravity_force = gravity_force

        self.rand_step_length = rand_step_length

        self.spawns = spawns
        self.spawn_number = None
        self.particles_per_spawn = particles_per_spawn

        self.min_spawn_radius = min_spawn_radius
        self.max_spawn_radius = max_spawn_radius
        self.destroy_radius = destroy_radius

        self.collision_map = None
        self.solid_particles = []
        self.moving_particles = []

        self.new_solid_particles = []

    def initialize_simulation(self):
        """
        Creates initial simulation state.
        """
        self.spawn_number = 0

        self.collision_map = np.zeros(shape=(self.height, self.width))

        center = Particle(
            self.gravity_center[0],
            self.gravity_center[1],
            self.particle_radius)
        center.solid = True

        center.make_pixel_stamp(self.collision_map)

        self.solid_particles = [center]
        self.moving_particles = []
        self.new_solid_particles = []

    def spawn_particles(self):
        """
        Spawns new particles set.
        Returns false if the limit of spawns number is reached, true otherwise.
        """
        if self.spawn_number == self.spawns:
            return False

        self.spawn_number += 1

        radius_range = self.max_spawn_radius - self.min_spawn_radius

        def rand_particle():
            r = rand() * radius_range + self.min_spawn_radius
            a = rand() * 2 * np.pi
            return Particle(
                self.gravity_center[0] + np.cos(a) * r,
                self.gravity_center[1] + np.sin(a) * r,
                self.particle_radius
            )

        new_particles = [rand_particle() for _ in range(self.particles_per_spawn)]
        self.moving_particles += new_particles
        return True

    def update_particles(self):
        """
        Moves all particles and checks collisions.
        Returns false if there are no particles to move, true otherwise.
        """

        if len(self.moving_particles) == 0:
            return False

        def outside_limit(p):
            if self.destroy_radius is None:
                return False

            squared_dist = (p.pos_x - self.gravity_center[0])**2 + \
                           (p.pos_y - self.gravity_center[1])**2

            return squared_dist > self.destroy_radius**2

        self.moving_particles = [p for p in self.moving_particles if not outside_limit(p)]

        for p in self.moving_particles:
            p.apply_gravity(
                self.gravity_center[0],
                self.gravity_center[1],
                self.gravity_force
            )
            p.make_step(self.collision_map, self.rand_step_length)

        new_solid = [p for p in self.moving_particles if p.solid]
        new_moving = [p for p in self.moving_particles if not p.solid]

        self.solid_particles += new_solid
        self.moving_particles = new_moving
        self.new_solid_particles = new_solid

        return True
