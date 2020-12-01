# Testing how to read from Delphes output file
# H->tautau

from ROOT import TFile, TH1D, TLorentzVector
import copy
import utils


def find_jet_pair(tree):
    # Find a pair of two tau jets
    jets = tree.jets
    tau_tags = tree.tauTags
    pair = None
    n_jets = len(jets)
    for i in range(n_jets - 1):
        if tau_tags[i].tag < 0.5:
            continue
        vector1 = utils.get_lorentz_vector(jets[i])
        if not check_deltaR(vector1, tree):
            continue
        if not utils.check_pt(vector1, 15):
            continue
        for j in range(i + 1, n_jets):
            if tau_tags[j].tag < 0.5:
                continue
            vector2 = utils.get_lorentz_vector(jets[j])
            if not check_deltaR(vector2, tree):
                continue
            if not utils.check_pt(vector2, 15):
                continue
            pair = {
                jets[i]: vector1,
                jets[j]: vector2
            }
    return pair


def check_deltaR(vector, tree):
    # compares delta R w.r.t. MC taus
    mc_particles = tree.skimmedGenParticles
    for particle in mc_particles:
        pdg = particle.core.pdgId
        if abs(pdg) == 15:
            deltaR = vector.DeltaR(utils.get_lorentz_vector(particle))
            if deltaR < 0.05:
                return True
    return False


def missing_energy(tree):
    # finds neutrinos from MC particles
    mc_particles = tree.skimmedGenParticles
    neutrinos = {}
    for particle in mc_particles:
        pdg = particle.core.pdgId
        if abs(pdg) in [12, 14, 16]:
            # print(pdg, end=':')
            # print(particle.core.status, end=' ')
            neutrinos.update({particle: utils.get_lorentz_vector(particle)})
    # print('\n', end='')
    return neutrinos


# files
inf = TFile('data/p8_ee_ZH.root')
outf = TFile('data/histo_Htautau.root', 'RECREATE')

# histogram settings
histograms = {}
histogram_list = {
    'no_missing_energy',
    'with_missing_energy'
}
for name in histogram_list:
    histograms.update(
        {name: TH1D(name, 'mass (GeV)', 20, 75, 175)}
    )

# read events
tree = inf.Get('events')
n_tot = tree.GetEntries()
for event in range(n_tot):
    tree.GetEntry(event)

    # find tau jet pairs 
    jet_pair = None
    if len(tree.jets) >= 2:
        jet_pair = find_jet_pair(tree)
    if not jet_pair:
        continue

    # calculate mass without considering missing energy
    jet_pair_missing_energy = copy.deepcopy(jet_pair)
    mass_no_missing_energy = utils.calculate_mass(jet_pair)
    histograms['no_missing_energy'].Fill(mass_no_missing_energy)

    # calculate mass including missing energy calculated from MC neutrinos
    jet_pair_missing_energy.update(missing_energy(tree))
    mass_missing_energy = utils.calculate_mass(jet_pair_missing_energy)
    histograms['with_missing_energy'].Fill(mass_missing_energy)

# write to file
outf.Write()
