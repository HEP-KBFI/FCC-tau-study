#!/bin/bash

# Run only Pythia simulation

if [ ! -d ${PWD}/"cards" ];
then
  echo "Cannot find 'cards' directory."

else
if [ ! -d ${PWD}/"data" ];
then
  mkdir data
fi

options="options/Pythia_config.py"
card="cards/Pythia_ee_ZH_Htautau.cmd"
output="data/p8_output.root"
log="data/pythia_log.txt"
n_events="100"

k4run $options --Filename $card --filename $output -n $n_events > $log
fi
