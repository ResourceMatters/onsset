onsset : Open Source Spatial Electrification Tool
=================================================

[![PyPI version](https://badge.fury.io/py/onsset.svg)](https://badge.fury.io/py/onsset)
[![Build Status](https://travis-ci.com/OnSSET/onsset.svg?branch=master)](https://travis-ci.com/OnSSET/onsset)
[![Coverage Status](https://coveralls.io/repos/github/OnSSET/onsset/badge.svg?branch=master)](https://coveralls.io/github/OnSSET/onsset?branch=master)
[![Documentation Status](https://readthedocs.org/projects/onsset/badge/?version=latest)](https://onsset.readthedocs.io/en/latest/?badge=latest)

# Scope

This repository contains the source code of the Open Source Spatial Electrification Tool
([OnSSET](http://www.onsset.org/)), modified to reflect the particular circumstances of the DRC. 

## Contains

This folder contains:
* Costs_preparation.ipynb - A notebook to develop the cost layer required for the new grid routing algorithm
* OnSSET_notebook.ipynb - A notebook to run the OnSSET tool with or without the new grid reouting algorithm
* onsset - a folder with the neccessary python files and the gui_runner.py file to run the OnSSET tool with or without the new grid routing algorithm using e.g. PyCharm
* GridExtensionData.zip - a zip folder containing the neccessary layers after the Costs_preparation.ipynb to run OnSSET with the new grid algorithm 

## Installation

**Requirements**

The extraction module (as well as all supporting scripts in this repo) have been developed in Python 3. You are recommended to install [Anaconda's free distribution](https://www.anaconda.com/distribution/) as suited for your operating system. 

**Install the extraction repository from GitHub**

After installing Anaconda you can download the repository directly or clone it to your designated local directory using:

```
> conda install git
> git clone https://github.com/ResourceMatters/onsset/
```
Once installed, open anaconda prompt and move to your local "OnSSET" directory using:
```
> cd ..\OnSSET
```

In order to be able to run the tool (main.ipynb and funcs.ipynb) you have to install all necessary packages. "environment.yml" contains all of these and can be easily set up by creating a new virtual environment named OnSSET_GIS (or any other name you prefer) using:

```
conda env create --name OnSSET_GIS --file environment.yml
```

This might take some time. When complete, activate the virtual environment using:

```
conda activate OnSSET_extraction
```

With the environment activated, you can now move to the extraction directory and start a "jupyter notebook" session by simply typing:

```
..\OnSSET> jupyter notebook 
```

If you use the gui_runner.py file to run the code in PyCharm, choose the interpreter to be OnSSET_GIS

## Contact
For more information regarding the tool, its functionality and implementation
please visit https://www.onsset.org or contact the development team
at seap@desa.kth.se.
