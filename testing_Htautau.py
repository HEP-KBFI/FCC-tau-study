# Testing how to read from Delphes output file
# H->tautau

from ROOT import TFile, TH1D, TLorentzVector

def FindJetPair(tree):
    # Find a pair of two oppositely charged muons
    jets = tree.jets
    tautags = tree.tauTags
    pair = None
    n_jets = len(jets)
    for i in range(n_jets - 1):
        if tautags[i].tag < 0.5:
            continue
        vector1 = GetLorentzVector(jets[i])
        if not CheckPT(vector1):
            continue
        for j in range(i + 1, n_jets):
            if tautags[j].tag < 0.5:
                continue
            vector2 = GetLorentzVector(jets[j])
            if not CheckPT(vector2):
                continue
            pair = {
                jets[i]: vector1,
                jets[j]: vector2
            }
    return pair


def CalculateMass(particles):
    # Calculate invariant mass
    vectors = list(particles.values())
    for i, vector in enumerate(vectors):
        if i == 0:
            sum_vector = vector
        else:
            sum_vector += vector
    mass = sum_vector.M()
    return mass


def GetLorentzVector(particle):
    # Get the Lorentz Vector of a given particle
    vector = TLorentzVector()
    vector.SetXYZM(
        particle.core.p4.px,
        particle.core.p4.py,
        particle.core.p4.px,
        particle.core.p4.mass
    )
    return vector


def CheckPT(vector):
    # Check whether the transverse momentum of corresponding to a given Lorentz vector is over 30 GeV
    pT = vector.Perp()
    if pT > 40:
        return True
    return False


def CheckIsolation(tree, i):
    # Check whether muon isolation tag is below 0.4
    iso = tree.muonITags[i].tag
    if iso < 0.4:
        return True
    return False


# files
inf = TFile('p8_ee_ZH.root')
outf = TFile('histo_Htautau.root', 'RECREATE')

# histogram settings
title = 'mass (GeV)'
bins = 15
low = 75
high = 175
histogram = TH1D('data', title, bins, low, high)

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
    mass = CalculateMass(jet_pair)
    histogram.Fill(mass)
outf.Write()