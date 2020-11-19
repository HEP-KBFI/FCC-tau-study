# Useful functions

from ROOT import TLorentzVector


def get_lorentz_vector(particle):
    # Get the Lorentz Vector of a given particle
    vector = TLorentzVector()
    vector.SetXYZM(
        particle.core.p4.px,
        particle.core.p4.py,
        particle.core.p4.px,
        particle.core.p4.mass
    )
    return vector



# class Particle:
#     def __init__(self, data):
#         self.data = data
#         self.vector = TLorentzVector()
#         self.vector.SetXYZM(
#                             self.data.core.p4.px,
#                             self.data.core.p4.py,
#                             self.data.core.p4.px,
#                             self.data.core.p4.mass
#         )

#     def deltaR_comparison(self, other):
#         deltaR = self.vector.DeltaR(other.vector)
#         return deltaR


# class ParticleList:
#     def __init__(self, *particles):
#         self.particles = []
#         for particle in particles:
#             self.particles.append(particle)

#     def get_vectors(self):
#         vectors = []
#         for particle in self.particles:
#             vectors.append(particle.vector)
#         return vectors

#     def calculate_mass(self):
#         for i, vector in enumerate(get_vectors(self)):
#             if i == 0:
#                 sum_vector = vector
#             else:
#                 sum_vector += vector
#         self.mass = sum_vector.M()
#         return self.mass

#     def cross_deltaR_comparison(self, other):
#         for particle1 in self.particles:
#             for particle2 in other.particles:
#                 particle1.deltaR_comparison(particle2)