# Comparison of tau tagged jets to MC taus

from ROOT import TFile, TH1D
import utils

# files
inf = TFile('data/p8_ee_ZH.root')
outf = TFile('data/histo_deltaR.root', 'RECREATE')

# histogram settings
histogram = TH1D('deltaR', 'deltaR', 100, 0, 1)

# read events
tree = inf.Get('events')
ntot = tree.GetEntries()
for event in range(ntot):
    tree.GetEntry(event)

    # get tau tagged jets
    tau_jets = []
    jets = tree.jets
    tags = tree.tauTags
    n_jets = len(jets)
    for i in range(n_jets):
        if tags[i].tag > 0:
            tau_jets.append(jets[i])

    # get MC taus
    mc_taus = []
    mc_particles = tree.skimmedGenParticles
    for particle in mc_particles:
        pdg = particle.core.pdgId
        if abs(pdg) == 15:
            mc_taus.append(particle)

    # compare tau tagged jets to MC taus
    for tau_jet in tau_jets:
        jet_vector = utils.get_lorentz_vector(tau_jet)
        for mc_tau in mc_taus:
            mc_vector = utils.get_lorentz_vector(mc_tau)
            histogram.Fill(jet_vector.DeltaR(mc_vector))

# write to file
outf.Write()