#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
x2fa.py: A small script for converting XMFA files to FASTA format.
Copyright (C) 2013 Adrian Lärkeryd

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
#Apologies for the perl-esque way of coding.
#I updated a perl script and tried to copy it line for line.
#VERSION 9
#Updates for v9:
#Changed the way screening of flanks is done. Fixed a bug where it sometimes messed
#the length of the alignment up.
#Updates for v8:
#Saves strings in the form of bytearrays. The immutability of python strings
#make the process of changing strings inefficient (which is how this implementation works).
#Using the bytearrays, the program runs a lot faster, especially when screening deletion flanks.
import re
import os
import sys
from string import maketrans

def reverse_complement(dna):
	'''Complement and reverse DNA string'''
	complements = maketrans('acgtrymkbdhvACGTRYMKBDHV', 'tgcayrkmvhdbTGCAYRKMVHDB')
	return dna.translate(complements)[::-1]

if __name__ == "__main__":
	'''Run the program'''
	if len(sys.argv) != 5:
		#Usage information
		exit("usage: x2fas_v6.py <.xmfa> <reference> <screen deletions by X bases> <outfile>")

	#Self-explanatory grabbing of command-line arguments
	xmfa = open(sys.argv[1], "r")
	outfile = open(sys.argv[4], "w")
	reference_name = sys.argv[2]
	flank = int(sys.argv[3])
	
	#Counters and other single variable initiations
	alignment_number = 0 #Keeps track of the alignment
	curr_seq = None #Keeps track of which sequence is active when reading xmfa
	curr_pos = None #Keeps track of which position in the sequence we are at when reading xmfa

	#Regex patterns
	pattern_start_of_seq = re.compile("^>\s*(\d+):(\d+)-(\d+) ([+-])") #Finds the start of sequence in xmfa
	pattern_seq_name = re.compile("#Sequence(\d+)File") #Finds comment line that contains sequence name in xmfa
	pattern_comment = re.compile("#") #Finds comment in xmfa
	pattern_gap = re.compile("-+") #Finds a gap of any size!

	#Dictionaries
	aGen = dict() #This is the dictionary that will contain all alignment fragments
	outseqs = dict() #Will eventually be filled with finalised sequences
	rmH = dict() #Will contain information on things that are going to be removed
	name2num = dict() #Conversion dictionaries
	num2name = dict() #Conversion dictionaries
	aGen[alignment_number] = dict()
	rmH[alignment_number] = dict()
	for line in xmfa:
		if pattern_start_of_seq.search(line):
			#This line contains information on the aligned sequence, add it to aGen
			
			curr_seq = int(line.split(":")[0].split(" ")[1])
			curr_pos = 0
			aGen[alignment_number][curr_seq] = dict()
		
			#Get the start and end position of the alignment
			startend = line.split(" ")[1].split(":")[1].split("-")
			startend[0] = int(startend[0])
			startend[1] = int(startend[1])
			if startend[0] < startend[1]:
				aGen[alignment_number][curr_seq]["p1"] = startend[0]
				aGen[alignment_number][curr_seq]["p2"] = startend[1]
			else:
				aGen[alignment_number][curr_seq]["p1"] = startend[1]
				aGen[alignment_number][curr_seq]["p2"] = startend[0]
			aGen[alignment_number][curr_seq]["sign"] = line.split(" ")[2]
			
			#Save the alignment as a bytearray.
			aGen[alignment_number][curr_seq]["seq"] = bytearray(" "*(aGen[alignment_number][curr_seq]["p2"]-aGen[alignment_number][curr_seq]["p1"]), encoding="utf8")
		elif line.strip() == "=":
			# = marks the start of a new alignment block
			alignment_number += 1
			aGen[alignment_number] = dict()
			rmH[alignment_number] = dict()
		elif pattern_seq_name.search(line):
			#If its a sequence name comment line, add information to name2num/num2name
			num = int(line.split("Sequence")[1].split("File")[0])
			name = line.split("\t")[1].strip()
			name2num[name] = num
			num2name[num] = name
		elif pattern_comment.search(line):
			#If its another type of comment line, dont do anything
			pass
		else:
			#The rest is only sequence, add it to the current seq at the current position
			length_of_line = len(line)-1
			aGen[alignment_number][curr_seq]["seq"][curr_pos:curr_pos+length_of_line] = line.strip().encode(encoding="utf8")
			curr_pos += length_of_line
	
	#Dont need this file open anymore
	xmfa.close()

	#Find out which of the sequences is the reference
	reference_num = name2num[reference_name]
	#Get the length of the reference sequence, the position of the "last" bit that is aligned
	length_of_reference = 0
	for alignment in aGen.keys():
		try: #Try to test this, but skip any errors, the reference is not in all alignments
			if aGen[alignment][reference_num]["p2"] > length_of_reference:
				length_of_reference = aGen[alignment][reference_num]["p2"]
		except KeyError as e:
			pass
	
	#Mock up the output sequences, fill them with only gaps
	for num in num2name.keys():
		#Handle the output sequences as bytearrays too!
		outseqs[num] = bytearray("-"*length_of_reference)

	for alignment in aGen.keys():
		keep_going_flag = False
		try: #Test if the reference is in the alignment
			tmp = aGen[alignment][reference_num]["seq"]
			keep_going_flag = True
		except KeyError as e: #Delete the alignment if it doesnt have the reference
			del aGen[alignment]
	
		if keep_going_flag: #If we have the reference
			search_pos = 0
			sequence_search_string = str(aGen[alignment][reference_num]["seq"])
			while search_pos < length_of_reference:
				gap_hit = pattern_gap.search(sequence_search_string, search_pos)
				if gap_hit: #Looking for gaps in the reference
					rmH[alignment][gap_hit.start()] = gap_hit.end()-gap_hit.start() #Save information
					search_pos = gap_hit.end()
				else:
					break	
			for pos in reversed(sorted(rmH[alignment].keys())): #Go through those gaps and remove them
				if rmH[alignment][pos]:
					start = pos
					end = pos + rmH[alignment][pos]
					for sequence in aGen[alignment].keys():
						if flank > 0:
							new_start = max(0, start-1)
							new_end = min(len(aGen[alignment][sequence]["seq"]), start+1)
							aGen[alignment][sequence]["seq"][new_start:new_end] = bytearray("-"*(new_end-new_start))
						aGen[alignment][sequence]["seq"] = aGen[alignment][sequence]["seq"][:start] + aGen[alignment][sequence]["seq"][end:]
			if flank > 0:
				list_of_gaps = list()
				for sequence in aGen[alignment].keys():
					if sequence == reference_num:
						continue
					sequence_search_string = str(aGen[alignment][sequence]["seq"])
					while search_pos < length_of_reference:
						gap_hit = pattern_gap.search(sequence_search_string, search_pos)
						if gap_hit: #Looking for gaps in the non-references
							list_of_gaps.append([gap_hit.start(), gap_hit.end()])
							search_pos = gap_hit.end()
						else:
							break
				for non_ref_gap in list_of_gaps:
					for sequence in aGen[alignment].keys():
						aGen[alignment][sequence]["seq"][non_ref_gap[0]:non_ref_gap[1]] = bytearray("-"*(non_ref_gap[1]-non_ref_gap[0]))
	#Go through all the alignment blocks and add the sequence to the output bytearrays
	for alignment in aGen.keys():
		start = int(aGen[alignment][reference_num]["p1"])-1
		end = int(aGen[alignment][reference_num]["p2"])
		if flank > 0:
			start += flank
			end -= flank
		if aGen[alignment][reference_num]["sign"] == "+":
			#Add sequence to outseqs
			for sequence in aGen[alignment].keys():
				if start >= 0 and end > 0 and aGen[alignment][sequence]["seq"]:
					if flank > 0:
						outseqs[sequence][start:end] = bytearray(str(aGen[alignment][sequence]["seq"][flank:-flank]), encoding="utf8")
					else:
						outseqs[sequence][start:end] = bytearray(str(aGen[alignment][sequence]["seq"]), encoding="utf8")
		else:
			#Add reverse complement to outseqs
			for sequence in aGen[alignment].keys():
				if start >= 0 and end > 0 and aGen[alignment][sequence]["seq"]:
					if flank > 0:
						outseqs[sequence][start:end] = bytearray(reverse_complement(str(aGen[alignment][sequence]["seq"][flank:-flank])), encoding="utf8")
					else:
						outseqs[sequence][start:end] = bytearray(reverse_complement(str(aGen[alignment][sequence]["seq"])), encoding="utf8")
	
	#First, write the reference sequence
	outfile.write(">"+num2name[reference_num]+"\n")
	seqpos = 0
	#80 characters at a time
	while seqpos < len(outseqs[reference_num]):
		outfile.write(str(outseqs[reference_num][seqpos:seqpos+80])+"\n")
		seqpos += 80

	#Then, write the rest
	for sequence in outseqs.keys():
		if sequence != reference_num:
			outfile.write(">"+num2name[sequence]+"\n")
			seqpos = 0
			while seqpos < len(outseqs[sequence]):
				outfile.write(str(outseqs[sequence][seqpos:seqpos+80])+"\n")
				seqpos += 80
	outfile.close()
