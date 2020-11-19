# Testing how to read from Delphes output file
# H->tautau

from ROOT import TFile, TH1D, TLorentzVector
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
        if not utils.check_pt(vector1, 30):
            continue
        for j in range(i + 1, n_jets):
            if tau_tags[j].tag < 0.5:
                continue
            vector2 = utils.get_lorentz_vector(jets[j])
            if not check_deltaR(vector2, tree):
                continue
            if not utils.check_pt(vector2, 30):
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


# files
inf = TFile('data/p8_ee_ZH.root')
outf = TFile('data/histo_Htautau.root', 'RECREATE')

# histogram settings
histogram = TH1D('data', 'mass (GeV)', 15, 75, 175)

# read events
tree = inf.Get('events')
n_tot = tree.GetEntries()
for event in range(n_tot):
    tree.GetEntry(event)
    jet_pair = None
    if len(tree.jets) >= 2:
        jet_pair = find_jet_pair(tree)
    if not jet_pair:
        continue
    mass = utils.calculate_mass(jet_pair)
    histogram.Fill(mass)

# write to file
outf.Write()
