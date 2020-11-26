#!/bin/sh

REGEXES=refinedDataForRPQ/LUBM300/regexes/'q*0'
GRAPHS=( [0]=refinedDataForRPQ/LUBM300/LUBM300.txt [1]=refinedDataForRPQ/LUBM500/LUBM500.txt [2]=refinedDataForRPQ/LUBM1M/LUBM1M.txt [3]=refinedDataForRPQ/LUBM1.5M/LUBM1.5M.txt [4]=refinedDataForRPQ/LUBM1.9M/LUBM1.9M.txt)

for r in $REGEXES
    do
        python main.py clos_regexp $r
    done

for (( i=0; i < 5; i++ ))
do
    python main.py clos_graph ${GRAPHS[i]}
    for r in $REGEXES
    do
        python main.py intersection ${GRAPHS[i]} $r
    done
done

