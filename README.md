# Selective indexing classification system

This repository contains the source code for combination of 
a CNN and voting ensemble in the prediction of citations requiring
MeSH indexing

## Installation

To install clone this repository via
```
git clone https://github.com/saverymax/selective_indexing.git
```

## Usage

To run the system from the command line, enter
```
python SIM.py --path /path/to/citation/xml
```

For example
```
python SIM.py --path sample_citations.xml
```
will generate a set of predictions for the two citations in sample_citations.xml





