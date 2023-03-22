#!/bin/bash
#Scripting file for the second experiment of the multi-channel DART paper to generate results for all 100 runs for the non-MC-DART algorithm

for i in {1..100}
do
    echo "RUN $i"
    python MCDARTExp2.py $i 0
done
