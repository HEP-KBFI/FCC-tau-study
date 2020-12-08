from ROOT import TFile, TH1D
import utils

def get_gen_taus(tree):
    gen_particles = tree.skimmedGenParticles
    taus = []

    # loop through generator particles
    for particle in gen_particles:
        pdg = particle.core.pdgId
        status = particle.core.status

        # find taus
        if abs(pdg) == 15 and status == 2:
            taus.append(utils.get_lorentz_vector(particle))

    return taus


def get_particle_cone(tree, lorentz_vector, cone_size):
    gen_particles = tree.skimmedGenParticles
    cone_particles = {}

    # loop through all generator particles
    for gen_particle in gen_particles:
        gen_vector = utils.get_lorentz_vector(gen_particle)

        # check if particle is stable
        if gen_particle.core.status != 1:
            continue

        # find delta R w.r.t given lorentz vector
        deltaR = lorentz_vector.DeltaR(gen_vector)

        # compare delta R to given cone size
        if deltaR < cone_size:
            cone_particles.update({gen_particle: gen_vector})

    return cone_particles


def calculate_energy_difference(particle, cone):
    energy_diff = 0
    cone_particles = list(cone.values())
    for cone_particle in cone_particles:
        energy_diff += cone_particle.E()
    energy_diff -= particle.E()
    return energy_diff


def fill_histogram(tree, particles, cone_size, histogram, statistics):
    for particle in particles:
        cone = get_particle_cone(tree, particle, cone_size)
        energy_diff = calculate_energy_difference(particle, cone)
        histogram.Fill(energy_diff)
        particle_statistics(cone, statistics)


def particle_statistics(cone, statistics):
    particles = list(cone.keys())
    for particle in particles:
        pdg = particle.core.pdgId
        if pdg in statistics:
            statistics[pdg] += 1
        else:
            statistics.update({pdg: 1})


def sort_statistics(statistics):
    sorted_statistics = {key: value for key, value in sorted(statistics.items(), key=lambda item: item[1], reverse=True)}
    return sorted_statistics


def print_statistcs(statistics):
    count = 0
    for particle in statistics:
        print(particle, '\t:\t', statistics[particle])
        count += statistics[particle]
    print('Total\t:\t', count)


# files
inf = TFile('data/p8_ee_ZH.root')
outf = TFile('data/tau_cone.root', 'RECREATE')

hist1 = TH1D('delta R < 0.5', 'delta E', 200, -100, 100)
hist2 = TH1D('delta R < 0.3', 'delta E', 200, -100, 100)
hist3 = TH1D('delta R < 0.1', 'delta E', 200, -100, 100)

stat1 = {}
stat2 = {}
stat3 = {}

# read events
tree = inf.Get('events')
n_tot = tree.GetEntries()
for event in range(n_tot):

    tree.GetEntry(event)

    # find all generator taus
    taus = get_gen_taus(tree)

    fill_histogram(tree, taus, 0.5, hist1, stat1)
    fill_histogram(tree, taus, 0.3, hist2, stat2)
    fill_histogram(tree, taus, 0.1, hist3, stat3)

# write to file
outf.Write()

# print out statistics
print('-------------------------------')

print("delta R < 0.5")
stat1 = sort_statistics(stat1)
print_statistcs(stat1)

print('-------------------------------')

print("delta R < 0.3")
stat2 = sort_statistics(stat2)
print_statistcs(stat2)

print('-------------------------------')

print("delta R < 0.1")
stat3 = sort_statistics(stat3)
print_statistcs(stat3)

print('-------------------------------')
