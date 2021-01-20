## Minimal graph database
SPbU, fall semester 2020, formal language course

| master | dev | assignment7 |
|:------:|:---:|:-----------:|
|[![Build Status](https://travis-ci.org/AnzhelaSukhanova/Minimal_GDB.svg?branch=master)](https://travis-ci.org/AnzhelaSukhanova/Minimal_GDB) | [![Build Status](https://travis-ci.org/AnzhelaSukhanova/Minimal_GDB.svg?branch=dev)](https://travis-ci.org/AnzhelaSukhanova/Minimal_GDB) | [![Build Status](https://travis-ci.org/AnzhelaSukhanova/Minimal_GDB.svg?branch=assignment7)](https://travis-ci.org/AnzhelaSukhanova/Minimal_GDB) |

You will need the pygraphblas and pyformlang to work with this project. They can be install with:  
`conda install -c conda-forge pygraphblas ; pip3 install pyformlang`  
Or you can install the pygraphblas by following the instuctions from https://github.com/michelp/pygraphblas.

### Tests
There are some simple tests to review:
1) the functionality of the pygraphblas and pyformlang libraries;
2) the implementation of graph intersection using tensor product;
3) the implementation of CYK;
4) three implementations of CFPQ (by Hellings Algorithm, boolean matrix multiplication and tensor product);
5) minimal syntactical analyzer;
6) derivative-based regular language recognizer.

They can be run with the command:  
`pytest -s src/tests.py`.  

To see the output of the graph intersection function (in the form of a pair "label — number of edges marked by it") use (it give you the running times too):  
`python src/main.py inter <graph_file> <regexp_file>`.  
Also there are implementations of reachability requests:
`python src/main.py clos_regexp <regexp_file>` or `python src/main.py clos_graph <graph_file>`  
You can use `python src/main.py cfpq <graph_file> <grammar_file>` to test three types of CFPQ.  
With `python src/main.py cfpq <regexp_file>` you can check if a word (you will need to enter it) belongs to the regular language, given by the regex.  

To parse your program do:
`python src/main.py sa syntax <prog_file>`

### Time measurements
Read about time measurements of transitive closure and intersection implementations and the output of the latter in reports/report1.pdf.  
Read about time comparison of different CFPQ-algorithms in reports/report2.pdf.


### GDB query language syntax
Pay attention to the fact that the symbols and names of the graphs and databases can be written with **{a-z, 0-9, ., /}** (not just "/" or ".") without spaces. Do not forget to put spaces before words and around service symbols. Every next statement starts on a new line and can be separated with `\`.  
First connect to the database:
`connect <db_name>`  
The edges or their number can be extracted from gdb by:
`sel edg <graph>` and `sel # edg <graph>` respectively  
To specify a graph enter:
`gr <graph_name>` or `(query <reg_expr> )`  
Also, as a graph, you can give the intersection of two graphs:
`(inter gr <graph_name1> gr <graph_name2>)`  
Regular expression can be written with according to the following rules:
* `s` is placed before the not service symbols;
* the asterisk indicates zero or more occurrences of the preceding regexp: `<regexp> *`;
* the plus sign indicates one or more occurrences of the preceding regexp: `<regexp> +`;
* the question mark indicates zero or one occurrences of the preceding regexp: `<regexp> ?`;
* the exclamation mark denotes the alternation: `<regexp1> ! <regexp2>`;
* the exclamation mark denotes the concatenation: `<regexp1> . <regexp2>`.

Check out examples of syntactically correct queries in tests/prog0, tests/prog1, tests/prog2.
