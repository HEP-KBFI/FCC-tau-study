# Testing how to read from Delphes output file
# Z->mumu

from ROOT import TFile, TH1D, TLorentzVector
import utils

def FindPair(tree):
    # Find a pair of two oppositely charged muons
    muons = tree.muons
    pair = None
    n_mu = len(muons)
    for i in range(n_mu - 1):
        vector1 = utils.get_lorentz_vector(muons[i])
        if not CheckPT(vector1):
            continue
        if not CheckIsolation(tree, i):
            continue
        ch1 = muons[i].core.charge
        for j in range(i + 1, n_mu):
            vector2 = utils.get_lorentz_vector(muons[j])
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
outf = TFile('histo_Zmumu.root', 'RECREATE')

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
    mass = utils.calculate_mass(muon_pair)
    histogram.Fill(mass) 

outf.Write()