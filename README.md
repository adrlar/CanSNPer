[![install with bioconda](https://img.shields.io/badge/install%20with-bioconda-brightgreen.svg?style=flat-square)](http://bioconda.github.io/recipes/cansnper/README.html)

## Installing CanSNPer
CanSNPer is written in Python and requires Python installed as well as several 
dependencies. The easiest way to install CanSNPer is using 
[Bioconda conda](https://bioconda.github.io/recipes/cansnper/README.html) channel 
or with pip. Consult the INSTALL document for detailed installation instructions. 
When the dependencies are all installed CanSNPer can be run as it is from the shell.

## Running CanSNPer
All CanSNPer runs start with the main CanSNPer script. Following installation,
try to invoke the CanSNPer help with this command:

```
CanSNPer -h
```

Sometimes CanSNPer will want more information from you, such as the name of the 
organism you want to use as a reference when aligning. This is done by a prompt 
where you type the answer in and press enter to submit. If you are ever stuck 
in a prompt or dont know what to enter, type 'exit' to exit. 
  
Note that not all information that CanSNPer needs can be given interactively. 
File names can only be given as a command argument. 

## Running the usual analysis 
CanSNPer takes a fasta file as input, using the argument  `--snp_type_file (-i)`  
with the file name, the reference organism is given with the argument `--reference (-r)` and the
path to the CanSNPer database is given with the `--db_path (-b)`:

```
CanSNPer --snp_type_file /path/to/fasta.fa -r Yersinia_pestis -b CanSNPerDB.db
```

If you want to change the output of CanSNPer use the arguments `--tab_sep (-t)`, 
`--draw_tree (-d)`, `--list_snps (-l)` or `--verbose (-v)`. The following command 
will type fasta.fa with Y. pestis as reference, print the outcome in a tab 
separated format, create a text file with all SNPs listed, draw a canSNP tree 
and save it as a PDF file and CanSNPer will print whatever it is doing (because 
we used all the `-t`, `-l`, `-d` and `-v` options):

```
CanSNPer -i fasta.fa -r Yersinia_pestis -tldv -b CanSNPerDB.db
```

## Threads
CanSNPer is fairly lightweight in terms of how much computational power it 
needs. However, If there are several reference strains to align to (as in the 
case of Fracisella tularensis) the alignments of the query to each reference 
are all assigned their own thread. That is, unless the user specifies a 
MAXIMUM number of threads to use. The default value is no limit (0). This 
option is called `-n`.

```
CanSNPer -i fasta.fa -r Yersinia_pestis -b CanSNPerDB -n2 
```

## The `--allow_differences` argument
This argument allows CanSNPer to pass through a number of canSNP tree nodes 
even if the SNP is not in a derived state. The number of nodes that are 
permitted to be wrong is stated after `--allow_differences`. This option can be 
useful if you know there is a specific part of the sequence missing and that 
this will cause CanSNPer to overlook information. Use this option only if you 
are certain of the effects on the outcome. Here is an example:

```
CanSNPer -i BROKEN.fa --allow_differences 1 -b CanSNPerDB.db
```

This may produce a warning, in addition to the classification, letting you 
know which SNPs (if any) were not in the derived state in the canSNP tree:

Classification of BROKEN.fa: B.24
```
#[WARNING] these SNPs were not in the derived state: B.3
```

## Setting up, or changing a CanSNPer database
A database complete with the current information is available with the CanSNPer 
distribution, but if you want to create a separate DB, or add to yours, here 
are some CanSNPer command line arguments that will help. The formatting of the 
SNP text file and the tree text file is explained in another section of this 
README.

The SQLite database file will be created automatically in the location 
specified in CanSNPer.conf (default is in your home folder). When you want to 
add a new organism to your database, use the -initialise_organism argument:

```
CanSNPer -initialise_organism -b CanSNPerDB.db
```

CanSNPer will ask for an organism name if you did not supply one using the `-r` 
argument.

After initialising an organism you can start to add information to it. To add 
the list of SNPs use the `--import_snp_file` argument and supply the text-file. 
If you did not supply the `-r` argument CanSNPer will ask which organism this 
data belongs to.

```
CanSNPer -r Yersinia_pestis --import_snp_file y_snps.txt -b CanSNPerDB.db
```

Next, if you want to upload a new, or update an existingcanSNP tree, use 
`--import_tree_file`. The tree in the CanSNPer database will be replaced:

```
CanSNPer -r Yersinia_pestis --import_tree_file y_tree.txt -b CanSNPerDB.db
```

The last database altering option in CanSNPer allows you to import a fasta 
sequence to the SQLite database. A sequence file has to be imported for each of 
the reference strains that are used in the SNP table. You can only import one 
at a time, though:

```
CanSNPer -r Yersinia_pestis --import_seq_file CO92.fa -b CanSNPerDB.db
```

CanSNPer list the reference strains that are in the SNP list, and you choose 
one of them to link to the sequence you are uploading.

With the `--import_seq_file` argument you can also add the `--strain_name` and tell 
CanSNPer what the strain name is without having to go through the prompt:

```
CanSNPer -r Yersinia_pestis -b CanSNPerDB.db --import_seq_file CO92.fa --strain_name CO92 
```

## Formatting a canSNP tree text file for CanSNPer
The format that CanSNPer accepts as a tree is very simple.  
1. The first line MUST contain the root of the tree.  
2. All subsequent lines represent one intermediate or leaf node in the tree. It 
is listed with all its ancestors in order, separated by semi-colons, with the 
node name at the end.
  
This formatting creates a tree that is easy to inspect in text form, in any 
editor.

Here is an example tree:
```
Root
Root;SNP1
Root;SNP1;SNP3
Root;SNP1;SNP4
Root;SNP1;SNP4;SNP5
Root;SNP2
```

The only node with a positional requirement, in terms of line number, is the 
root and while it doesnt exactly make much sense to write it like this, the 
following tree is also valid:
```
Root
Root;SNP1;SNP4;SNP5
Root;SNP1;SNP4
Root;SNP1
Root;SNP2
Root;SNP1;SNP3
```
## Formatting a SNP list text file for CanSNPer
The SNP list is a tab separated text file and must have the information in the 
following order: SNP name, Organism name, Reference, Strain, Position, Derived 
base, Ancestral base

Here is an example:
```
B.1	Francisella	Svensson	LVS	23942	A	G
```
The header line is not needed and any line beginning with a '#' will be 
considered a comment line. The order of derived and ancestral state is of 
particular importance because there is no way for CanSNPer to tell the columns 
apart.

The column Organism name is not used by CanSNPer at this moment, but is kept in 
order to ease any future work with the file formats and import functions. It 
can be left out, but there must then be two tabs between SNP name and Reference.

## Running CanSNPer in Galaxy
There is a Galaxy tool definition file available with the Github CanSNPer 
distribution called CanSNPer.xml. Place this file along with the CanSNPer main 
script and the CanSNPer.conf in the Galaxy tools folder and make sure to edit 
the Galaxy tool_conf.xml tool-registry file. More detailed instructions on how 
to add a tool to Galaxy can be found at wiki.galaxyproject.org.

There is one more thing that may need additional configuration when running 
CanSNPer in Galaxy; the tmp-folder set by Galaxy. The default may cause issues 
running progressiveMauve and will in that case show up as an error in the 
CanSNPer error file produced by Galaxy. Set the tmp-file path in the 
universe_wsgi.ini config file located in your Galaxy root. Just make sure you 
have the apropriate permissions to work in the set directory.

CanSNPer has a specific command-line option that is specific for a Galaxy run. 
It is `--galaxy` and should not be invoked unless CanSNPer is running from Galaxy.

The CanSNPer galaxy tool is largely untested and feedback is greatly 
appreciated.


## Citing CanSNPer 
The first verion of CanSNPer is published in Bioinformatics.

```
Lärkeryd A, Myrtennäs K, Karlsson E, Dwibedi CK, Forsman M, Larsson P, Johansson A, Sjödin A: 
CanSNPer: a hierarchical genotype classifier of clonal pathogens. Bioinformatics 2014
```

Depending on which canonical SNPs that are used to classify your strain some the following 
publications should also be cited. More information about were each CanSNP is publiched may 
be found in snp.txt file for each genus. 

__Francisella__

- Birdsell, D. N. et al. Francisella tularensis subsp. tularensis Group A.I, United States. Emerg. Infect. Dis. 20, 861–865 (2014).
- Chanturia, G. et al. Phylogeography of Francisella tularensis subspecies holarctica from the country of Georgia. BMC Microbiol. 11, 139 (2011).
- Dwibedi, C. et al. Long-range dispersal moved Francisella tularensis into western Europe from the East. Microbial Genomics (2016)
- Gyuranecz, M. et al. Phylogeography of Francisella tularensis subsp. holarctica, Europe. Emerg. Infect. Dis. 18, 290–3 (2012).
- Karadenizli, a et al. Genomic analyses of Francisella tularensis strains confirm disease transmission from drinking water sources, Turkey, 2008, 2009 and 2012. Eurosurveillance 20, 21136 (2015).
- Karlsson, E. et al. The phylogeographic pattern of Francisella tularensis in Sweden indicates a Scandinavian origin of Eurosiberian tularaemia. Environ. Microbiol. 15, 634–645 (2013).
- Myrtennäs, K. et al. Introduction and persistence of tularemia in Bulgaria. Infect. Ecol. Epidemiol. 6, 1–9 (2016).
- Schulze, C. et al. High and novel genetic diversity of Francisella tularensis in Germany and indication of environmental persistence. Epidemiol. Infect. 144, 3025–3036 (2016).
- Svensson, K. et al. A real-time PCR array for hierarchical identification of Francisella isolates. PLoS One 4, e8360 (2009).
- Vogler, A. J. et al. Phylogeography of Francisella tularensis: global expansion of a highly fit clone. J. Bacteriol. 191, 2474–84 (2009).
- Wittwer, M et al. Population Genomics of Francisella tularensis subsp. holarctica and its Implication on the Eco-Epidemiology of Tularemia in Switzerland. Front Cell Infect Microbiol. 8: 89. (2018).

__Bacillus__
- Van Ert, M. N. et al. Global genetic population structure of Bacillus anthracis. PLoS One 2, e461 (2007).

__Brucella__
- Foster, J. T. et al. Real-time PCR assays of single-nucleotide polymorphisms defining the major Brucella clades. J. Clin. Microbiol. 46, 296–301 (2008).

__Coxiella__
- Karlsson, E. et al. Eight New Genomes and Synthetic Controls Increase the Accessibility of Rapid Melt-MAMA SNP Typing of Coxiella burnetii. PLoS One 9, e85417 (2014).

__Yersinia__
- Morelli, G. et al. Yersinia pestis genome sequencing identifies patterns of global phylogenetic diversity. Nat. Genet. 42, 1140–3 (2010).
