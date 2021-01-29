# Run Pythia simulation and save all results
# Based on k4Gen/k4Gen/options/pythia.py
from Gaudi.Configuration import *

# Workflow Steering
from Configurables import ApplicationMgr
ApplicationMgr().EvtSel = 'NONE'
ApplicationMgr().EvtMax = 100
ApplicationMgr().OutputLevel = INFO

# Data service
from Configurables import k4DataSvc
podioEvent = k4DataSvc("EventDataSvc")
ApplicationMgr().ExtSvc += [podioEvent]

# Pythia generator
from Configurables import PythiaInterface
pythia8gentool = PythiaInterface()
pythia8gentool.Filename = "cards/Pythia_ee_ZH_Htautau.cmd" # default card

# Write the HepMC::GenEvent to the data service
from Configurables import GenAlg
pythia8gen = GenAlg("Pythia8")
pythia8gen.SignalProvider = pythia8gentool
pythia8gen.hepmc.Path = "hepmc"
ApplicationMgr().TopAlg += [pythia8gen]

# Reads an HepMC::GenEvent from the data service and writes a collection of EDM Particles
from Configurables import HepMCToEDMConverter
hepmc_converter = HepMCToEDMConverter("Converter")
hepmc_converter.hepmc.Path = "hepmc"
hepmc_converter.hepmcStatusList = []  # convert particles with all statuses
hepmc_converter.GenParticles.Path = "genParticles"
# hepmc_converter.GenVertices.Path = "genVertices"
ApplicationMgr().TopAlg += [hepmc_converter]

# FCC event-data model output -> define objects to be written out
from Configurables import PodioOutput
out = PodioOutput("out")
out.filename = "FCCOutput.root"
out.outputCommands = ["keep *"]
ApplicationMgr().TopAlg += [out]
