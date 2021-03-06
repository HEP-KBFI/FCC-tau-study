# Useful functions
from ROOT import Math, TLorentzVector


def get_lorentz_vector(particle):
    # Get the Lorentz Vector of a given particle (Legacy TLorentzVector class)
    vector = TLorentzVector()
    vector.SetXYZM(
        particle.core.p4.px,
        particle.core.p4.py,
        particle.core.p4.pz,
        particle.core.p4.mass
    )
    return vector


def get_lorentz_vector_new(particle):
    # Get the Lorentz Vector of a given particle (Math::LorentzVector class)
    vector = Math.PxPyPzMVector()
    vector.SetPx(particle.core.p4.px)
    vector.SetPy(particle.core.p4.py)
    vector.SetPz(particle.core.p4.pz)
    vector.SetM(particle.core.p4.mass)
    return vector


def calculate_mass(particles):
    # Calculate invariant mass
    vectors = list(particles.values())
    for i, vector in enumerate(vectors):
        if i == 0:
            sum_vector = vector
        else:
            sum_vector += vector
    mass = sum_vector.M()
    return mass


def check_pt(vector, limit):
    # Check whether the transverse momentum corresponding to a given Lorentz vector is over the given limit (GeV)
    pT = get_pt(vector)
    if pT > limit:
        return True
    return False


def get_pt(vector):
    # Get pT from a given Lorentz vector
    pT = None
    try:
        pT = vector.Perp()
    except AttributeError:
        pT = Math.sqrt(vector.Perp2())
    return pT
