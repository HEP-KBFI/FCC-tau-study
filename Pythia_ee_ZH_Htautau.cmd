! File: Pythia_ee_ZH_Htautau.cmd
Random:setSeed = on
Main:timesAllowErrors = 10          ! how many aborts before run stops

! 2) Settings related to output in init(), next() and stat().
Next:numberCount = 100             ! print message every n events
Beams:idA = 11                     ! first beam, e+ = 11
Beams:idB = -11                    ! second beam, e- = -11

! 3) Hard process : ZH at 240 GeV.
Beams:eCM = 240  ! CM energy of collision
HiggsSM:ffbar2HZ = on

! 4) Settings for the event generation process in the Pythia8 library.
PartonLevel:ISR = on               ! initial-state radiation
PartonLevel:FSR = on               ! final-state radiation

! 5) Tuning.
25:m0        = 125.0               ! Higgs mass
23:onMode    = off				   ! switch off Z boson decays
23:onIfAny   = 13				   ! switch on Z boson decay to muons
25:onMode    = off				   ! switch off Higgs boson decays
25:onIfAny   = 15				   ! switch on Higgs boson decay to taus