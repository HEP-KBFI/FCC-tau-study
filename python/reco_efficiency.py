# Plotting the efficiency and fake rate of tau reconstruction

from ROOT import TFile, TEfficiency, TH1D
import jetmatcher as jm


def fill_histograms(taus, efficiency_pt, fakerate_pt):
    # Fill efficiency histogram
    gen_taus = taus.get_gen_taus()
    for tau in gen_taus:
        value = tau.check_reco()
        efficiency_pt.Fill(value, tau.visible_pt())

    # Fill fake rate histogram
    reco_taus = taus.get_reco_jets()
    for tau in reco_taus:
        fakerate_pt.Fill(tau.check_fake(), tau.pt())


# Files
inf = TFile('data/delphes_output.root')
outf = TFile('data/rec_efficiency.root', 'RECREATE')

# Create histograms
efficiency_pt = TEfficiency('efficiency', 'efficiency (pT)', 13, 0, 130)
fakerate_pt = TEfficiency('fake rate', 'fake rate (pT)', 13, 0, 130)

n_tag = 0  # Count of correctly tagged true taus
n_gen = 0  # Count of true taus
n_reco = 0  # Count of reconstructed tau jets
n_fake = 0  # Count of fake tau jets

# Read events
tree = inf.Get('events')
n_tot = tree.GetEntries()
for event in range(n_tot):
    tree.GetEntry(event)
    taus = jm.JetMatcher(tree)

    # Count taus
    curr_recs = taus.count_recos()
    curr_correct = taus.count_correct_tag()
    n_gen += taus.count_gens()
    n_reco += curr_recs
    n_tag += curr_correct
    n_fake += curr_recs - curr_correct

    fill_histograms(taus, efficiency_pt, fakerate_pt)

# Print out results
print("Generated taus: ", n_gen)
print("Reconstructed tau jets: ", n_reco)
print("Correctly tagged taus: ", n_tag)
print("Efficiency over entire dataset: ", n_tag / n_gen)
print("Fake rate over entire dataset: ", n_fake / n_reco)

# Write histograms to file
outf.Write()
