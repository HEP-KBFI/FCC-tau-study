# Plotting the efficiency and fake rate of tau reconstruction

from ROOT import TFile, TEfficiency
import utils


class TauSet:
    def __init__(self, tree):
        # Initialize
        self.tree = tree
        self.count = 0
        for particle in tree.skimmedGenParticles:
            if abs(particle.core.pdgId) == 15 and particle.core.status == 2:
                self.count += 1
        self.taus = []
        for i in range(self.count):
            self.taus.append(TauJet())
        # Find taus
        self.__get_gen_taus()
        self.__get_rec_taus()

    def __len__(self):
        return self.count

    def __getitem__(self, item):
        return self.taus[item]

    def __get_gen_taus(self):
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
        jets = self.tree.jets
        tags = self.tree.tauTags
        for i in range(len(jets)):
            if tags[i].tag < 0.5:
                continue
            self.__add_reconstruction(jets[i])

    def __add_tau(self, tau):
        for obj in self.taus:
            if not obj.gen_tau:
                obj.gen_tau = tau
                break

    def __add_neutrino(self, neutrino):
        for obj in self.taus:
            # print("Checking tau with ID ", obj.gen_tau.core.pdgId)
            if not obj.gen_neutrino:
                # print("Neutrino not found, attempting to match...")
                if obj.match_neutrino(neutrino):
                    break

    def __add_states(self, state):
        for obj in self.taus:
            if obj.match_previous_states(state):
                break

    def __add_reconstruction(self, jet):
        for obj in self.taus:
            if not obj.rec_taujet:
                if obj.match_reconstruction(jet):
                    break

    def num_rec_taus(self):
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
        self.previous_states = []
        # Reconstruction information
        self.rec_taujet = None
        self.rec_vector = None

    def match_neutrino(self, neutrino):
        if self.gen_tau.core.pdgId * neutrino.core.pdgId > 0:
            self.gen_neutrino = neutrino
            self.gen_vector = utils.get_lorentz_vector(self.gen_tau) - utils.get_lorentz_vector(neutrino)
            return True
        return False

    def match_previous_states(self, state):
        if self.gen_tau.core.charge != state.core.charge:
            return False
        deltaR = self.gen_vector.DeltaR(utils.get_lorentz_vector(state))
        if deltaR < 0.05:
            self.previous_states.append(state)
            return True
        return False

    def match_reconstruction(self, jet):
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
        if self.rec_taujet:
            return True
        return False


# class Tau:
#     # Data object to save data about a tau particle
#     def __init__(self, tau):
#         self.tau = tau
#
#     def pt(self):
#         # Shorthand function for getting the transverse momentum
#         return utils.get_pt(self.vector)


# class GeneratorTauJet(Tau):
#     # Data object to save information about a generator level tau jet and associate it with its other states
#     def __init__(self, tau, neutrino):
#         # Tau jet
#         super().__init__(tau)
#         self.neutrino = neutrino
#         self.vector = utils.get_lorentz_vector(self.tau) - utils.get_lorentz_vector(self.neutrino)
#         # Associations
#         self.final_state = None
#         self.previous_states = []
#         self.reconstruction = None
#
#     def add_state(self, candidate):
#         # Check if candidate tau is a previous state of the given generator tau and add it
#         candidate = GeneratorTau(candidate)
#         if self.get_charge() != candidate.get_charge():
#             return False
#         deltaR = self.vector.DeltaR(candidate.vector)
#         if deltaR < 0.05:
#             candidate.final_state = self
#             self.previous_states.append(candidate)
#             return True
#         return False
#
#     def get_charge(self):
#         # Return the charge of the tau
#         return self.tau.core.charge
#
#     def check_reconstruction(self):
#         # Check if the tau has a matching reconstruction
#         if self.reconstruction:
#             return True
#         return False
#
#
# class ReconstructedTau(Tau):
#     # Data object to associate reconstructed tau jet to corresponding generator tau
#     def __init__(self, data):
#         # Tau jet
#         super().__init__(data)
#         self.vector = utils.get_lorentz_vector(self.tau)
#         # Associations
#         self.generator_match = None
#
#     def add_generator_match(self, candidate):
#         # Check if corresponding generator tau already exists
#         if self.generator_match:
#             return False
#         # Check if candidate generator tau corresponds
#         deltaR = self.vector.DeltaR(candidate.vector)
#         if deltaR < 0.05:
#             self.generator_match = candidate
#             if candidate.final_state:
#                 candidate.final_state.reconstruction = self
#             else:
#                 candidate.reconstruction = self
#             return True
#         return False
#
#     def check_fake(self):
#         # Return true if no matching generator tau jet
#         if not self.generator_match:
#             return True
#         return False


# def get_gen_taus(tree):
#     # Get generator level taus as final taus with corresponding previous states
#     gen_particles = tree.skimmedGenParticles
#     tau_jets = []
#     final_taus = []
#     previous_states = []
#     neutrinos = []
#
#     # Find generator level taus and tau neutrinos
#     for particle in gen_particles:
#         if abs(particle.core.pdgId) == 16:
#             neutrinos.append(particle)
#             continue
#
#         elif abs(particle.core.pdgId) != 15:
#             continue
#
#         if particle.core.status == 2:
#             final_taus.append(particle)
#         else:
#             previous_states.append(particle)
#
#     # Match neutrinos to taus and create objects
#     for tau in final_taus:
#         matched = False
#         for neutrino in neutrinos:
#             if matched:
#                 break
#             if tau.core.charge == neutrino.core.charge:
#                 tau_jets.append(GeneratorTauJet(tau, neutrino))
#                 matched = True
#
#     # Match previous states to final taus
#     for tau in previous_states:
#         for jet in tau_jets:
#             if jet.add_state(tau):
#                 continue
#
#     return tau_jets

#
# def get_rec_taus(tree):
#     # Get reconstructed tau jets
#     jets = tree.jets
#     tau_tags = tree.tauTags
#     rec_taus = []
#     for i in range(len(jets)):
#         if tau_tags[i].tag < 0.5:
#             continue
#         rec_taus.append(ReconstructedTau(jets[i]))
#     return rec_taus


# def match_taus(gen_taus, rec_taus):
#     for tau in gen_taus:
#         match = False
#         for rec_tau in rec_taus:
#             match = rec_tau.add_generator_match(tau)
#             break
#         if not match:
#             for previous_state in tau.previous_states:
#                 if match:
#                     break
#                 for rec_tau in rec_taus:
#                     if rec_tau.add_generator_match(previous_state):
#                         break
#
#         # Try to match a generator tau to a tau tagged reconstructed jet
#         for rec_tau in rec_taus:
#             if rec_tau.add_generator_match(tau):
#                 return True
#     # # Try to match any previous state of a generated tau to a reconstructed jet
#     # for previous_state in gen_tau.previous_states:
#     #     for rec_tau in rec_taus:
#     #         if rec_tau.add_generator_tau(previous_state):
#     #             return True
#     return False


def fill_histograms(taus, efficiency_histo):
    # gen_taus = get_gen_taus(tree)
    # rec_taus = get_rec_taus(tree)
    #
    # for tau in gen_taus:
    #     # Try to match a final state  of a generated tau to a reconstructed jet
    #     match = match_taus(tau, rec_taus)
    #
    #     if not match:
    #     # Try to match any previous state of a generated tau to a reconstructed jet
    #         for previous_state in tau.previous_states:
    #             match = match_taus(previous_state, rec_taus)
    #             if match:
    #                 break

    # Fill efficiency histogram
    for i in range(len(taus)):
        efficiency_histo.Fill(taus[i].check_reconstructed(), taus[i].pt())
    #
    # # Fill fake rate histogram
    # for tau in rec_taus:
    #     fake_histo.Fill(tau.check_fake(), tau.pt())


# Files
inf = TFile('data/delphes_output.root')
outf = TFile('data/rec_efficiency.root', 'RECREATE')

# Create histograms
# efficiency_histo = TEfficiency('efficiency', 'efficiency', 8, 0, 120)
# fake_histo = TEfficiency('fake rate', 'fake rate', 8, 0, 120)

n_tag = 0
n_true = 0

# Read events
tree = inf.Get('events')
n_tot = tree.GetEntries()
for event in range(n_tot):
    tree.GetEntry(event)
    # gen_taus = get_gen_taus(tree)
    # rec_taus = get_rec_taus(tree)
    #
    # match_taus(gen_taus, rec_taus)
    #
    # for tau in gen_taus:
    #     n_true += 1
    #     if tau.matching_reconstruction:
    #         n_tag += 1

    taus = TauSet(tree)

    n_true += len(taus)
    n_tag += taus.num_rec_taus()

    # fill_histograms(taus, efficiency_histo)

# Write histograms to file
print("Generated taus: ", n_true)
print("Correctly tagged taus: ", n_tag)
# print("Efficiency over entire dataset: ", n_tag / n_true)
# outf.Write()
