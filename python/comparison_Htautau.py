# Comparing tau energies from generator level and reconstruction level results
from ROOT import TFile, TH1D
import utils


def get_gen_tau_masses(collection):
    vectors = []

    # try to get positive tau jet Lorentz vector
    try:
        vectors.append(collection[-15] - collection[-16])
    except UnboundLocalError:
        pass

    # try to get negative tau jet Lorentz vector
    try:
        vectors.append(collection[15] - collection[16])
    except UnboundLocalError:
        pass

    # calculate masses
    masses = []
    for vector in vectors:
        masses.append(vector.M())

    return masses


def get_tau_collection(tree):
    # get data from tree
    jets = tree.jets
    tau_tags = tree.tauTags
    gen_particles = tree.skimmedGenParticles
    tau_collection = []

    # loop through reconstructed jets
    for i in range(len(jets)):
        curr_set = {}

        # select only tau-tagged jets
        if tau_tags[i].tag < 0.5:
            continue

        # get lorentz vector of selected jet
        vector = utils.get_lorentz_vector(jets[i])

        # find a matching generator tau particle for reconstructed jet
        for particle in gen_particles:

            # select only taus
            pdg = particle.core.pdgId
            if abs(pdg) == 15:

                # find delta R of tau jet w.r.t generated tau
                deltaR = vector.DeltaR(utils.get_lorentz_vector(particle))

                # select generated tau with small delta R
                if deltaR < 0.05:
                    curr_set = {
                        'gen': particle,
                        'rec': jets[i],
                        'rec_vector': vector
                    }
                    break

        # find corresponding neutrino for gen tau
        if curr_set:
            for particle in gen_particles:

                # select only tau neutrinos
                pdg = particle.core.pdgId
                if abs(pdg) == 16:

                    # check if charges match
                    if pdg * curr_set['gen'].core.pdgId > 0:
                        curr_set.update({'gen_neutrino': particle})

            # add found set into collection
            tau_collection.append(curr_set)

        else:
            print('Reconstructed tau jet found with no matching generator tau particle')

    return tau_collection


def get_gen_tau_mass(tau_set):
    tau_vector = utils.get_lorentz_vector(tau_set['gen'])
    neutrino_vector = utils.get_lorentz_vector(tau_set['gen_neutrino'])
    jet_vector = tau_vector - neutrino_vector
    mass = jet_vector.M()
    return mass


def get_rec_tau_mass(tau_set):
    vector = tau_set['rec_vector']
    mass = vector.M()
    return mass


def get_tau_masses(collection):
    masses = {
        'gen': [],
        'rec': []
    }

    for tau_set in collection:
        masses['gen'].append(get_gen_tau_mass(tau_set))
        masses['rec'].append(get_rec_tau_mass(tau_set))

    return masses


def get_gen_tau_energy(tau_set):
    tau_vector = utils.get_lorentz_vector(tau_set['gen'])
    neutrino_vector = utils.get_lorentz_vector(tau_set['gen_neutrino'])
    jet_vector = tau_vector - neutrino_vector
    energy = jet_vector.E()
    return energy


def get_rec_tau_energy(tau_set):
    vector = tau_set['rec_vector']
    energy = vector.E()
    return energy


def get_tau_energies(collection):
    energies = {
        'gen': [],
        'rec': []
    }

    for tau_set in collection:
        energies['gen'].append(get_gen_tau_energy(tau_set))
        energies['rec'].append(get_rec_tau_energy(tau_set))

    return energies


def compare_tau_energies(tau_energies):
    relative = []
    absolute = []

    gen_energies = tau_energies['gen']
    rec_energies = tau_energies['rec']

    for i, gen_energy in enumerate(gen_energies):
        relative.append(rec_energies[i] / gen_energy)
        absolute.append(rec_energies[i] - gen_energy)

    return relative, absolute


def compare_parts_energies(tau_energies, parts_energies):
    relative = []
    absolute = []

    gen_energies = tau_energies['gen']

    for i, parts_energy in enumerate(parts_energies):
        relative.append(parts_energy / gen_energies[i])
        absolute.append(parts_energy - gen_energies[i])

    return relative, absolute


def get_jetparts(tree, jet):
    vectors = []
    jetparts = tree.jetParts
    begin = jet.particles_begin
    end = jet.particles_end

    for jetpart in jetparts[begin:end]:
        vectors.append(utils.get_lorentz_vector(jetpart))

    return vectors


# files
inf = TFile('data/p8_ee_ZH.root')
outf = TFile('data/histo_comparison.root', 'RECREATE')

relative_hist1 = TH1D('relative_rec_gen', 'Erec/Egen', 10, 0.75, 1.25)
relative_hist2 = TH1D('relative_parts_gen', 'Eparts/Egen', 10, 0.75, 1.25)
absolute_hist1 = TH1D('absolute_rec_gen', 'Erec - Egen', 20, -5, 10)
absolute_hist2 = TH1D('absolute_parts_gen', 'Eparts - Egen', 20, -5, 10)

# read events
tree = inf.Get('events')
n_tot = tree.GetEntries()
for event in range(n_tot):

    print('===============================')
    print('===============================')

    tree.GetEntry(event)

    print('Event ', event + 1)

    tau_collection = get_tau_collection(tree)

    if not tau_collection:
        print('No matches found / No reconstructed tau jets found')
        continue

    print('Chosen generator tau particles:')
    for tau_set in tau_collection:
        print('ID ', tau_set['gen'].core.pdgId)

    print('-------------------------------')

    tau_energies = get_tau_energies(tau_collection)

    print('Generated tau jet energies:')
    for energy in tau_energies['gen']:
        print(energy)

    print('-------------------------------')

    print('Reconstructed tau jet energies:')
    for energy in tau_energies['rec']:
        print(energy)

    relative, absolute = compare_tau_energies(tau_energies)

    for value in relative:
        relative_hist1.Fill(value)

    for value in absolute:
        absolute_hist1.Fill(value)

    print('-------------------------------')

    parts_energies = []

    for tau_set in tau_collection:
        jetpart_vectors = get_jetparts(tree, tau_set['rec'])
        print('Reconstructed jet constituents\' energies:')

        energy_sum = 0

        for jetpart in jetpart_vectors:
            energy = jetpart.E()
            print(energy)
            energy_sum += energy

        print('Sum of constituents\' energy:')
        print(energy_sum)

        parts_energies.append(energy_sum)

    relative2, absolute2 = compare_parts_energies(tau_energies, parts_energies)

    for value in relative2:
        relative_hist2.Fill(value)

    for value in absolute2:
        absolute_hist2.Fill(value)

# write to file
outf.Write()
