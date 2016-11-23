from setuptools import setup
import sys


if sys.version_info[:2] != (2, 7):
    sys.exit('Sorry, only Python 2.7 is supported')

setup(
    name = "CanSNPer",
    version = "1.0.6",
    ulr = "https://github.com/adrlar/CanSNPer",
    description = "CanSNPer: A toolkit for SNP-typing using NGS data.",
    license = "GPL'",
    keywords = "Bioinformatics SNP-typing sequence-data",
    classifiers = [
        'Development Status :: 5 - Alpha',
        'License :: OSI Approved :: GPL',
        'Programming Language :: Python :: 2.7'
        ],
    install_requires = ['numpy', 'ete2'],
    packages = ['CanSNPer'],
    entry_points = {
        'console_scripts':[
            'CanSNPer=CanSNPer.__main__:main'
        ]
    }
)
