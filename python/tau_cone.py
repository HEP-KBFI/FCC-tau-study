# Observing particles in different sized cones around a tau
from ROOT import TFile, TH1D
import utils


def get_gen_taus(tree):
    gen_particles = tree.genParticles
    taus = []

    # loop through generator particles
    for particle in gen_particles:
        pdg = particle.core.pdgId
        status = particle.core.status

        # find taus
        if abs(pdg) == 15 and status == 2:
            vector = utils.get_lorentz_vector(particle)
            taus.append(vector)
            # print('Found tau: ', pdg, ' with energy ', vector.E())

    return taus


def get_particle_cone(tree, lorentz_vector, cone_size):
    gen_particles = tree.genParticles
    cone_particles = {}

    # loop through all generator particles
    for gen_particle in gen_particles:
        gen_vector = utils.get_lorentz_vector(gen_particle)

        # pdg = gen_particle.core.pdgId
        status = gen_particle.core.status

        # check if particle is stable
        if status != 1:
            continue

        # find delta R w.r.t given lorentz vector
        deltaR = lorentz_vector.DeltaR(gen_vector)

        # if pdg in [11, 12, -11, -12]:
        #     print('Found ', pdg, ' with delta R ', deltaR, ' and energy ', gen_vector.E())

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


def fill_histogram(particles, cones, histogram, statistics):
    # energy_diffs = []
    for i, particle in enumerate(particles):
        energy_diff = calculate_energy_difference(particle, cones[i])
        # energy_diffs.append(energy_diff)

        histogram.Fill(energy_diff)
        particle_statistics(cones[i], statistics)

    # return energy_diffs


def particle_statistics(cone, statistics):
    particles = list(cone.keys())
    for particle in particles:
        pdg = particle.core.pdgId
        if pdg in statistics:
            statistics[pdg] += 1
        else:
            statistics.update({pdg: 1})


def sort_statistics(statistics):
    sorted_statistics = {key: value for key, value in
                         sorted(statistics.items(), key=lambda item: item[1], reverse=True)}
    return sorted_statistics


def print_statistcs(statistics):
    count = 0
    for particle in statistics:
        print(particle, '\t:\t', statistics[particle])
        count += statistics[particle]
    print('Total\t:\t', count)


# files
inf = TFile('data/p8_output.root')
outf = TFile('data/tau_cone.root', 'RECREATE')

hist1 = TH1D('delta R < 0.5', 'delta E', 150, -75, 75)
hist2 = TH1D('delta R < 0.3', 'delta E', 150, -75, 75)
hist3 = TH1D('delta R < 0.1', 'delta E', 150, -75, 75)

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

    # find cones for each tau
    cones1 = []
    cones2 = []
    cones3 = []

    for i, tau in enumerate(taus):
        # print('Tau ', i + 1)

        # delta R < 0.5
        cones1.append(get_particle_cone(tree, tau, 0.5))
        # delta R < 0.3
        cones2.append(get_particle_cone(tree, tau, 0.3))
        # delta R < 0.1
        cones3.append(get_particle_cone(tree, tau, 0.1))

    # fill histograms
    fill_histogram(taus, cones1, hist1, stat1)
    fill_histogram(taus, cones2, hist2, stat2)
    fill_histogram(taus, cones3, hist3, stat3)

    # for i, energy in enumerate(energies):
    #     # print(energy)
    #     if energy < -0.5:
    #         print('Event ', event + 1)
    #         print(energy)
    # print('Tau ', i + 1)
    # cone = list(cones1[i].keys())
    # for particle in cone:
    #     print(particle.core.pdgId)
    #     print(cones1[i][particle].E())

# write to file
outf.Write()

# print out statistics
print('----------Statistics-----------')

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
