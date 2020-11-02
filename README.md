## Minimal graph database
SPbU, fall semester 2020, formal language course
#### master:
[![Build Status](https://travis-ci.org/AnzhelaSukhanova/Minimal_GDB.svg?branch=master)](https://travis-ci.org/AnzhelaSukhanova/Minimal_GDB)  
#### dev:
[![Build Status](https://travis-ci.org/AnzhelaSukhanova/Minimal_GDB.svg?branch=dev)](https://travis-ci.org/AnzhelaSukhanova/Minimal_GDB)  

You will need the pygraphblas and pyformlang to work with this project. They can be install with:  
`conda install -c conda-forge pygraphblas ; pip3 install pyformlang`  
Or you can install the pygraphblas by following the instuctions from https://github.com/michelp/pygraphblas.

### Tests
There are some simple tests to review:
1) the functionality of the pygraphblas and pyformlang libraries;
2) the implementation of graph intersection using tensor product;
3) the implementation of CYK;
4) three implementations of CFPQ (by Hellings Algorithm, boolean matrix multiplication and tensor product).

They can be run with the command:  
`pytest -s src/tests.py`.  

To see the output of the graph intersection function (in the form of a pair "label — number of edges marked by it") use (it give you the running times too):  
`python src/main.py intersection <graph_file> <regexp_file>`.  
Also there are implementations of reachability requests:
`python src/main.py clos_regexp <regexp_file>` or `python src/main.py clos_graph <graph_file>`  
You can use `python src/main.py cyk <grammar_file>` (it will require word input) to test CYK or `python src/main.py cfpq <graph_file> <grammar_file>` to test three types of CFPQ.

### Time measurements
Read about time measurements of transitive closure and intersection implementations and the output of the latter in reports/report1.pdf.  
Read about time comparison of different CFPQ-algorithms in reports/report2.pdf.
