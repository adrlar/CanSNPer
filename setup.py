from setuptools import setup
import sys

if sys.version_info[:2] != (2, 7):
    sys.exit('Sorry, only Python 2.7 is supported')

#def get_install_requires():
#    ''' Return a list with the dependencies for
#        CanSNPer depending on the python version'''
#    requires = ['numpy']
#    if sys.version_info[0] < 3:
#        requires.append('ete2')
#        return requires
#    else:
#        requires.append('ete3')
#        return requires

setup(
    name = "CanSNPer",
    version = "1.0.6",
    ulr = "https://github.com/adrlar/CanSNPer",
    description = "CanSNPer: A toolkit for SNP-typing using NGS data.",
    license = "GPL'",
    keywords = "Bioinformatics SNP-typing sequence-data",
    classifiers = [
        'License :: OSI Approved :: GPL',
        'Programming Language :: Python :: 2.7'
        ],
    install_requires = ['numpy', 'ete2'],
    #install_requires = get_install_requires(),
    packages = ['CanSNPer'],
    entry_points = {
        'console_scripts':[
            'CanSNPer=CanSNPer.__main__:main'
        ]
    }
)
