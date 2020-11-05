# Testing how to read from Delphes output file
# Z->mumu

from ROOT import TFile, TH1D, TLorentzVector

def FindPair(tree):
    # Find a pair of two oppositely charged muons
    muons = tree.muons
    pair = None
    n_mu = len(muons)
    for i in range(n_mu - 1):
        vector1 = GetLorentzVector(muons[i])
        if not CheckPT(vector1):
            continue
        if not CheckIsolation(tree, i):
            continue
        ch1 = muons[i].core.charge
        for j in range(i + 1, n_mu):
            vector2 = GetLorentzVector(muons[j])
            if not CheckPT(vector2):
                continue
            if not CheckIsolation(tree, j):
                continue
            ch2 = muons[j].core.charge
            if ch1 * ch2 < 0:
                pair = {
                    muons[i]: vector1, 
                    muons[j]: vector2
                }
    return pair


def CalculateMass(muons):
    # Calculate invariant mass of muon pair
    vectors = list(muons.values())
    mass = (vectors[0] + vectors[1]).M()
    return mass


def GetLorentzVector(muon):
    # Get the Lorentz Vector of a given muon
    vector = TLorentzVector()
    vector.SetXYZM(
        muon.core.p4.px,
        muon.core.p4.py,
        muon.core.p4.px,
        muon.core.p4.mass
    )
    return vector


def CheckPT(vector):
    # Check whether the transverse momentum of corresponding to a given Lorentz vector is over 15 GeV
    pT = vector.Perp()
    if pT > 15:
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
outf = TFile('histogram.root', 'RECREATE')

# histogram settings
title = 'mass (GeV)'
bins = 15
low = 50
high = 150
histogram = TH1D('data', title, bins, low, high)

# read events
tree = inf.Get('events')
ntot = tree.GetEntries()
for event in range(ntot):
    tree.GetEntry(event)
    muon_pair = None
    if len(tree.muons) >= 2:
        muon_pair = FindPair(tree)
    if not muon_pair:
        continue
    mass = CalculateMass(muon_pair)
    histogram.Fill(mass) 

outf.Write()