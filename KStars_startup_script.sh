#!/bin/bash

SCRIPT_PATH=$(dirname $(realpath -s $0))

sudo service ntp start
wait
cd $SCRIPT_PATH
python Input_parameters.py &
wait
python NEO_KStars.py &
wait
kstars
echo "Finished startup"
