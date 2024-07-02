#! /usr/bin/env python3

import sys
import pandas
import subprocess

# Directions:
# hmmtbl_parser.py <input_hmmtbl> <method>
# for method sort by "score" or "evalue" (type in one of those options)
# This program works for scaffold names that were created with the addFileName2head.pl script


with open(str(sys.argv[1]), 'r') as infile:
    with open(str(sys.argv[1]).rsplit(".",1)[0]+'_full.tsv', 'w') as outfile:
        outfile.write("protein" + "\t" + "bin" + "\t" + "id" + "\t" + "evalue" + "\t" + "score" + '\n')
        for line in infile:
            check = False
            if not line.startswith('#'):
                line = line.split(' ')
                parse = list(filter(None, line))
                if parse != None:
                    temp = str(parse[0]).replace("~~","_").replace("~","_").split("_NODE")[0]
                    check = True
            if check == True:
                if str(parse[3]) == "-":
                    outfile.write(str(parse[0]) + '\t' + str(temp) + '\t' + str(parse[2]) + '\t' + str(parse[4]) + '\t' + str(parse[5]) + '\n')  #other (KEGG, TIGER)
                else:
                    outfile.write(str(parse[0]) + '\t' + str(temp) + '\t' + str(parse[3]) + '\t' + str(parse[4]) + '\t' + str(parse[5]) + '\n')   #pfam

with open(str(sys.argv[1]).rsplit(".",1)[0]+'_full.tsv', 'r') as sort:
    table = pandas.read_csv(sort, sep="\t")
    if sys.argv[2] == "evalue":
        sort = table.sort_values(by='evalue', ascending=True)
    if sys.argv[2] == "score":
        sort = table.sort_values(by='score', ascending=False)
    drop = sort.drop_duplicates(subset='bin', keep='first')
    drop.to_csv(str(sys.argv[1]).rsplit(".",1)[0]+'_parsed-hmmtbl.tsv', index=False, sep="\t")

intermediate_file = (sys.argv[1]).rsplit(".",1)[0]+'_full.tsv'

subprocess.run(["rm", intermediate_file])