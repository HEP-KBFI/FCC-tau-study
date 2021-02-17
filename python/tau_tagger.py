# Initial testing for creating a new tau tagger module

from ROOT import TFile
import csv
import utils


def get_jetparts(tree, jet):
    selected_jetparts = []
    jetparts = tree.jetParts
    begin = jet.particles_begin
    end = jet.particles_end
    for jetpart in jetparts[begin:end]:
        selected_jetparts.append(jetpart)
    return selected_jetparts


def find_leading_track(jet_parts, jet_part_vectors):
    curr_max = -1
    leading_track = None
    for i, part in enumerate(jet_parts):
        if part.core.charge == 0:
            continue
        pt = utils.get_pt(jet_part_vectors[i])
        if pt > curr_max:
            curr_max = pt
            leading_track = jet_part_vectors[i]
    return leading_track


def find_fractions(jetparts):
    vectors = []
    for part in jetparts:
        vectors.append(utils.get_lorentz_vector(part))

    neutral_vectors = []
    charged_vectors = []
    for i, part in enumerate(jetparts):
        if part.core.charge != 0:
            charged_vectors.append(vectors[i])
        else:
            neutral_vectors.append(vectors[i])

    vector_sum = utils.add_vectors(vectors)
    if vector_sum:
        total_energy = vector_sum.E()
    else:
        return None, None

    if total_energy == 0:
        return None, None

    charged_sum = utils.add_vectors(charged_vectors)
    if charged_sum:
        charged_energy = charged_sum.E()
        charged_fraction = charged_energy / total_energy
    else:
        charged_fraction = None

    neutral_sum = utils.add_vectors(neutral_vectors)
    if neutral_sum:
        neutral_energy = neutral_sum.E()
        neutral_fraction = neutral_energy / total_energy
    else:
        neutral_fraction = None

    return charged_fraction, neutral_fraction


def find_cone_size(jetparts):
    vectors = []
    for part in jetparts:
        vectors.append(utils.get_lorentz_vector(part))
    leading_track = find_leading_track(jetparts, vectors)
    if not leading_track:
        return None
    cone_size = 0
    for vector in vectors:
        deltaR = leading_track.DeltaR(vector)
        if deltaR > cone_size:
            cone_size = deltaR
    return cone_size


def get_eta(jet):
    vector = utils.get_lorentz_vector(jet)
    return vector.Eta()


# Opening and reading the input file
inf = TFile('data/delphes_Htautau.root')
tree = inf.Get('events')
n_tot = tree.GetEntries()

# Preparing the output file
outf = open('data/tau_tagger.csv', 'w')
fieldnames = ['n_charged', 'n_neutral', 'd_R', 'm', 'charged_fraction', 'neutral_fraction', 'eta']
writer = csv.DictWriter(outf, fieldnames=fieldnames)
writer.writeheader()

# Loop through events
for event in range(n_tot):
    tree.GetEntry(event)
    jets = tree.jets
    for i, jet in enumerate(jets):
        jetparts = get_jetparts(tree, jet)
        n_charged = 0
        n_neutral = 0
        for part in jetparts:
            if part.core.charge != 0:
                n_charged += 1
            else:
                n_neutral += 1
        deltaR = find_cone_size(jetparts)
        mass = utils.calculate_mass(jetparts)
        charged_fraction, neutral_fraction = find_fractions(jetparts)
        writer.writerow({
            'n_charged': n_charged,
            'n_neutral': n_neutral,
            'd_R': deltaR,
            'm': mass,
            'charged_fraction': charged_fraction,
            'neutral_fraction': neutral_fraction,
            'eta': get_eta(jet)
        })

outf.close()
