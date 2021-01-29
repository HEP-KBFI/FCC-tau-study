# Plotting the efficiency and fake rate of tau reconstruction

from ROOT import TFile, TEfficiency, TH1D
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
        self.taus = []  # List of taus
        # Create data objects for storing information about tau jets
        for i in range(self.count):
            self.taus.append(TauJet())
        # Find taus
        self.__get_gen_taus()
        self.__get_rec_taus()

    def __get_gen_taus(self):
        # Sort through generator level tau and calculate tau jets
        particles = tree.skimmedGenParticles
        neutrinos = []
        for particle in particles:
            id = particle.core.pdgId
            # Find neutrinos
            if abs(id) == 16:
                neutrinos.append(particle)
                continue
            elif abs(id) != 15:
                continue
            # Save final state taus
            if particle.core.status == 2:
                self.__add_tau(particle)
        # Add neutrinos to corresponding taus
        for neutrino in neutrinos:
            self.__add_neutrino(neutrino)

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
            if not obj.gen_tau and not obj.rec_taujet:
                obj.create_gen_tau(tau)
                break

    def __add_neutrino(self, neutrino):
        # Add corresponding neutrinos to generator level tau particles
        for obj in self.taus:
            if not obj.gen_neutrino:
                if obj.match_neutrino(neutrino):
                    break

    def __add_reconstruction(self, jet):
        # Match a reconstruction to a generator level tau
        for obj in self.taus:
            if not obj.rec_taujet and obj.gen_tau:
                if obj.match_reconstruction(jet):
                    return
        fake = TauJet()
        fake.create_rec_tau(jet)
        self.taus.append(fake)

    def get_gen_taus(self):
        # Return a list of all generated taus
        gen_taus = []
        for obj in self.taus:
            if obj.gen_tau:
                gen_taus.append(obj)
        return gen_taus

    def get_rec_taus(self):
        # Return a list of all reconstructed tau jets
        rec_taus = []
        for obj in self.taus:
            if obj.rec_taujet:
                rec_taus.append(obj)
        return rec_taus

    def count_gens(self):
        # Return number of generated taus
        count = 0
        for tau in self.taus:
            if tau.gen_tau:
                count += 1
        return count

    def count_recs(self):
        # Return number of reconstructed tau jets
        count = 0
        for tau in self.taus:
            if tau.rec_taujet:
                count += 1
        return count

    def count_correct_tag(self):
        # Return number of correctly tagged tau jets
        count = 0
        for tau in self.taus:
            if tau.check_reconstructed():
                count += 1
        return count


class TauJet:
    def __init__(self):
        # Generator level information
        self.gen_tau = None
        self.gen_neutrino = None
        self.gen_vector = None
        # self.previous_states = []
        # Reconstruction information
        self.rec_taujet = None
        self.rec_vector = None

    def create_gen_tau(self, tau):
        # Create a generator level tau
        self.gen_tau = tau
        self.gen_vector = utils.get_lorentz_vector(tau)

    def match_neutrino(self, neutrino):
        # Match a tau neutrino to a generator level tau particle
        if self.gen_tau.core.pdgId * neutrino.core.pdgId > 0:
            self.gen_neutrino = neutrino
            self.gen_vector = utils.get_lorentz_vector(self.gen_tau) - utils.get_lorentz_vector(neutrino)
            return True
        return False

    def create_rec_tau(self, taujet):
        # Create a reconstructed tau jet
        self.rec_taujet = taujet
        self.rec_vector = utils.get_lorentz_vector(taujet)

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
        # Check whether a tau has been correctly reconstructed
        if self.rec_taujet and self.gen_tau:
            return True
        return False

    def check_fake(self):
        # Check whether a tau is fake
        if self.rec_taujet and not self.gen_tau:
            return True
        return False

    def pt(self):
        # Return the pT of the tau
        if self.rec_taujet:
            return utils.get_pt(self.rec_vector)
        return utils.get_pt(self.gen_vector)

    def visible_pt(self):
        # Return the visible pT of a generator tau
        if not self.gen_tau:
            return None
        vector = utils.get_lorentz_vector(self.gen_tau)
        return utils.get_pt(vector)

    def eta(self):
        # Return the eta of the tau
        if self.gen_vector:
            return self.gen_vector.Eta()
        return self.rec_vector.Eta()


def fill_histograms(taus, efficiency_pt, fakerate_pt):
    # Fill efficiency histogram
    gen_taus = taus.get_gen_taus()
    for tau in gen_taus:
        value = tau.check_reconstructed()
        efficiency_pt.Fill(value, tau.visible_pt())

    # Fill fake rate histogram
    rec_taus = taus.get_rec_taus()
    for tau in rec_taus:
        fakerate_pt.Fill(tau.check_fake(), tau.pt())


# Files
inf = TFile('data/delphes_output.root')
outf = TFile('data/rec_efficiency.root', 'RECREATE')

# Create histograms
efficiency_pt = TEfficiency('efficiency', 'efficiency (pT)', 13, 0, 130)
fakerate_pt = TEfficiency('fake rate', 'fake rate (pT)', 13, 0, 130)

n_tag = 0  # Count of correctly tagged true taus
n_gen = 0  # Count of true taus
n_rec = 0  # Count of reconstructed tau jets
n_fake = 0  # Count of fake tau jets

# Read events
tree = inf.Get('events')
n_tot = tree.GetEntries()
for event in range(n_tot):
    tree.GetEntry(event)
    taus = EventTauFinder(tree)

    # Count taus
    curr_recs = taus.count_recs()
    curr_correct = taus.count_correct_tag()
    n_gen += taus.count_gens()
    n_rec += curr_recs
    n_tag += curr_correct
    n_fake += curr_recs - curr_correct

    fill_histograms(taus, efficiency_pt, fakerate_pt)

# Print out results
print("Generated taus: ", n_gen)
print("Reconstructed tau jets: ", n_rec)
print("Correctly tagged taus: ", n_tag)
print("Efficiency over entire dataset: ", n_tag / n_gen)
print("Fake rate over entire dataset: ", n_fake / n_rec)

# Write histograms to file
outf.Write()
