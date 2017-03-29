##Installing CanSNPer
CanSNPer is written in Python and requires Python installed as well as several 
dependencies listed below. The software is developed and tested with Python 
version 2.7 but earlier (2.5, 2.6) may work just as well. Due to other 
dependencies other versions of Python are not supported.

### Bioconda
With an activated Bioconda channel (see [Set up channels](https://bioconda.github.io/index.html#set-up-channels)), 
install with:
`conda install cansnper`
and update with:
`conda update cansnper`

This will install CanSNPer with all Python and other dependencies (except progressivemauve).

Remark that Bioconda only supports MacOS and Linux systems. 

### Python Package Index
An alternative way to install CanSNPer and Python dependencies is using PyPI with: 
`pip install cansnper`

Non-Python dependencies needs to be installed manuelly. See dependency secion below.

### Latest source code
To install the latest source code, start by cloning this repo, change into the CanSNPer directory and
run the setup file. This will install CanSNPer and the Python dependecies.

```
git clone https://github.com/adrlar/CanSNPer.git
cd CanSNPer
python setup.py
```

Non-Python dependencies needs to be installed manuelly. See dependency secion below.

## Testing the installation
When the dependencies are all installed CanSNPer can be run as it is from the 
shell.

To begin with, try:
```
CanSNPer --help
```

If there are no errors and you see the help text printed, CanSNPer is working 
correctly and you can go on to do your analysis.

If all dependencies are installed you can also run CanSNPer without running the
`setup.py`. This is done by running `python CanSNPer -h` from within the CanSNPer
directory.

More on how to run CanSNPer in its various modes can be found in the README 
file that came with the distribution.

CanSNPer has been tested on Linux and MacOS (OSX), but feel free to tinker with setting up 
a working version on your favorite OS. Mauve is available on other platforms.

##Dependencies
Software that must be installed before running CanSNPer:

[Python (2.7.X)](http://www.python.org/getit/)  
Most Linux distributions come with Python installed. However we recommend using 
[Conda](http://conda.pydata.org/docs/) to setup a flexible Python environment. 

[ETE2](http://ete.cgenomics.org/)  
ETE2 has a number of additional dependencies, listed in their install 
notes. Most notably, there are several dependencies that are not needed 
for CanSNPer, but they may raise warnings as ETE2 is loaded. Note that
Qt < 5 is needed to run ETE2.

[NumPy](http://www.numpy.org/)  
Simple install instructions are available for this package.

[progressiveMauve](http://darlinglab.org/mauve/mauve.html)  
The progressiveMauve binary must be in the PATH or specifically set in 
the CanSNPer.conf file.
