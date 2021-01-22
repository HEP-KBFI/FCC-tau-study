# Plotting the efficiency and fake rate of tau reconstruction

from ROOT import TFile, TEfficiency
import utils


class EventTauFinder:
    def __init__(self, tree):
        # Initialize
        self.tree = tree
        self.count = 0
        # Count generator level taus
        for particle in tree.skimmedGenParticles:
            if abs(particle.core.pdgId) == 15 and particle.core.status == 2:
                self.count += 1
        self.taus = []  # List of true taus
        self.fakes = []  # List of fake taus
        # Create data objects for storing information about tau jets
        for i in range(self.count):
            self.taus.append(TauJet())
        # Find taus
        self.__get_gen_taus()
        self.__get_rec_taus()

    def __len__(self):
        # Return number of taus
        return self.count

    def __getitem__(self, item):
        # Return one tau with given index
        return self.taus[item]

    def __get_gen_taus(self):
        # Sort through generator level tau and calculate tau jets
        particles = tree.skimmedGenParticles
        neutrinos = []
        previous_states = []
        for particle in particles:
            id = particle.core.pdgId
            # Find neutrinos
            if abs(id) == 16:
                neutrinos.append(particle)
                continue
            elif abs(id) != 15:
                continue
            # Find taus
            if particle.core.status == 2:
                self.__add_tau(particle)
            else:
                previous_states.append(particle)
        # Add neutrinos to corresponding taus
        for neutrino in neutrinos:
            self.__add_neutrino(neutrino)
        # Add previous states to corresponding taus
        for state in previous_states:
            self.__add_states(state)

    def __get_rec_taus(self):
        # Sort through reconstructed tau jets
        jets = self.tree.jets
        tags = self.tree.tauTags
        for i in range(len(jets)):
            if tags[i].tag < 0.5:
                continue
            self.__add_reconstruction(jets[i])

    def __add_tau(self, tau):
        # Save generator level tau particle
        for obj in self.taus:
            if not obj.gen_tau:
                obj.gen_tau = tau
                break

    def __add_neutrino(self, neutrino):
        # Add corresponding neutrinos to generator level tau particles
        for obj in self.taus:
            if not obj.gen_neutrino:
                if obj.match_neutrino(neutrino):
                    break

    def __add_states(self, state):
        # Save information about generator level tau particle's previous states
        for obj in self.taus:
            if obj.match_previous_states(state):
                break

    def __add_reconstruction(self, jet):
        # Match a reconstruction to a generator level tau
        for obj in self.taus:
            if not obj.rec_taujet:
                if obj.match_reconstruction(jet):
                    return
        self.fakes.append(jet)

    def count_recs(self):
        # Return number of correctly reconstructed tau jets
        count = 0
        for tau in self.taus:
            if tau.check_reconstructed():
                count += 1
        return count

    def count_fakes(self):
        # Return number of fake taus
        return len(self.fakes)


class TauJet:
    def __init__(self):
        # Generator level information
        self.gen_tau = None
        self.gen_neutrino = None
        self.gen_vector = None
        self.previous_states = []
        # Reconstruction information
        self.rec_taujet = None
        self.rec_vector = None

    def match_neutrino(self, neutrino):
        # Match a tau neutrino to a generator level tau particle
        if self.gen_tau.core.pdgId * neutrino.core.pdgId > 0:
            self.gen_neutrino = neutrino
            self.gen_vector = utils.get_lorentz_vector(self.gen_tau) - utils.get_lorentz_vector(neutrino)
            return True
        return False

    def match_previous_states(self, state):
        # Match generator level information about previous states to a tau particle
        if self.gen_tau.core.charge != state.core.charge:
            return False
        deltaR = self.gen_vector.DeltaR(utils.get_lorentz_vector(state))
        if deltaR < 0.05:
            self.previous_states.append(state)
            return True
        return False

    def match_reconstruction(self, jet):
        # Match a reconstructed tau jet to a generator level tau
        if self.rec_taujet:
            return False
        vector = utils.get_lorentz_vector(jet)
        deltaR = self.gen_vector.DeltaR(vector)
        if deltaR < 0.05:
            self.rec_taujet = jet
            self.rec_vector = vector
            return True
        return False

    def check_reconstructed(self):
        # Check whether a tau has a reconstruction
        if self.rec_taujet:
            return True
        return False

    def pt(self):
        # Return the pT of the tau
        return utils.get_pt(self.gen_vector)


def fill_histograms(taus, efficiency_histo):
    # Fill histograms
    for i in range(len(taus)):
        # Fill efficiency histogram
        efficiency_histo.Fill(taus[i].check_reconstructed(), taus[i].pt())

    # # Fill fake rate histogram
    # for tau in rec_taus:
    #     fake_histo.Fill(tau.check_fake(), tau.pt())


# Files
inf = TFile('data/delphes_output.root')
outf = TFile('data/rec_efficiency.root', 'RECREATE')

# Create histograms
efficiency_histo = TEfficiency('efficiency', 'efficiency', 10, 0, 90)
# fake_histo = TEfficiency('fake rate', 'fake rate', 8, 0, 120)

n_tag = 0  # Count of correctly tagged true taus
n_true = 0  # Count of true taus

# Read events
tree = inf.Get('events')
n_tot = tree.GetEntries()
for event in range(n_tot):
    tree.GetEntry(event)
    taus = EventTauFinder(tree)

    # Count taus
    n_true += len(taus)
    n_tag += taus.count_recs()

    fill_histograms(taus, efficiency_histo)

# Write histograms to file
print("Generated taus: ", n_true)
print("Correctly tagged taus: ", n_tag)
print("Efficiency over entire dataset: ", n_tag / n_true)

outf.Write()
