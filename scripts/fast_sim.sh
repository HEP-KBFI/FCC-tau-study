#!/bin/bash

# Perform a fast simulation in Delphes with IDEA config file from FCCSW

if [ ! -d ${PWD}/"cards" ];
then
  echo "Cannot find 'cards' directory."

else
if [ ! -d ${PWD}/"data" ];
then
  mkdir data
fi

options="$FCCSW/Sim/SimDelphesInterface/options/PythiaDelphes_config_IDEAtrkCov.py"
card="cards/Pythia_ee_ZH_Htautau.cmd"
output="data/delphes_output.root"
log="data/log.txt"
n_events="1000"

fccrun $options --Filename $card --filename $output -n $n_events > $log
fi
