# Testing different Lorentz vector functions and comparing results

import utils
from math import sqrt
from ROOT import Math, TFile, TH1D


def get_lorentz_vector_new(particle):
    # Get the Lorentz Vector of a given particle
    vector = Math.PxPyPzMVector()
    vector.SetPx(particle.core.p4.px)
    vector.SetPy(particle.core.p4.py)
    vector.SetPz(particle.core.p4.pz)
    vector.SetM(particle.core.p4.mass)
    return vector


def check_pt(vector, limit):
    # Check whether the transverse momentum corresponding to a given Lorentz vector is over the given limit (GeV)
    pT = get_pt(vector)
    if pT > limit:
        return True
    return False


def get_pt(vector):
    # Get pT from a given Lorentz vector
    pT = None
    try:
        pT = vector.Perp()
    except AttributeError:
        pT = sqrt(vector.Perp2())
    return pT


def find_muon_pair_new(tree):
    # Find a pair of two oppositely charged muons with additional filtering (new LorentzVector)
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
    # Find a pair of two oppositely charged muons (new LorentzVector)
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
    # Find a pair of two oppositely charged muons with additional filtering (legacy TLorentzVector)
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
    # Find a pair of two oppositely charged muons (legacy TLorentzVector)
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
histograms = {}
histogram_list = [
    'old_mass_nofilter',
    'new_mass_nofilter',
    'old_mass',
    'new_mass',
    'old_pt_nofilter',
    'new_pt_nofilter',
    'old_pt',
    'new_pt'
]
for name in histogram_list:
    if name.find('pt') != -1:
        histograms.update(
            {name: TH1D(name, 'pt', bins, 0, high)}
        )
    else:
        histograms.update(
            {name: TH1D(name, 'mass (GeV)', bins, low, high)}
        )

# initializing comparison count
count_ok = 0
count_nok = 0

# read events
tree = inf.Get('events')
n_tot = tree.GetEntries()
for event in range(n_tot):
    tree.GetEntry(event)

    muon_pair_old_nofilter = None
    muon_pair_new_nofilter = None
    muon_pair_old = None
    muon_pair_new = None

    # find muon pairs
    if len(tree.muons) >= 2:
        muon_pair_old_nofilter = find_muon_pair_nofilter(tree)
        muon_pair_new_nofilter = find_muon_pair_new_nofilter(tree)
        muon_pair_old = find_muon_pair(tree)
        muon_pair_new = find_muon_pair_new(tree)

    # fill histograms
    if muon_pair_old_nofilter:
        for muon in muon_pair_old_nofilter.values():
            pt_old = get_pt(muon)
            histograms['old_pt_nofilter'].Fill(pt_old)
        mass1 = utils.calculate_mass(muon_pair_old_nofilter)
        histograms['old_mass_nofilter'].Fill(mass1)

    if muon_pair_new_nofilter:
        for muon in muon_pair_new_nofilter.values():
            pt_new = get_pt(muon)
            histograms['new_pt_nofilter'].Fill(pt_new)
        mass2 = utils.calculate_mass(muon_pair_new_nofilter)
        histograms['new_mass_nofilter'].Fill(mass2)

    if muon_pair_old:
        for muon in muon_pair_old.values():
            histograms['old_pt'].Fill(get_pt(muon))
        mass3 = utils.calculate_mass(muon_pair_old)
        histograms['old_mass'].Fill(mass3)

    if muon_pair_new:
        for muon in muon_pair_new.values():
            histograms['new_pt'].Fill(get_pt(muon))
        mass4 = utils.calculate_mass(muon_pair_new)
        histograms['new_mass'].Fill(mass4)

    # count pT matches
    if abs(pt_old - pt_new) < 5:
        count_ok += 1
    else:
        count_nok += 1

# Print out comparison
print("Equal pT: " + str(count_ok))
print("Not equal pT " + str(count_nok))

outf.Write()
