##Installing CanSNPer 
CanSNPer is written in Python and requires Python installed as well as several 
dependencies listed in the INSTALL document. Consult that file for detailed 
installation instructions. When the dependencies are all installed CanSNPer can 
be run as it is from the shell.

##Running CanSNPer
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

##Running the usual analysis 
CanSNPer takes a fasta file as input, using the argument `-i` or `--snp_type_file`  
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
CanSNPer -i fasta.fa -r Yersinia_pestis -tldv
```

##Threads
CanSNPer is fairly lightweight in terms of how much computational power it 
needs. However, If there are several reference strains to align to (as in the 
case of Fracisella tularensis) the alignments of the query to each reference 
are all assigned their own thread. That is, unless the user specifies a 
MAXIMUM number of threads to use. The default value is no limit (0). This 
option is called `-n`.

```
CanSNPer -i fasta.fa -r Yersinia_pestis -n2
```

##The `--allow_differences` argument
This argument allows CanSNPer to pass through a number of canSNP tree nodes 
even if the SNP is not in a derived state. The number of nodes that are 
permitted to be wrong is stated after `--allow_differences`. This option can be 
useful if you know there is a specific part of the sequence missing and that 
this will cause CanSNPer to overlook information. Use this option only if you 
are certain of the effects on the outcome. Here is an example:

```
CanSNPer -i BROKEN.fa --allow_differences 1
```

This may produce a warning, in addition to the classification, letting you 
know which SNPs (if any) were not in the derived state in the canSNP tree:

Classification of BROKEN.fa: B.24
```
#[WARNING] these SNPs were not in the derived state: B.3
```

##Setting up, or changing a CanSNPer database
A database complete with the current information is available with the CanSNPer 
distribution, but if you want to create a separate DB, or add to yours, here 
are some CanSNPer command line arguments that will help. The formatting of the 
SNP text file and the tree text file is explained in another section of this 
README.

The SQLite database file will be created automatically in the location 
specified in CanSNPer.conf (default is in your home folder). When you want to 
add a new organism to your database, use the -initialise_organism argument:

```
CanSNPer -initialise_organism
```

CanSNPer will ask for an organism name if you did not supply one using the -r 
argument.

After initialising an organism you can start to add information to it. To add 
the list of SNPs use the `--import_snp_file` argument and supply the text-file. 
If you did not supply the -r argument CanSNPer will ask which organism this 
data belongs to.

```
CanSNPer -r Yersinia_pestis --import_snp_file y_snps.txt
```

Next, if you want to upload a new, or update an existingcanSNP tree, use 
`--import_tree_file`. The tree in the CanSNPer database will be replaced:

```
CanSNPer -r Yersinia_pestis --import_tree_file y_tree.txt
```

The last database altering option in CanSNPer allows you to import a fasta 
sequence to the SQLite database. A sequence file has to be imported for each of 
the reference strains that are used in the SNP table. You can only import one 
at a time, though:

```
CanSNPer -r Yersinia_pestis --import_seq_file CO92.fa
```

CanSNPer list the reference strains that are in the SNP list, and you choose 
one of them to link to the sequence you are uploading.

With the `--import_seq_file` argument you can also add the `--strain_name` and tell 
CanSNPer what the strain name is without having to go through the prompt:

```
CanSNPer -r Yersinia_pestis --import_seq_file CO92.fa --strain_name CO92
```

##Formatting a canSNP tree text file for CanSNPer
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
##Formatting a SNP list text file for CanSNPer
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

##Running CanSNPer in Galaxy
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


##Citing CanSNPer 
The first verion of CanSNPer is published in Bioinformatics.
```
Lärkeryd A, Myrtennäs K, Karlsson E, Dwibedi CK, Forsman M, Larsson P, Johansson A, Sjödin A: 
CanSNPer: a hierarchical genotype classifier of clonal pathogens. Bioinformatics 2014
```
