#!/bin/bash
#Scripting file for the first experiment of the multi-channel DART paper to generate results for all 100 runs

for i in {1..100}
do
    echo "RUN $i"
    python MCDARTExp1.py $i
done
