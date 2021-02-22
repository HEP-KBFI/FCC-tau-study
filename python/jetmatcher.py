# Module for finding and filtering reconstructed jets
# and matching them to generator tau particles
import utils


class JetMatcher:
    def __init__(self, tree, jetfilter='tautagged'):
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
            self.taus.append(Jet())
        # Find taus
        self.__get_gen_taus()
        if jetfilter == 'tautagged':
            self.__get_reco_taus()
        elif jetfilter == 'all':
            self.__get_reco_jets()
        else:
            print("Invalid jet filter")

    def __get_gen_taus(self):
        # Sort through generator level tau and calculate tau jets
        particles = self.tree.skimmedGenParticles
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

    def __get_reco_taus(self):
        # Sort through reconstructed tau jets
        jets = self.tree.jets
        tags = self.tree.tauTags
        for i in range(len(jets)):
            if tags[i].tag < 0.5:
                continue
            self.__add_reco(jets[i])

    def __get_reco_jets(self):
        # Add all reconstructed jets
        jets = self.tree.jets
        for jet in jets:
            self.__add_reco(jet)

    def __add_tau(self, tau):
        # Save generator level tau particle
        for obj in self.taus:
            if not obj.gen_tau and not obj.reco_jet:
                obj.create_gen_tau(tau)
                break

    def __add_neutrino(self, neutrino):
        # Add corresponding neutrinos to generator level tau particles
        for obj in self.taus:
            if not obj.gen_neutrino:
                if obj.match_neutrino(neutrino):
                    break

    def __add_reco(self, jet):
        # Match a reconstruction to a generator level tau
        for obj in self.taus:
            if not obj.reco_jet and obj.gen_tau:
                if obj.match_reco(jet):
                    return
        fake = Jet()
        fake.create_reco_jet(jet)
        self.taus.append(fake)

    def get_gen_taus(self):
        # Return a list of all generated taus
        gen_taus = []
        for obj in self.taus:
            if obj.gen_tau:
                gen_taus.append(obj)
        return gen_taus

    def get_reco_taus(self):
        # Return a list of all reconstructed tau jets
        rec_taus = []
        for obj in self.taus:
            if obj.reco_jet:
                rec_taus.append(obj)
        return rec_taus

    def count_gens(self):
        # Return number of generated taus
        count = 0
        for tau in self.taus:
            if tau.gen_tau:
                count += 1
        return count

    def count_recos(self):
        # Return number of reconstructed tau jets
        count = 0
        for tau in self.taus:
            if tau.reco_jet:
                count += 1
        return count

    def count_correct_tag(self):
        # Return number of correctly tagged tau jets
        count = 0
        for tau in self.taus:
            if tau.check_reco():
                count += 1
        return count


class Jet:
    def __init__(self):
        # Generator level information
        self.gen_tau = None
        self.gen_neutrino = None
        self.gen_vector = None
        # self.previous_states = []
        # Reconstruction information
        self.reco_jet = None
        self.reco_vector = None

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

    def create_reco_jet(self, taujet):
        # Create a reconstructed tau jet
        self.reco_jet = taujet
        self.reco_vector = utils.get_lorentz_vector(taujet)

    def match_reco(self, jet):
        # Match a reconstructed tau jet to a generator level tau
        if self.reco_jet:
            return False
        vector = utils.get_lorentz_vector(jet)
        deltaR = self.gen_vector.DeltaR(vector)
        if deltaR < 0.05:
            self.reco_jet = jet
            self.reco_vector = vector
            return True
        return False

    def check_reco(self):
        # Check whether a tau has been correctly reconstructed
        if self.reco_jet and self.gen_tau:
            return True
        return False

    def check_fake(self):
        # Check whether a tau is fake
        if self.reco_jet and not self.gen_tau:
            return True
        return False

    def pt(self):
        # Return the pT of the tau
        if self.reco_jet:
            return utils.get_pt(self.reco_vector)
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
        return self.reco_vector.Eta()
