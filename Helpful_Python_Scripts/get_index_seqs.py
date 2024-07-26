import sys
from Bio.Seq import Seq
import argparse
import textwrap

parser = argparse.ArgumentParser(prog="get_index_seqs.py", 
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 description=textwrap.dedent('''\
                                                             Tool to extract index sequence from full length adapter sequences.
                                                             ------------------------------------------------------------------
                                                             This currently only applies to the Earth Microbiome Primers

                                                             16S primer is at position 32:44 in adapter 
                                                             ITS primer is at position 24:36 in adapter
                                                             18S primer is at position 24:36 in adapter
                                                             
                                                             *INPUT MUST BE TEXT FILES WITH ONE ADAPTER SEQUENCE PER LINE PER MARKER GENE TYPE*'''),
                                 epilog="Written by Adam Breister, ambreist@ncsu.edu")

parser.add_argument('-b', '--bact', help="Specify file path to list of 16S adapter sequences (515F-806R)", nargs=1, default=None)
parser.add_argument('-f', '--fun', help="Specify file path to list of ITS adapter sequences (ITS1f-ITS2)", nargs=1, default=None)
parser.add_argument('-e', '--euk', help="Specify file path to list of 18S adapter sequences (1391F-EukBr)", nargs=1, default=None)

args = parser.parse_args()

present_files = []
generated_files = []

if args.bact != None:
    present_files.append("16S")
    barcoded_16S_primers = args.bact[0]
    index_sequence_file_16S = barcoded_16S_primers.rsplit(".", 1)[0] + "_indexes.txt"
    with open(barcoded_16S_primers, "r") as input_16S, open(index_sequence_file_16S, "w") as output_16S:
        for line in input_16S:
            output_16S.write(line[32:44] + "\n")
        generated_files.append("16S")

if args.fun != None:
    present_files.append("ITS")
    barcoded_ITS_primers = args.fun[0]
    index_sequence_file_ITS = barcoded_ITS_primers.rsplit(".", 1)[0] + "_indexes.txt"
    with open(barcoded_ITS_primers, "r") as input_ITS, open(index_sequence_file_ITS, "w") as output_ITS:
        for line in input_ITS:
            ITS_index_seq = Seq(line[24:36])
            ITS_index_seq_rev_comp = ITS_index_seq.reverse_complement()
            output_ITS.write(str(ITS_index_seq_rev_comp) + "\n")
        generated_files.append("ITS")

if args.euk != None:
    present_files.append("18S")
    barcoded_18S_primers = args.euk[0]
    index_sequence_file_18S = barcoded_18S_primers.rsplit(".", 1)[0] + "_indexes.txt"
    with open(barcoded_18S_primers, "r") as input_18S, open(index_sequence_file_18S, "w") as output_18S:
        for line in input_18S:
            index_seq_18S = Seq(line[24:36])
            index_seq_18S_rev_comp = index_seq_18S.reverse_complement()
            output_18S.write(str(index_seq_18S_rev_comp) + "\n")
        generated_files.append("18S")



number = len(present_files)

if number == 3:
    print(str(present_files[0]) + ", " + str(present_files[1]) + ", and " + str(present_files[2]) + " primers were provided\n")
elif number == 2:
    print(str(present_files[0]) + " and " + str(present_files[1]) + " primers were provided\n")
elif number == 1:
    print(str(present_files[0]) + " primers were provided\n")


output = len(generated_files)

if output == 3:
    print(str(generated_files[0]) + ", " + str(generated_files[1]) + ", and " + str(generated_files[2]) + " indexes were generated")
elif output == 2:
    print(str(generated_files[0]) + " and " + str(generated_files[1]) + " indexes were generated")
elif output == 1:
    print(str(generated_files[0]) + " indexes were generated")