# Testing how to read from Delphes output file
# Z->mumu

from ROOT import TFile, TH1D
import utils


def find_muon_pair(tree):
    # Find a pair of two oppositely charged muons
    muons = tree.muons
    pair = None
    n_mu = len(muons)
    for i in range(n_mu - 1):
        vector1 = utils.get_lorentz_vector(muons[i])
        if not utils.check_pt(vector1, 15):
            continue
        if not check_isolation(tree, i):
            continue
        ch1 = muons[i].core.charge
        for j in range(i + 1, n_mu):
            vector2 = utils.get_lorentz_vector(muons[j])
            if not utils.check_pt(vector2, 15):
                continue
            if not check_isolation(tree, j):
                continue
            ch2 = muons[j].core.charge
            if ch1 * ch2 < 0:
                pair = {
                    muons[i]: vector1,
                    muons[j]: vector2
                }
    return pair


def check_isolation(tree, i):
    # Check whether muon isolation tag is below 0.4
    iso = tree.muonITags[i].tag
    if iso < 0.4:
        return True
    return False


# files
inf = TFile('data/p8_ee_ZH.root')
outf = TFile('data/histo_Zmumu.root', 'RECREATE')

# histogram settings
title = 'mass (GeV)'
bins = 15
low = 50
high = 150
histogram = TH1D('data', title, bins, low, high)

# read events
tree = inf.Get('events')
n_tot = tree.GetEntries()
for event in range(n_tot):
    tree.GetEntry(event)
    muon_pair = None
    if len(tree.muons) >= 2:
        muon_pair = find_muon_pair(tree)
    if not muon_pair:
        continue
    mass = utils.calculate_mass(muon_pair)
    histogram.Fill(mass)

outf.Write()
