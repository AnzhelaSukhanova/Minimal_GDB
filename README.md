## Minimal graph database [![Build Status](https://travis-ci.org/AnzhelaSukhanova/Minimal_GDB.svg?branch=assignment1)](https://travis-ci.org/AnzhelaSukhanova/Minimal_GDB)
SPbU, fall semester 2020, formal language course

You will need the pygraphblas and pyformlang to work with this project. They can be install with:  
`conda install -c conda-forge pygraphblas ; pip3 install pyformlang`  
Or you can install the pygraphblas by following the instuctions from https://github.com/michelp/pygraphblas.

### Tests
There are some simple tests to review:
1) the functionality of the pygraphblas and pyformlang libraries;
2) the implementation of graph intersection using tensor product.  

They can be run with the command:  
`pytest -s src/tests.py`.  
To see the output of the graph intersection function on specific graphs/automatons (in the form of a pair "label — number of edges marked by it") use:  
`python src/main.py tests/graph<number>.txt tests/auto<number>.txt`.  
Also there are implementations of reachability requests between all pairs of vertices (reachability\_all() in src/main.py), from set of vertices (reachability\_from() in src/main.py) and from one set of vertices to another (reachability\_from\_to() in src/main.py).

### Time measurements
To get some test data (files with graphs and regular expressions) use:  
`gdown https://drive.google.com/uc?id=158g01o2rpdq5eL3Ari8e5SPbbeZTJspr`
Only then can you run time.sh.

