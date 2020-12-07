# Comparing generator level and reconstruction level results
from ROOT import TFile, TH1D
# import copy
import utils


# def find_gen_taus(tree):
#     gen_particles = tree.skimmedGenParticles
#     tau_set = {}
#     for particle in gen_particles:
#         pdg = particle.core.pdgId
#         status = particle.core.status
#         if abs(pdg) == 15 and status == 2:
#             tau_set.update({particle: utils.get_lorentz_vector(particle)})
#         elif abs(pdg) == 16 and status == 1:
#             tau_set.update({particle: utils.get_lorentz_vector(particle)})
#     return tau_set


# def get_tau_vectors(tau_set):
#     particles = list(tau_set.keys())
#     tau_vectors = []
#     for particle in particles:
#         pdg = particle.core.pdgId
#         if abs(pdg) == 15:
#             tau_vectors.append(tau_set[particle])
#     return tau_vectors


# def get_tau_jet_vectors(tau_set):
#     particles = list(tau_set.keys())
#     jet_pos_vector = None
#     jet_neg_vector = None
#     for particle in particles:
#         pdg = particle.core.pdgId
#         if pdg == 15:
#             tau_pos_key = particle
#         elif pdg == -15:
#             tau_neg_key = particle
#         elif pdg == 16:
#             neutrino_pos_key = particle
#         elif pdg == -16:
#             neutrino_neg_key = particle
#     try:
#         jet_pos_vector = tau_set[tau_pos_key] - tau_set[neutrino_pos_key]
#         jet_neg_vector = tau_set[tau_neg_key] - tau_set[neutrino_neg_key]
#     except UnboundLocalError:
#         pass
#     finally:
#         return jet_pos_vector, jet_neg_vector


# def get_tau_jet_masses(tau_set):
#     tau_jet_vector1, tau_jet_vector2 = get_tau_jet_vectors(tau_set)
#     masses = []
#     try:
#         masses.append(tau_jet_vector1.M())
#         masses.append(tau_jet_vector2.M())
#     except AttributeError:
#         pass
#     finally:
#         return masses


def get_gen_tau_collection(tree):
    gen_particles = tree.skimmedGenParticles
    tau_collection = {}

    for particle in gen_particles:
        pdg = particle.core.pdgId
        status = particle.core.status

        # find taus
        if abs(pdg) == 15 and status == 2:
            tau_collection.update({pdg: utils.get_lorentz_vector(particle)})

        # find tau neutrinos
        elif abs(pdg) == 16 and status == 1:
            tau_collection.update({pdg: utils.get_lorentz_vector(particle)})

    return tau_collection


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
        match_found = False
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
                    match_found = True
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

# histogram settings
# histograms = {}
# histogram_list = {
#     'gen_taus',
#     'rec_taus',
#     'relative',
#     'absolute'
# }
# for name in histogram_list:
#     if name == 'relative':
#         title = 'Erec/Egen'
#     elif name == 'absolute':
#         title = 'Erec - Egen'
#     else:
#         title = 'mass (GeV)'
#     histograms.update(
#         {name: TH1D(name, title, 20, 0, 1)}
#     )

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
        # print('Status', tau_set['gen'].core.status)

    print('-------------------------------')

    tau_energies = get_tau_energies(tau_collection)

    print('Generated tau jet energies:')
    for energy in tau_energies['gen']:
        print(energy)
        # histograms['gen_taus'].Fill(energy)

    # print('Tau neutrino energies:')
    # for tau_set in tau_collection:
    #     print(utils.get_lorentz_vector(tau_set['gen_neutrino']).E())

    print('-------------------------------')

    print('Reconstructed tau jet energies:')
    for energy in tau_energies['rec']:
        print(energy)
        # histograms['rec_taus'].Fill(energy)

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

    # jets = tree.jets
    # print('Number of jets: ', len(jets))
    # for jet in jets:
    #     print(jet)
    #     print(jet.particles_begin, jet.particles_end)
    # jetparts = tree.jetParts
    # print('Number of jetparts: ', len(jetparts))
    # for jetpart in jetparts:
    #     print(jetpart)

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


    # gen_tau_masses = get_gen_tau_masses(gen_tau_collection)
    # for mass in gen_tau_masses:
    #     histograms['gen_taus'].Fill(mass)

    # print('Gen taus: ', gen_tau_masses, end=' - ')

    # # rec tau jets
    # rec_tau_collection = get_rec_tau_collection(tree)
    # rec_tau_masses = get_rec_tau_masses(rec_tau_collection)
    # for mass in rec_tau_masses:
    #     histograms['rec_taus'].Fill(mass)

    # print('Rec taus: ', rec_tau_masses)

    # tau_set = find_gen_taus(tree)

    # # calculate tau jet mass
    # tau_set_4_jets = copy.deepcopy(tau_set)
    # masses = get_tau_jet_masses(tau_set_4_jets)
    # for mass in masses:
    #     print(mass)
    #     histograms['tau_jets'].Fill(mass)

    # # calculate Higgs mass
    # tau_vectors = get_tau_vectors(tau_set)
    # if len(tau_vectors) != 2:
    #     print('error')
    # higgs_mass = (tau_vectors[0] + tau_vectors[1]).M()
    # histograms['higgs'].Fill(higgs_mass)

# write to file
outf.Write()
