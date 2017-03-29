#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
CanSNPer: A toolkit for SNP-typing using NGS data.
Copyright (C) 2016 Adrian Lärkeryd

VERSION 1.0.9

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
from sys import stderr, argv, version_info, exit
from os import path, remove, makedirs, getcwd
from shutil import copy as shutil_copy
from uuid import uuid4
import errno
import inspect
import getpass
import time
import pkg_resources

import argparse
import re
import sqlite3

from subprocess import Popen

if version_info[0] < 3:
    from ete2 import Tree, faces, AttrFace, TreeStyle, NodeStyle
else:
    from ete3 import Tree, faces, AttrFace, TreeStyle, NodeStyle


def parse_arguments():
    '''Parses arguments from the command line and sends them to read_config

    '''

    cansnper_description = '''
    CanSNPer: A toolkit for SNP-typing using NGS data.
    Copyright (C) 2016 Adrian Lärkeryd.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    If you are stuck in a prompt and do not know what to do,
    type 'exit' to exit.
    '''
    # Parse command line arguments
    parser = argparse.ArgumentParser(description=cansnper_description)
    parser.add_argument("-r", "--reference",
                        help="the name of the organism")
    parser.add_argument("-i", "--query",
                        help="fasta sequence file name that is to be analysed")
    parser.add_argument("-b", "--db_path",
                        help="path to CanSNPerDB.db")
    parser.add_argument("--import_tree_file",
                        help="imports a tree structure into the database")
    parser.add_argument("--import_snp_file",
                        help="imports a list of SNPs into the database")
    parser.add_argument("--import_seq_file",
                        help="loads a sequence file into the database")
    parser.add_argument("--strain_name",
                        help="the name of the strain")
    parser.add_argument("--allow_differences",
                        help="allow a number of SNPs to be wrong, i.e." +
                        "continue moving down the tree even if none of the " +
                        "SNPs of the lower level are present [0]", type=int,
                        default=0)
    parser.add_argument("-t", "--tab_sep", action="store_true",
                        help="print the results in a simple tab " +
                        "separated format")
    parser.add_argument("-d", "--draw_tree", action="store_true",
                        help="draw a pdf version of the tree, marking SNPs " +
                        "of the query sequence")
    parser.add_argument("-m", "--progressiveMauve",
                        help="path to progressiveMauve binary file")
    parser.add_argument("-l", "--list_snps", action="store_true",
                        help="lists the SNPs of the given sequence")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="prints some more information about the " +
                        "goings-ons of the program while running")
    parser.add_argument("-s", "--save_align", action="store_true",
                        help="saves the alignment file")
    parser.add_argument("-n", "--num_threads",
                        help="maximum number of threads CanSNPer is " +
                        "allowed to use, the default [0] is no limit, " +
                        "CanSNPer will start one process per " +
                        "reference genome while aligning", type=int, default=0)
    parser.add_argument("-delete_organism", action="store_true",
                        help="deletes all information in the database " +
                        "concerning an organism")
    parser.add_argument("-initialise_organism", action="store_true",
                        help="initialise a new table for an organism")
    parser.add_argument("-f", "--tmp_path",
                        help="where temporary files are stored")
    parser.add_argument("-q", "--dev", action="store_true", help="dev mode")
    parser.add_argument("--galaxy", action="store_true",
                        help="argument used if Galaxy is running CanSNPer, " +
                        "do NOT use.")

    # Exit and print help if there were no arguments
    if len(argv) == 1:
        parser.print_help()
        exit()

    args = parser.parse_args()

    # Send the command line arguments to read_config,
    # it will return a compiled dict of configurations
    return read_config(args)


def read_config(args):
    '''Reads the configuration file, merges it with command line
    arguemts and returns all settings.

    Keyword arguments:
    args -- the collection of command line arguments

    Options stated on the command line override anything written in the
    config file.

    '''
    user = getpass.getuser()

    version = '1.0.8'

    config_list = {"tmp_path": "string",
                   "db_path": "string",
                   "mauve_path": "string",
                   "x2fa_path": "string",
                   "num_threads": "int",
                   "verbose": "boolean",
                   "allow_differences": "int",
                   "save_align": "boolean",
                   "draw_tree": "boolean",
                   "list_snps": "boolean",
                   "reference": "string",
                   "tab_sep": "boolean",
                   "dev": "boolean",
                   "galaxy": "boolean",
                   "db_path": "string"}

    config = dict()

    # Default settings
    config["tmp_path"] = "/tmp/CanSNPer_%s/" % user
    config["db_path"] = None
    config["mauve_path"] = "progressiveMauve"  # In your PATH
    config["x2fa_path"] = "x2fa.py"  # In your PATH
    config["allow_differences"] = 0
    config["num_threads"] = 0
    config["tab_sep"] = False
    config["verbose"] = False
    config["save_align"] = False
    config["draw_tree"] = False
    config["list_snps"] = False
    config["reference"] = None
    config["dev"] = False
    config["galaxy"] = False
    config["query"] = None
    config["import_tree_file"] = None
    config["import_snp_file"] = None
    config["import_seq_file"] = None
    config["strain_name"] = None
    config["delete_organism"] = None
    config["initialise_organism"] = None

    if args.dev:
        config["dev"] = True
        config["verbose"] = True  # Want verbose output if we are running dev
    if args.reference:
        config["reference"] = args.reference
    if args.query:
        config["query"] = args.query
    if args.db_path:
        config["db_path"] = args.db_path
    if args.import_tree_file:
        config["import_tree_file"] = args.import_tree_file
    if args.import_snp_file:
        config["import_snp_file"] = args.import_snp_file
    if args.import_seq_file:
        config["import_seq_file"] = args.import_seq_file
    if args.strain_name:
        config["strain_name"] = args.strain_name
    if args.allow_differences:
        config["allow_differences"] = int(args.allow_differences)
    if args.tab_sep:
        config["tab_sep"] = True
    if args.draw_tree:
        config["draw_tree"] = True
    if args.progressiveMauve:
        config["mauve_path"] = args.progressiveMauve
    if args.list_snps:
        config["list_snps"] = True
    if args.verbose:
        config["verbose"] = True
    if args.save_align:
        config["save_align"] = True
    if args.num_threads:
        config["num_threads"] = int(args.num_threads)
    if args.delete_organism:
        config["delete_organism"] = True
    if args.initialise_organism:
        config["initialise_organism"] = True
    if args.galaxy:
        config["galaxy"] = True
    if args.tmp_path:
        config["tmp_path"] = args.tmp_path
    if config["dev"]:  # Developer printout
        print("#[DEV] configurations:%s" % config)
    if config["verbose"]:
        print("#Version: %s" % version)
        if config["galaxy"]:
            print("#Running through Galaxy")
    return config


def get_organism(config, c):
    '''Returns the organism name chosen.

    If it was supplied as an argument, this is returned,
    otherwise call function select_table() that lets
    the user pick an organism name

    '''
    if config["reference"]:
        return config["reference"]
    else:
        return select_table(c)


def get_strain(organism, config, c):
    '''Returns the strain chosen.

    Keyword arguments:
    organism -- the organism name

    If it was supplied as an argument, this is returned,
    otherwise call function select_strain() that lets
    the user pick a strain in the selected organism

    '''
    if config["strain_name"]:
        return config["strain_name"]
    else:
        return select_strain(organism, c)


def select_table(c):
    '''Returns an organism name chosen by the user.'''
    c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = c.fetchall()

    # You are not supposed to be able to pick one of these
    tables_NOT_to_list = ["Sequences", "Tree"]

    table_list = list()
    db_name = ""

    # print(the tables and enter them into table list, for cross-checking the user input)
    print("The organisms currently in the database are:")
    for table in tables:
        if not table[0] in tables_NOT_to_list:
            print(table[0])
            table_list.append(table[0])
    while True:
        db_name = raw_input("Choose one: ")
        if db_name in table_list:  # Spell-check!
            break
        elif db_name.strip().lower() == "exit":
            exit("Exiting...")
    return db_name


def select_strain(db_name, c):
    '''Returns a strain chosen by the user.

    Keyword arguments:
    db_name -- the organism (or as named here, database)

    '''
    c.execute("SELECT DISTINCT Strain FROM %s" % db_name)
    rows = c.fetchall()
    strain_list = list()

    # print(the strains available in this table)
    for row in rows:
        print("%s" % row[0].strip())
        strain_list.append(row[0].strip())
    while True:
        strain_name = raw_input('Choose strain name to link to this file: ')
        if strain_name in strain_list:  # Spell-check!
            break
        elif strain_name.strip().lower() == "exit":
            exit("Exiting...")
    return strain_name


def silent_remove(file_name):
    '''Removes a file, without throwing no-such-file-or-directory-error.

    Keyword arguments:
    file_name -- the file name of the file that is to be removed

    Raises any error that is not an ENOENT

    '''
    try:
        remove(file_name)
    except OSError as e:
        if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
            raise  # re-raise exception if a different error occured


def initialise_table(config, c):
    '''Initialises a table in the SQLite3 database.

    Prompts the user for an organism name that is
    used as the table name.

    '''
    if config["reference"]:
        organism_name = config["reference"]
    else:
        # Cant use get_organism() because we need a new organism name, not select one of the existing
        organism_name = raw_input("Enter organism name: ")
        if organism_name.strip() == "exit":
            exit("Exiting...")
    try:
        # Try to execute, otherwise spit out the error
        c.execute("CREATE TABLE IF NOT EXISTS Tree (Name text, Children text, Organism text)")
        c.execute("CREATE TABLE IF NOT EXISTS Sequences (Organism text, Strain text, Sequence text)")
        c.execute("CREATE TABLE IF NOT EXISTS %s (SNP text, Reference text, Strain text, Position integer, Derived_base text, Ancestral_base text)" % organism_name)
    except sqlite3.OperationalError as e:
        exit("#[ERROR in %s] SQLite OperationalError: %s" % (config["query"], str(e)))


def purge_organism(config, c):
    '''Removes everything in the SQLite3 database connected to a organism.'''
    db_name = get_organism(config, c)
    if raw_input("Delete everything concerning %s? (Y/N) " % db_name).lower()[0] == "y":
        c.execute("DROP TABLE %s" % db_name)
        c.execute("DELETE FROM Sequences WHERE Organism = ?", (db_name, ))
        c.execute("DELETE FROM Tree WHERE Organism = ?", (db_name, ))
    else:
        exit("#Nothing happened, promise.")


def import_sequence(file_name, config, c):
    '''Loads a fasta file into the SQLite3 database.

    Keyword arguments:
    file_name -- the file name of the fasta file

    The file is checked for non-ATGCN characters and
    the database is also checked for a sequence for
    the same strain. If there is one the user is asked
    whether or not to update the sequence entry.

    '''
    print(file_name)
    seq_file = open(file_name, "r")
    seq = "".join(seq_file.read().split("\n")[1:])
    seq_file.close()

    # Going to search for ATCGN and see if that is all we find
    sequence_validation_regex = re.compile("[ATCGN]+")
    validation_search = sequence_validation_regex.search(seq)
    if validation_search.start() != 0 or validation_search.end() != len(seq):
        message = "#[ERROR in %s] You have a non-ATCGN character in your sequence file at position  % d" % (config["query"], validation_search.end() + 1)
        exit(message)

    organism_name = get_organism(config, c)
    strain_name = get_strain(organism_name, config, c)

    # Checking for entries with this strain name
    c.execute("SELECT DISTINCT Organism, Strain FROM Sequences")
    flag = True
    for row in c.fetchall():
        if strain_name == row[1] and organism_name == row[0]:  # If an entry was found, set our flag to false
            flag = False
    if flag:  # No entry for this strain name
        c.execute("INSERT INTO Sequences VALUES(?,?,?)", (organism_name, strain_name, seq))
    else:  # There was an entry for this strain name, ask for update
        print("This strain name already has a sequence listed in the database. Update entry? (Y/N)")
        while True:
            answer = raw_input()
            if answer[0].lower() == "n":  # Dont do anything if user doesnt want update
                break
            elif answer[0].lower() == "y":  # Update Sequences
                c.execute("UPDATE Sequences SET Sequence = ? WHERE Organism = ? AND Strain = ?",
                          (seq, organism_name, strain_name))
                break
            elif answer.lower().strip() == "exit":
                exit("Exiting...")


def import_to_db(file_name, config, c):
    '''Imports a textfile of SNP information into the SQLite3 database.
    Lines beginning with # are considered comment lines.

    Keyword arguments:
    file_name -- the file name of the file containing the SNP info

    Format of the file:
    #SNP-name\tOrganism-name\tReference\tStrain\tPosition\tDerived-base\tAncestral-base
    B.1\tFrancisella\tSvensson\tLVS\t23942\tA\tG

    Organism-name isnt used at the moment, the table name is the organism name.

    '''
    db_name = get_organism(config, c)

    snp_file = open(file_name, "r")

    queries = []
    for line in snp_file.readlines():
        if line != "" and line[0] != "#":
            line = line.strip()
            values = line.split("\t")
            unicode_values = list()
            for value in values:
                unicode_values.append(unicode(value.strip(), encoding="utf8"))
            snpname = unicode_values[0]
            c.execute("SELECT SNP from %s WHERE SNP=?" % db_name, (snpname,))
            if c.fetchone():
                if len(unicode_values) == 7:
                    c.execute("UPDATE %s SET Reference = ?, Strain = ?, Position = ?, Derived_base = ?, Ancestral_base = ? WHERE SNP = ?" % db_name,
                              (unicode_values[2], unicode_values[3], int(unicode_values[4]),
                               unicode_values[5], unicode_values[6], snpname))
            else:
                if len(unicode_values) == 7:
                    queries.append((snpname, unicode_values[2], unicode_values[3],
                                   int(unicode_values[4]), unicode_values[5], unicode_values[6]))
                else:  # Skip line if one of the pieces of information is missing
                    print("#Skipping:", values)
    c.executemany("INSERT INTO %s VALUES(?,?,?,?,?,?)" % db_name, queries)
    snp_file.close()


def import_tree(file_name, config, c):
    '''Imports a tree structure into the SQLite3 database

    Keyword arguments:
    file_name -- the file name of the txt file with the tree structure

    Format of the txt file:
    ROOT
    ROOT;N1
    ROOT;N2
    ROOT;N2;N3
    ROOT;N2;N4
    ROOT;N2;N5
    ROOT;N2;N5;N6

    The above structure represents this newick tree,
    however newick format can not be imported at this time:
    (N1,(N3,N4,(N6)N5)N2)ROOT;

    '''
    organism_name = get_organism(config, c)
    tree_file = open(file_name, "r")
    text_tree = tree_file.readlines()
    # Truncate the table
    c.execute("DELETE FROM Tree WHERE Organism = ?", (organism_name, ))
    tree_file.close()
    for line in text_tree:
        if line[0] != "#":
            nodes = line.strip().split(";")
            for i in range(0, len(nodes)):
                if nodes[i] != "":
                    c.execute("SELECT Name FROM Tree WHERE Name = ? AND Organism = ?", (nodes[i], organism_name))
                    if c.fetchone():
                        if len(nodes) > i + 1:  # Looking for children
                            c.execute("SELECT Children FROM Tree WHERE Name = ? and Organism = ?", (nodes[i], organism_name))
                            children = c.fetchone()[0]
                            if children:
                                child_list = children.split(";")
                                if nodes[i + 1] in child_list:
                                    pass  # Already listed as a child, skip
                                else:  # Append child
                                    new_children = ";".join(child_list) + ";" + nodes[i + 1]
                                    c.execute("UPDATE Tree SET Children = ? WHERE Name = ? AND Organism = ?",
                                              (new_children, nodes[i], organism_name))
                            else:
                                c.execute("UPDATE Tree SET Children = ? WHERE Name = ? AND Organism = ?",
                                          (nodes[i + 1], nodes[i], organism_name))
                    else:  # Add a node
                        if len(nodes) > i + 1 and nodes[i + 1] != "":  # First check if its got children
                            c.execute("INSERT INTO Tree VALUES(?,?,?)", (nodes[i], nodes[i + 1], organism_name))
                        else:
                            c.execute("INSERT INTO Tree VALUES(?,?,?)", (nodes[i], None, organism_name))


def tree_to_newick(organism, config, c):
    '''Returns a tree in the SQLite3 database in newick format

    Keyword arguments:
    organism -- the organism tree wanted

    Tries to convert the tree in the SQLite3 database into newick
    format. Does so by inserting the root and its children, after
    which each child is replaced by an entry containing itself and
    its children. Tries to go through all nodes 10000 times. This
    is because of the possibility of a node being listed before
    its parent. If after 10000 loops there are still nodes left,
    a warning is printed, but the resulting tree is still returned

    '''
    c.execute("SELECT * FROM Tree WHERE Organism = ?", (organism, ))
    nodes = c.fetchall()
    if config['dev']:
        print("#[DEV] Nodes in Tree that have %s as Organism" % organism)
        for node in nodes:
            print("#[DEV]", node)
    result = ''
    count = 0  # Counter to stop if it doesnt work properly
    while nodes and count < 10000:  # Run the loop a maximum of 10000 times
        for node in nodes:  # Go through all nodes
            search_regex = re.compile("[(|,]" + node[0] + "[,|)]")
            search_hit = search_regex.search(result)
            if search_hit:  # If the node is part of result, replace that entry with the same node and its children
                if node[1]:
                    result = result[:search_hit.start() + 1] + \
                        "(%s)%s" % (node[1].replace(";", ","), node[0]) + \
                        result[search_hit.end() - 1:]
                    nodes.remove(node)
                else:
                    nodes.remove(node)  # Just remove the node from the list if it doesnt have children
            elif result == '':  # If result is empty, just add the node. This is the root!
                if node[1]:
                    result += "(%s)%s;" % (node[1].replace(";", ","), node[0])
                    nodes.remove(node)
                else:
                    result += "%s;" % node[0]
                    nodes.remove(node)
        count += 1
    if count > 9999:  # Could not insert all nodes into the tree
        stderr.write("#[WARNING in %s] Broken tree, cannot convert entire tree to newick format. " % config["query"] +
                     "Most likely reason is a non-root node not listed as a child anywhere in the tree\n")
        if config["dev"]:
            print("#[DEV] These nodes were left out of the tree: %s" % str(nodes))
    if config["dev"]:
        print("#[DEV] Tree in newick format:%s" % result)
    return result


def CanSNPer_tree_layout(node):
    '''Layout style for ETE2 trees.'''
    name_face = AttrFace("name")
    # Adds the name face to the image at the top side of the branch
    faces.add_face_to_node(name_face, node, column=0, position="branch-top")


def draw_ete2_tree(organism, snplist, tree_file_name, config, c):
    '''Draws a phylogenetic tree using ETE2

    Keyword arguments:
    organism -- the organism of which to make a tree
    snplist -- a list of the SNP names, positions and state
    file_name -- the name of the out-file _tree.pdf will be added

    '''
    newick = tree_to_newick(organism, config, c)
    tree = Tree(newick, format=1)
    tree_depth = int(tree.get_distance(tree.get_farthest_leaf()[0]))
    for n in tree.traverse():
        # Nodes are set to red colour
        nstyle = NodeStyle()
        nstyle["fgcolor"] = "#BE0508"
        nstyle["size"] = 10
        nstyle["vt_line_color"] = "#000000"
        nstyle["hz_line_color"] = "#000000"
        nstyle["vt_line_type"] = 0
        nstyle["hz_line_type"] = 0
        nstyle["vt_line_width"] = 2
        nstyle["hz_line_width"] = 2
        for snp in snplist:
            if n.name == snp[0]:
                if snp[1] == snp[3]:
                    # If the SNP is Derived in snplist,
                    # change appearance of node
                    nstyle["fgcolor"] = "#99FF66"
                    nstyle["size"] = 15
                    nstyle["vt_line_color"] = "#000000"
                    nstyle["hz_line_color"] = "#000000"
                    nstyle["vt_line_type"] = 0
                    nstyle["hz_line_type"] = 0
                elif snp[3] == "-":
                    # If the SNP is missing due to a gap, make it grey
                    nstyle["fgcolor"] = "#DDDDDD"
                    nstyle["size"] = 10
                    nstyle["vt_line_color"] = "#DDDDDD"
                    nstyle["hz_line_color"] = "#DDDDDD"
                    nstyle["vt_line_type"] = 1
                    nstyle["hz_line_type"] = 1
        n.set_style(nstyle)
    ts = TreeStyle()
    ts.show_leaf_name = False  # Do not print(leaf names, they are added in layout)
    ts.show_scale = False  # Do not show the scale
    ts.layout_fn = CanSNPer_tree_layout  # Use the custom layout
    ts.optimal_scale_level = 'full'  # Fully expand the branches of the tree
    if config["dev"]:
        print("#[DEV] Tree file: %s" % tree_file_name)
    tree.render(tree_file_name, tree_style=ts, w=tree_depth * 500)


def find_tree_root(db_name, c, config):
    '''Returns the root of a tree.

    Keyword arguments:
    db_name -- the name of the organism from which we are grabbing the tree

    Definition of root:
    Is not listed as a child anywhere in the entire tree.

    If there are several nodes that arent listed as a child,
    the first one listed in the SQLite3 database is returned.

    '''
    root = None
    c.execute("SELECT * FROM Tree WHERE Organism = ?", (db_name,))
    nodes = c.fetchall()
    for node in nodes:
        flag = True
        for node_two in nodes:
            if node_two[1]:
                if node[0] in node_two[1].split(";"):
                    flag = False
                    break  # Break out if the node is listed as a child somewhere
        if flag:  # If the node was never listed as a child
            root = node[0]  # Set it as root
            break
    if config["dev"]:  # Developer printout
        print("#[DEV] root %s tree: %s" % (db_name, root))
    if not root:
        exit("#[ERROR in %s] Could not find root of %s tree" % (config["query"], db_name))
    return root


def snp_lister(sequences, organism, out_name, config, c):
    '''Returns a list of all SNPs, their positions and state in the sequence.

    Keyword arguments:
    sequences -- a list of all the query sequences, aligned to each reference
    organism -- the name of the organism
    out_name -- the name of the query

    '''
    c.execute("SELECT Strain, Position, Derived_base, Ancestral_base, SNP FROM %s" % organism)
    results = list()
    results.append(["#SNP", "Derived", "Ancestral", out_name])
    for snp in c.fetchall():
        try:  # Catch a KeyError that arises when a sequence is missing from the DB
            results.append([snp[4], snp[2], snp[3], sequences[snp[0]][snp[1] - 1]])
        except KeyError as e:
            message = "#[ERROR in %s] SNP position of %s listed in strain that is not in the database: %s" % (config["query"], snp[4], str(e.message))
            exit(message)
    return results


def multi_tree_walker(node, sequences, organism, threshold, wrong_list, config, c, force_flag=False, quiet=False):
    '''Tree walking classifier for CanSNPer.

    Keyword arguments:
    node -- The current node in the tree.
    sequences -- The aligned sequences of the query. A list, one for each reference strain
    organism -- The name of the organism
    threshold -- Number of ancestral SNPs to allow in the classification
    wrong_list -- A list of the positions that have been wrong, ie ancestral SNP
        config -- Dictionary containing running arguments for CanSNPer
    force_flag -- Boolean, flag for whether or not to force through current node
                 even if the sequence does not have the derived SNP
    quiet -- Boolean, if the function is run in a quiet mode, i.e. as a test
             this mode is run by the algorithm itself when "looking" deeper into the tree

    Walks through a tree, descending to the children of the node only if a quiet
    test of the next node has been completed.

    '''
    qstring = ""
    fstring = ""
    if quiet:
        qstring = "quiet"
    else:
        qstring = "not quiet"
    if force_flag:
        fstring = "Forcing"
    else:
        fstring = "Walking"
    if config["dev"]:
        print("#[DEV]", fstring, "into", node, qstring)
    c.execute("SELECT Strain, Position, Derived_base FROM %s WHERE SNP = ?" % organism, (node,))
    snp_info = c.fetchone()
    if snp_info:
        try:  # Catch a KeyError that arises when a sequence is missing from the DB
            if sequences[snp_info[0]][snp_info[1] - 1] == snp_info[2] or force_flag:
                # If its wrong and we are forcing
                if sequences[snp_info[0]][snp_info[1] - 1] != snp_info[2]:
                    if node not in wrong_list:
                        wrong_list.append(node)
                if quiet and not force_flag:
                    # Return True if we are quietly testing a single node
                    # and we are not forcing it
                    return True, True
                c.execute("SELECT Children FROM Tree WHERE Name = ? AND Organism = ?", (node, organism))
                children = c.fetchone()[0]

                if not children:  # No children, Leaf node.
                    #  Hit a leaf that is not derived
                    if sequences[snp_info[0]][snp_info[1] - 1] != snp_info[2]:
                        if config["dev"] and not quiet:
                            print("#[DEV] %s was not derived" % node)
                        wrong_list.remove(node)
                        return None, wrong_list
                    else:  # Hit a leaf that is derived
                        if config["dev"] and not quiet:
                            print("#[DEV] %s was a derived leaf. We are done here." % node)
                        return node, wrong_list

                # Has children, loop through them
                for child in children.split(";"):
                    if config["dev"] and not quiet:  # Developer printout
                        print("#[DEV] testing child: %s" % child)
                    # Test the SNP of child
                    if multi_tree_walker(child, sequences, organism, threshold, wrong_list, config, c, False, True)[0]:
                        # Move further down the Tree if it worked
                        if config["dev"] and not quiet:
                            print("#[DEV] testing child success, going into: %s" % child)
                        return multi_tree_walker(child, sequences, organism, threshold, wrong_list, config, c, False, quiet)
                if config["dev"] and not quiet:
                    print("#[DEV] Number of forced SNPs: %s, Threshold: %s, %s" % (len(wrong_list), threshold, str(wrong_list)))
                if len(wrong_list) >= threshold:
                    # Return node if we passed the threshold
                    if not quiet and sequences[snp_info[0]][snp_info[1] - 1] == snp_info[2]:
                        return node, wrong_list
                    else:
                        wrong_list.remove(node)
                        return None, wrong_list

                if config["dev"] and not quiet:  # Developer printout
                    print("#[DEV] Now going to try to force %s" % children)
                for child in children.split(";"):  # loop again if there were no results without force
                    if config["dev"] and not quiet:
                            print("#[DEV] force-testing child: %s" % child)
                    # Test forcing the SNP of child
                    if multi_tree_walker(child, sequences, organism, threshold, wrong_list, config, c, True, True)[0]:
                        # Move further down the Tree if it worked
                        return multi_tree_walker(child, sequences, organism, threshold, wrong_list, config, c, True, quiet)

                if sequences[snp_info[0]][snp_info[1] - 1] == snp_info[2]:
                    return node, wrong_list  # Return node if we didnt find anything by forcing
                else:
                    wrong_list.remove(node)  # Return None if we failed while "looking" quietly
                    return None, wrong_list
        except KeyError as e:
            message = "#[ERROR in %s] SNP position of %s listed in strain that is not in the database: %s" % (config["query"], node, str(e.message))
            exit(message)
    else:
        stderr.write("#[WARNING in %s] SNP not in database: %s\n" % (config["query"], node))
    if config["dev"]:  # Developer printout
        print("#[DEV] %s was not derived" % node)
    # if not quiet and force_flag:
    if node in wrong_list:
        wrong_list.remove(node)
    return None, wrong_list


def x2fa_error_check(num, config):
    '''Function that checks for errors in x2fa.py runs.

    Keyword arguments:
    num -- the uuid for this specific x2fa run

    '''
    # This file contains the stderr output from progressiveMauve
    x2fa_errors_file = open("%s/CanSNPer_xerr%s.txt" % (config["tmp_path"], num), "r")
    x2fa_errors = x2fa_errors_file.read()
    x2fa_errors_file.close()

    if x2fa_errors:  # Quit if there was something wrong
        exit("#[ERROR in %s] x2fa.py failed to complete:\n%s" % (config["query"], x2fa_errors))

    # Remove the file if there were no errors, annoying to have an empty file lying around
    silent_remove("%s/CanSNPer_xerr%s.txt" % (config["tmp_path"], num))


def mauve_error_check(num, config):
    '''Function that checks for errors in progressiveMauve runs.

    Keyword arguments:
    num -- the uuid for this specific progressiveMauve run

    '''
    # This file contains the stderr output from progressiveMauve
    mauve_errors_file = open("%s/CanSNPer_err%s.txt" % (config["tmp_path"], num), "r")
    mauve_errors = mauve_errors_file.read()
    mauve_errors_file.close()

    if mauve_errors:  # Quit if there was something wrong
        exit("#[ERROR in %s] progressiveMauve filed to complete:\n%s" % (config["query"], mauve_errors))

    # Remove the file if there were no errors, annoying to have an empty file lying around
    silent_remove("%s/CanSNPer_err%s.txt" % (config["tmp_path"], num))


def align(file_name, config, c):
    '''This function is the "main" of the classifier part of the program.

    Keyword arguments:
    file_name -- the name of the fasta file that is to be typed

    Sets everything in motion and retrieves and distributes all the results.

    '''
    # Set warning flags
    WARNINGS = dict()

    # Get database and output name
    db_name = get_organism(config, c)
    out_name = file_name.split("/")[-1]
    output = "%s/%s.CanSNPer" % (config["tmp_path"], out_name)

    # Get the sequences from our SQLite3 database, and write them
    # to tmp files that progressiveMauve can read
    c.execute("SELECT Organism, Strain, Sequence FROM Sequences WHERE Organism = ?", (db_name,))
    seq_counter = 0  # Counter for the number of sequences
    seq_uids = dict()

    reference_sequences = dict()

    if config["verbose"]:
        print("#Fetching reference sequence(s) ...")
    for row in c.fetchall():
        seq_counter += 1
        # 32 char long unique hex string used for unique tmp file names
        seq_uids[seq_counter] = uuid4().hex
        reference_sequences[seq_counter] = row[1]  # save the name of the references
        if not path.exists(config["tmp_path"]):
            makedirs(config["tmp_path"])
        tmp_file = open("%s/CanSNPer_reference_sequence." % config["tmp_path"] +
                        seq_uids[seq_counter] +
                        ".fa", "w")  # Open a tmp file
        tmp_file.write(">%s.%s\n%s\n" % (row[0], row[1], row[2]))  # Write to tmp file
        tmp_file.close()

    # Check if the file exists
    if not path.isfile(file_name):
        exit("#[ERROR in %s] No such file: %s" % (config["query"], file_name))

    # Parallelised running of several progressiveMauve processes
    if config["num_threads"] == 0 or config["num_threads"] > seq_counter:
        max_threads = seq_counter
    else:
        max_threads = config["num_threads"]

    if config["verbose"]:
        print("#Aligning sequence against %i reference sequence(s) ..." % len(reference_sequences))

    processes = list()
    mauve_jobs = list()
    x2f_jobs = list()
    for i in range(1, seq_counter + 1):
        if config["save_align"]:
            fasta_name = reference_sequences[i]
        else:
            fasta_name = seq_uids[i]

        # Write the commands that will be run. one for each reference sequence
        mauve_jobs.append("%s --output=%s.%s.xmfa " % (config["mauve_path"], output, seq_uids[i]) +
                          "%s/CanSNPer_reference_sequence.%s.fa %s > " % (config["tmp_path"],
                                                                          seq_uids[i], file_name) +
                          "/dev/null 2> %s/CanSNPer_err%s.txt" % (config["tmp_path"], seq_uids[i]))

        x2f_jobs.append("%s %s.%s.xmfa %s/CanSNPer_reference_sequence.%s.fa " % (config["x2fa_path"],
                        output, seq_uids[i], config["tmp_path"], seq_uids[i]) +
                        "0 %s.%s.fa 2> %s/CanSNPer_xerr%s.txt" % (output, fasta_name,
                                                                  config["tmp_path"], seq_uids[i]))

    # Starting the processes that use progressiveMauve to align sequences
    while True:
        while mauve_jobs and len(processes) < max_threads:
            job = mauve_jobs.pop()
            processes.append(Popen(job, shell=True))
            if config["dev"]:
                print("#[DEV] progressiveMauve command: %s" % job)
        for p in processes:
            if p.poll() is not None:
                processes.remove(p)
        if not processes and not mauve_jobs:
            break
        time.sleep(0.5)
    for uid in seq_uids:  # Errorcheck mauve, cant continue if it crashed
        mauve_error_check(seq_uids[uid], config)
    while True:
        while x2f_jobs and len(processes) < max_threads:
            job = x2f_jobs.pop()
            processes.append(Popen(job, shell=True))
            if config["dev"]:
                print("#[DEV] x2fa.py command: %s" % job)
        for p in processes:
            if p.poll() is not None:
                processes.remove(p)
        if not processes and not x2f_jobs:
            break
        time.sleep(0.5)
    for uid in seq_uids:  # Errorcheck x2fa.py
        x2fa_error_check(seq_uids[uid], config)

    # Now we have aligned sequences, read them into memory and
    # start working through the tree
    alternates = dict()
    for i in range(1, seq_counter + 1):
        if config["save_align"]:
            fasta_name = reference_sequences[i]
        else:
            fasta_name = seq_uids[i]
        fasta_name_readable = reference_sequences[i]
        alignment_file = open("%s.%s.fa" % (output, fasta_name), "r")
        sequences = alignment_file.read().split(">")[1:]
        alignment_file.close()
        reference = "".join(sequences[0].split("\n")[1:])
        alternate = "".join(sequences[1].split("\n")[1:])
        alternates[reference_sequences[i]] = alternate
        identity_counter = 0
        for j in range(0, len(reference)):
            if reference[j] == alternate[j]:
                identity_counter += 1
        if config["verbose"]:
            print("#Seq identity with %s: %.2f%s" % (fasta_name_readable, float(identity_counter) /
                  float(len(reference)) * 100, "%"))
        if float(identity_counter) / float(len(reference)) < 0.8:
            WARNINGS["ALIGNMENT_WARNING"] = "#[WARNING in %s] Sequence identity between %s and a reference strain of" % (config["query"], out_name) +\
                " %s was only %.2f percent" % (db_name, float(identity_counter) / float(len(reference)) * 100)

    root = find_tree_root(db_name, c, config)  # Find the root of the tree we are using
    if config["verbose"]:
        print("#Using tree root:", root)

    if config["allow_differences"]:  # Check whether or not to force the first tree node
        force_flag = True
    else:
        force_flag = False

    if config["list_snps"]:  # Make a raw list of which SNPs the sequence has
        snp_out_file = open("%s_snplist.txt" % file_name, "w")
        snplist = snp_lister(alternates, db_name, out_name, config, c)
        for snp in snplist:
            snp_out_file.write("\t".join(snp) + "\n")
        snp_out_file.close()

    if config["draw_tree"]:  # Draw a tree and mark positions
        snplist = snp_lister(alternates, db_name, out_name, config, c)
        if config["galaxy"]:
            tree_file_name = getcwd() + "/CanSNPer_tree_galaxy.pdf"
        else:
            tree_file_name = "%s_tree.pdf" % file_name
        draw_ete2_tree(db_name, snplist[1:], tree_file_name, config, c)
    # Tree walker!
    tree_location = multi_tree_walker(root, alternates, db_name, config["allow_differences"],
                                      list(), config, c, force_flag)

    # print(the results of our walk)
    if config["tab_sep"]:
        print("%s\t%s" % (out_name, tree_location[0]))
    else:
        print("Classification of %s: %s" % (out_name, tree_location[0]))

    if tree_location[1]:
        incorrect_snps = ""
        for incorrect_snp in tree_location[1]:
            incorrect_snps += str(incorrect_snp) + " "
        WARNINGS["TREE_WARNING"] = "#[WARNING in %s] these SNPs were not in the derived state: %s" % (config["query"], str(incorrect_snps))
        if config["verbose"]:
            print("#A forced tree walk was conducted")

    try:  # print(any warnings that may have been collected)
        stderr.write(str(WARNINGS["ALIGNMENT_WARNING"]) + "\n")
    except KeyError:
        pass
    try:
        stderr.write(str(WARNINGS["TREE_WARNING"]) + "\n")
    except KeyError:
        pass

    # Remove a bunch of tmp files
    while seq_counter:
        if config["save_align"]:
            destination = getcwd()
            srcfile = "%s.%s.fa" % (output, reference_sequences[seq_counter])
            shutil_copy(srcfile, destination)
            silent_remove("%s.%s.fa" % (output, reference_sequences[seq_counter]))
        silent_remove("%s.%s.fa" % (output, seq_uids[seq_counter]))
        silent_remove("%s/CanSNPer_reference_sequence.%s.fa" % (config["tmp_path"],
                      seq_uids[seq_counter]))
        silent_remove("%s/CanSNPer_reference_sequence.%s.fa.sslist" % (config["tmp_path"],
                      seq_uids[seq_counter]))
        silent_remove("%s.sslist" % (file_name))
        silent_remove("%s.%s.xmfa" % (output, seq_uids[seq_counter]))
        silent_remove("%s.%s.xmfa.bbcols" % (output, seq_uids[seq_counter]))
        silent_remove("%s.%s.xmfa.backbone" % (output, seq_uids[seq_counter]))
        seq_counter -= 1


def main():
    config = parse_arguments()
    
    db_open = False
    # Open sqlite3 connection
    if config["db_path"] is not None:
        if not path.isfile(config["db_path"]):
            print("Trying to create new database at %s" % config["db_path"])
        try:
            cnx = sqlite3.connect(config["db_path"])
            c = cnx.cursor()
            db_open = True
        except sqlite3.OperationalError as e:
            exit("#[ERROR in %s] Could not open database at %s:\n%s" % (config["query"],
                 config["db_path"], str(e)))

    # Check that the db is available before running
    if db_open:
        # Run the apropriate functions
        if config["initialise_organism"]:
            initialise_table(config, c)

        if config["import_snp_file"]:
            import_to_db(config["import_snp_file"], config, c)

        if config["import_tree_file"]:
            import_tree(config["import_tree_file"], config, c)

        if config["import_seq_file"]:
            import_sequence(config["import_seq_file"], config, c)

        if config["query"]:
            if config["verbose"]:
                print("#Starting %s ..." % config["query"])
            align(config["query"], config, c)

        if config["delete_organism"]:
            purge_organism(config, c)
    else:
        exit("#[ERROR] Did not find any open database connection")
    
    # If the database is been open, close it
    if db_open:
        cnx.commit()
        c.close()
        cnx.close()

if __name__ == '__main__':
    main()
