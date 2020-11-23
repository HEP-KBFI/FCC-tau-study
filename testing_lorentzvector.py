# Testing different Lorentz vector functions

import utils
from ROOT import Math, TFile, TH1D, TLorentzVector

def get_lorentz_vector_new(particle):
    # Get the Lorentz Vector of a given particle
    vector = Math.PxPyPzMVector(
        particle.core.p4.px,
        particle.core.p4.py,
        particle.core.p4.pz,
        particle.core.p4.mass
    )
    return vector


def check_pt(vector, limit):
    # Check whether the transverse momentum corresponding to a given Lorentz vector is over the given limit (GeV)
    try:
        pT = vector.Perp()
    except:
        pT = vector.Perp2()
    finally:
        if pT > limit:
            return True
        return False


def find_muon_pair_new(tree):
    # Find a pair of two oppositely charged muons
    muons = tree.muons
    pair = None
    n_mu = len(muons)
    for i in range(n_mu - 1):
        vector1 = get_lorentz_vector_new(muons[i])
        if not check_pt(vector1, 15):
            continue
        if not check_isolation(tree, i):
            continue
        ch1 = muons[i].core.charge
        for j in range(i + 1, n_mu):
            vector2 = get_lorentz_vector_new(muons[j])
            if not check_pt(vector2, 15):
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


def find_muon_pair_new_nofilter(tree):
    # Find a pair of two oppositely charged muons
    muons = tree.muons
    pair = None
    n_mu = len(muons)
    for i in range(n_mu - 1):
        vector1 = get_lorentz_vector_new(muons[i])
        ch1 = muons[i].core.charge
        for j in range(i + 1, n_mu):
            vector2 = get_lorentz_vector_new(muons[j])
            ch2 = muons[j].core.charge
            if ch1 * ch2 < 0:
                pair = {
                    muons[i]: vector1,
                    muons[j]: vector2
                }
    return pair


def find_muon_pair(tree):
    # Find a pair of two oppositely charged muons
    muons = tree.muons
    pair = None
    n_mu = len(muons)
    for i in range(n_mu - 1):
        vector1 = utils.get_lorentz_vector(muons[i])
        if not check_pt(vector1, 15):
            continue
        if not check_isolation(tree, i):
            continue
        ch1 = muons[i].core.charge
        for j in range(i + 1, n_mu):
            vector2 = utils.get_lorentz_vector(muons[j])
            if not check_pt(vector2, 15):
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


def find_muon_pair_nofilter(tree):
    # Find a pair of two oppositely charged muons
    muons = tree.muons
    pair = None
    n_mu = len(muons)
    for i in range(n_mu - 1):
        vector1 = utils.get_lorentz_vector(muons[i])
        ch1 = muons[i].core.charge
        for j in range(i + 1, n_mu):
            vector2 = utils.get_lorentz_vector(muons[j])
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
outf = TFile('data/lorentz.root', 'RECREATE')

# histogram settings
title = 'mass (GeV)'
bins = 15
low = 50
high = 150
histogram1 = TH1D('old', title, bins, low, high)
histogram2 = TH1D('new', title, bins, low, high)

# read events
tree = inf.Get('events')
n_tot = tree.GetEntries()
for event in range(n_tot):
    tree.GetEntry(event)
    muon_pair1 = None
    muon_pair2 = None
    if len(tree.muons) >= 2:
        muon_pair1 = find_muon_pair_nofilter(tree)
        muon_pair2 = find_muon_pair_new_nofilter(tree)
    if muon_pair1:
        mass1 = utils.calculate_mass(muon_pair1)
        histogram1.Fill(mass1)
    if muon_pair2:
        mass2 = utils.calculate_mass(muon_pair2)
        histogram2.Fill(mass2)

outf.Write()