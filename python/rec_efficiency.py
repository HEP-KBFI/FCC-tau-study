# Plotting the efficiency and fake rate of tau reconstruction

from ROOT import TFile, TEfficiency
import utils

def find_gen_match(tree, jet):

    gen_particles = tree.skimmedGenParticles

    final_taus = []
    other_taus = []

    for particle in gen_particles:
        pdg = particle.core.pdgId
        status = particle.core.status

        if abs(pdg) != 15:
            continue

        if status == 2:
            final_taus.append(particle)
        else:
            other_taus.append(particle)

    rec_vector = utils.get_lorentz_vector(jet)

    for tau in final_tau:
        gen_vector = utils.get_lorentz_vector(tau)
        deltaR = rec_vector.DeltaR(gen_vector)
        if deltaR < 0.05:
            return True

    for tau in other_taus:
        gen_vector = utils.get_lorentz_vector(tau)
        deltaR = rec_vector.DeltaR(gen_vector)
        if deltaR < 0.05:
            return True

    return False


def fill_histograms(tree, efficiency_histo, fake_histo):
    jets = tree.jets
    tau_tags = tree.tauTags
    gen_particles = tree.skimmedGenParticles

    for i in range(len(jets)):

        if tau_tags[i].tag < 0.5:
            continue

        vector = utils.get_lorentz_vector(jets[i])
        pt = utils.get_pt(vector)

        # all_histo.Fill(pt)

        selection = False
        for particle in gen_particles:
            pdg = particle.core.pdgId
            if abs(pdg) == 15:
                deltaR = vector.DeltaR(utils.get_lorentz_vector(particle))
                if deltaR < 0.05:
                    selection = True
                    break

        efficiency_histo.Fill(selection, pt)
        fake_histo.Fill(not selection, pt)

        # if not selection:
        #     fake_histo.Fill(pt)


def efficiency_plot(tree, plot):
    jets = tree.jets
    tau_tags = tree.tauTags
    gen_particles = tree.skimmedGenParticles

    for particle in gen_particles:

        pdg = particle.core.pdgId

        if abs(pdg) != 15:
            continue

        gen_vector = utils.get_lorentz_vector(particle)

        found_match = False

        for i in range(len(jets)):

            if tau_tags[i].tag < 0.5:
                continue

            rec_vector = utils.get_lorentz_vector(jets[i])
            deltaR = gen_vector.DeltaR(rec_vector)

            if deltaR < 0.05:
                found_match = True
                print(particle.core.status)
                break

        pt = utils.get_pt(gen_vector)
        plot.Fill(found_match, pt)


# files
inf = TFile('data/p8_ee_ZH.root')
outf = TFile('data/rec_efficiency.root', 'RECREATE')

# all_histo = TH1D('all events', 'all events', 8, 0, 120)
# efficiency_histo = TH1D('efficiency', 'efficiency', 8, 0, 120)
# fake_histo = TH1D('fake rate', 'fake rate', 8, 0, 120)

efficiency_histo = TEfficiency('efficiency', 'efficiency', 8, 0, 120)
fake_histo = TEfficiency('efficiency', 'efficiency', 8, 0, 120)

# read events
tree = inf.Get('events')
n_tot = tree.GetEntries()

print('Number of events: ', n_tot)

gen_stable = 0
gen_total = 0

rec_total = 0
rec_matching = 0
rec_fake = 0

for event in range(n_tot):

    tree.GetEntry(event)

    print('Event ', event + 1)

    jets = tree.jets
    tau_tags = tree.tauTags
    gen_particles = tree.skimmedGenParticles

    for i in range(len(jets)):

        if tau_tags[i].tag < 0.5:
            continue

        rec_total += 1

        vector = utils.get_lorentz_vector(jets[i])

        for particle in gen_particles:
            pdg = particle.core.pdgId
            status = particle.core.status
            found_match = False

            if abs(pdg) == 15:
                deltaR = vector.DeltaR(utils.get_lorentz_vector(particle))
                if deltaR < 0.05:
                    found_match = True
                    rec_matching += 1
                    break

        if not found_match:
            rec_fake += 1

    for particle in gen_particles:

        pdg = particle.core.pdgId
        if abs(pdg) != 15:
            continue

        print(particle.core.status, end=' ')
        gen_total += 1

        status = particle.core.status
        if status == 2:
            gen_stable += 1

    print()

    fill_histograms(tree, efficiency_histo, fake_histo)
    # efficiency_histo.Divide(all_histo)
    # fake_histo.Divide(all_histo)
    # efficiency_plot(tree, efficiency_histo)

outf.Write()
print('Number of total generator taus: ', gen_total)
print('Number of stable generator taus: ', gen_stable)
print('Number of reconstructed taus:', rec_total)
print('Number of matching taus: ', rec_matching)
print('Number of fake taus: ', rec_fake)