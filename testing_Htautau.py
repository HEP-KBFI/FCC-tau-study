# Testing how to read from Delphes output file
# H->tautau

from ROOT import TFile, TH1D, TLorentzVector
import utils

def FindJetPair(tree):
    # Find a pair of two tau jets
    jets = tree.jets
    tautags = tree.tauTags
    pair = None
    n_jets = len(jets)
    for i in range(n_jets - 1):
        if tautags[i].tag < 0.5:
            continue
        vector1 = utils.get_lorentz_vector(jets[i])
        if not CheckPT(vector1):
            continue
        for j in range(i + 1, n_jets):
            if tautags[j].tag < 0.5:
                continue
            vector2 = utils.get_lorentz_vector(jets[j])
            if not CheckPT(vector2):
                continue
            pair = {
                jets[i]: vector1,
                jets[j]: vector2
            }
    return pair


def CheckPT(vector):
    # Check whether the transverse momentum of corresponding to a given Lorentz vector is over 30 GeV
    pT = vector.Perp()
    if pT > 30:
        return True
    return False


# files
inf = TFile('data/p8_ee_ZH.root')
outf = TFile('data/histo_Htautau.root', 'RECREATE')

# histogram settings
histogram = TH1D('data', 'mass (GeV)', 15, 75, 175)

# read events
tree = inf.Get('events')
ntot = tree.GetEntries()
for event in range(ntot):
    tree.GetEntry(event)
    jet_pair = None
    if len(tree.jets) >= 2:
        jet_pair = FindJetPair(tree)
    if not jet_pair:
        continue
    mass = utils.calculate_mass(jet_pair)
    histogram.Fill(mass)
outf.Write()