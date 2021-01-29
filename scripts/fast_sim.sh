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

options="options/Delphes_config.py"
card="cards/Pythia_ee_ZH_Htautau.cmd"
output="data/k4_delphes_output.root"
log="data/k4_log.txt"
n_events="10000"

k4run $options --Filename $card --filename $output -n $n_events > $log
fi
