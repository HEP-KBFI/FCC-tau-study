# Plotting the efficiency and fake rate of tau reconstruction

from ROOT import TFile, TEfficiency
import utils


class GeneratorTau:
    # Data object to associate generator level final taus with corresponding previous state
    def __init__(self, data):
        self.data = data
        self.vector = utils.get_lorentz_vector(self.data)
        self.other_states = []

    def add_state(self, candidate):
        # Check if candidate tau is a previous state of the given generator tau and add it 
        candidate_state = GeneratorTau(candidate)
        deltaR = self.vector.DeltaR(candidate_state.vector)
        if deltaR < 0.05:
            self.other_states.append(candidate_state)
            return True
        return False

    def pt(self):
        return utils.get_pt(self.vector)


def get_gen_taus(tree):
    # Get generator level taus as final taus with corresponding previous states
    gen_particles = tree.skimmedGenParticles
    final_taus = []
    previous_states = []

    # Find generator level taus
    for particle in gen_particles:
        if abs(particle.core.pdgId) != 15:
            continue
        if particle.core.status == 2:
            final_taus.append(GeneratorTau(particle))
        else:
            previous_states.append(particle)

    # Match previous states to final taus
    for tau in previous_states:
        for final_tau in final_taus:
            if final_tau.add_state(tau):
                continue

    return final_taus



def find_gen_match(tree):

    gen_particles = tree.skimmedGenParticles

    # final_taus = []
    # other_taus = []
    taus = []

    for particle in gen_particles:
        pdg = particle.core.pdgId
        status = particle.core.status

        if abs(pdg) != 15:
            continue

        taus.append(particle)

        # if status == 2:
        #     final_taus.append(particle)
        # else:
        #     other_taus.append(particle)

    # rec_vector = utils.get_lorentz_vector(jet)

    # for i in range(len(taus) - 1):
    #     print(taus[i].core.status)
    #     ivector = utils.get_lorentz_vector(taus[i])
    #     for j in range(i + 1, len(taus)):
    #         jvector = utils.get_lorentz_vector(taus[j])
    #         deltaR = ivector.DeltaR(jvector)
    #         print(taus[j].core.status, end=':')
    #         print(deltaR, end=' ')
    #     print()


    # for tau in final_tau:
    #     gen_vector = utils.get_lorentz_vector(tau)
    #     deltaR = rec_vector.DeltaR(gen_vector)
    #     if deltaR < 0.05:
    #         return True

    # for tau in other_taus:
    #     gen_vector = utils.get_lorentz_vector(tau)
    #     deltaR = rec_vector.DeltaR(gen_vector)
    #     if deltaR < 0.05:
    #         return True

    # return False



def match_gen_tau_to_tau_jet(gen_tau, jets, tau_tags):
    # Try to match a generator tau to a tau tagged reconstructed jet
    for i in range(len(jets)):
        # Check if jet is a tau
        if tau_tags[i].tag < 0.5:
            continue
        # Compare delta R of reconstruced jet w.r.t generator tau
        rec_vector = utils.get_lorentz_vector(jets[i])
        deltaR = rec_vector.DeltaR(gen_tau.vector)
        if deltaR < 0.05:
            return jets[i]
    return None



def fill_histos(tree, efficiency_histo):
    jets = tree.jets
    tau_tags = tree.tauTags
    gen_taus = get_gen_taus(tree)

    # Find efficiency
    for tau in gen_taus:

        # Try to match a final state  of a generated tau to a reconstructed jet
        match = match_gen_tau_to_tau_jet(tau, jets, tau_tags)

        if not match:
        # Try to match any previous state of a generated tau to a reconstruced jet
            for previous_state in tau.other_states:
                match = match_gen_tau_to_tau_jet(previous_state, jets, tau_tags)
                if match:
                    break

        # Fill efficiency histogram
        pt = tau.pt()
        if match:
            efficiency_histo.Fill(True, pt)
        else:
            efficiency_histo.Fill(False, pt)



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
# fake_histo = TEfficiency('efficiency', 'efficiency', 8, 0, 120)

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

    # print('Event ', event + 1)

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

        # print(particle.core.status, end=' ')
        gen_total += 1

        status = particle.core.status
        if status == 2:
            gen_stable += 1

    # print()

    fill_histos(tree, efficiency_histo)

    # fill_histograms(tree, efficiency_histo, fake_histo)
    # efficiency_histo.Divide(all_histo)
    # fake_histo.Divide(all_histo)
    # efficiency_plot(tree, efficiency_histo)

outf.Write()
print('Number of total generator taus: ', gen_total)
print('Number of stable generator taus: ', gen_stable)
print('Number of reconstructed taus:', rec_total)
print('Number of matching taus: ', rec_matching)
print('Number of fake taus: ', rec_fake)