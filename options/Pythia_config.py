# Run Pythia simulation and save all results
from Gaudi.Configuration import *

# Workflow Steering
from Configurables import ApplicationMgr

ApplicationMgr().EvtSel = 'NONE'
ApplicationMgr().EvtMax = 100

# Data event model based on Podio
from Configurables import FCCDataSvc

podioEvent = FCCDataSvc("EventDataSvc")
ApplicationMgr().ExtSvc += [podioEvent]
ApplicationMgr().OutputLevel = INFO

# Pythia generator
from Configurables import PythiaInterface

pythia8gentool = PythiaInterface()
pythia8gentool.Filename = "Pythia_ee_ZH_Htautau.cmd"

# Write the HepMC::GenEvent to the data service
from Configurables import GenAlg

pythia8gen = GenAlg()
pythia8gen.SignalProvider = pythia8gentool
pythia8gen.hepmc.Path = "hepmc"
ApplicationMgr().TopAlg += [pythia8gen]

# Reads an HepMC::GenEvent from the data service and writes a collection of EDM Particles
from Configurables import HepMCToEDMConverter

hepmc_converter = HepMCToEDMConverter("Converter")
hepmc_converter.hepmc.Path = "hepmc"
hepmc_converter.hepmcStatusList = []  # convert particles with all statuses
hepmc_converter.genparticles.Path = "genParticles"
hepmc_converter.genvertices.Path = "genVertices"
ApplicationMgr().TopAlg += [hepmc_converter]

# FCC event-data model output -> define objects to be written out
from Configurables import PodioOutput

out = PodioOutput("out")
out.filename = "FCCOutput.root"
out.outputCommands = [
    "keep *",
]
ApplicationMgr().TopAlg += [out]
