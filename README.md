## Minimal graph database
master: [![Build Status](https://travis-ci.org/AnzhelaSukhanova/Minimal_GDB.svg?branch=master)](https://travis-ci.org/AnzhelaSukhanova/Minimal_GDB)
dev: [![Build Status](https://travis-ci.org/AnzhelaSukhanova/Minimal_GDB.svg?branch=dev)](https://travis-ci.org/AnzhelaSukhanova/Minimal_GDB)
SPbU, fall semester 2020, formal language course

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
`python src/main.py graph-regexp <filename1> <filename2>`.  
Also there are implementations of reachability requests:
`python src/main.py regexp <filename>` or `python src/main.py graph <filename>`  
Moreover, you can use `python src/main.py grammar <filename>` (it will require word input) to test CYK or `python src/main.py graph-grammar <filename1> <filename2>` to test three types of CFPQ.

### Time measurements
To get some test data (files with graphs and regular expressions) use:  
`gdown https://drive.google.com/uc?id=158g01o2rpdq5eL3Ari8e5SPbbeZTJspr`.  
Only then can you run time.sh (`bash time.sh`) that measures the running times of the transitive closure and intersection implementations and the output of the latter. The measurement results will be in the file time_out.txt. The result of a particular measurement is a list of times for five runs, their average and variance. Read more about it in reports/report1.pdf.

