# Plotting the efficiency and fake rate of tau reconstruction

from ROOT import TFile, TEfficiency
import utils


class Tau:
    # Data object to save data about a tau particle
    def __init__(self, data):
        self.data = data
        self.vector = utils.get_lorentz_vector(self.data)

    def pt(self):
        # Shorthand function for getting the transverse momentum
        return utils.get_pt(self.vector)

class GeneratorTau(Tau):
    # Data object to associate generator level final taus with corresponding previous state
    def __init__(self, data):
        super().__init__(data)
        self.other_states = []
        self.matching_reconstruction = None

    def add_state(self, candidate):
        # Check if candidate tau is a previous state of the given generator tau and add it 
        candidate_state = GeneratorTau(candidate)
        deltaR = self.vector.DeltaR(candidate_state.vector)
        if deltaR < 0.05:
            self.other_states.append(candidate_state)
            return True
        return False


class ReconstructedTau(Tau):
    # Data object to associate reconstructed tau jet to corresponding generator tau
    def __init__(self, data):
        super().__init__(data)
        self.generator_tau = None

    def add_generator_tau(self, candidate):
        # Check if corresponding generator tau already exists
        if self.generator_tau:
            return False
        # Check if candidate generator tau corresponds
        deltaR = self.vector.DeltaR(candidate.vector)
        if deltaR < 0.05:
            self.generator_tau = candidate
            candidate.matching_reconstruction = self
            return True
        return False

    def check_fake(self):
        # Return true if no matching generator tau
        if not self.generator_tau:
            return True
        return False


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


def get_rec_taus(tree):
    # Get reconstructed tau jets
    jets = tree.jets
    tau_tags = tree.tauTags
    rec_taus = []
    for i in range(len(jets)):
        if tau_tags[i].tag < 0.5:
            continue
        rec_taus.append(ReconstructedTau(jets[i]))
    return rec_taus


def match_taus(gen_tau, rec_taus):
    # Try to match a generator tau to a tau tagged reconstructed jet
    for rec_tau in rec_taus:
        if rec_tau.add_generator_tau(gen_tau):
            return True
    return False


def fill_histograms(tree, efficiency_histo, fake_histo):
    gen_taus = get_gen_taus(tree)
    rec_taus = get_rec_taus(tree)

    for tau in gen_taus:

        # Try to match a final state  of a generated tau to a reconstructed jet
        match = match_taus(tau, rec_taus)

        if not match:
        # Try to match any previous state of a generated tau to a reconstructed jet
            for previous_state in tau.other_states:
                match = match_taus(previous_state, rec_taus)
                if match:
                    break

        # Fill efficiency histogram
        efficiency_histo.Fill(match, tau.pt())

    # Fill fake rate histogram
    for tau in rec_taus:
        fake_histo.Fill(tau.check_fake(), tau.pt())


# Files
inf = TFile('data/p8_ee_ZH.root')
outf = TFile('data/rec_efficiency.root', 'RECREATE')

# Create histograms
efficiency_histo = TEfficiency('efficiency', 'efficiency', 8, 0, 120)
fake_histo = TEfficiency('fake rate', 'fake rate', 8, 0, 120)

# Read events
tree = inf.Get('events')
n_tot = tree.GetEntries()
for event in range(n_tot):
    tree.GetEntry(event)
    fill_histograms(tree, efficiency_histo, fake_histo)

# Write histograms to file
outf.Write()
