import argparse
import textwrap
import os

parser = argparse.ArgumentParser(prog="get_index_seqs.py", 
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 description=textwrap.dedent('''\
                                                             Tool to add filename to contig/sequence header'''),
                                 epilog="Written by Adam Breister, ambreist@ncsu.edu")

parser.add_argument('-i', '--input', help="Path to directory containing genomes", nargs=1, default=None, metavar="IN")

args = parser.parse_args()


directory = os.listdir(args.input[0])

for file in directory:
    filename = file.rsplit(".", 1)[0]
    with open(args.input[0].rstrip("/") + "/" + file, "r") as input, open(args.input[0].rstrip("/") + "/" + filename + "_renamed." + file.rsplit(".", 1)[1], "w") as output:
        for line in input:
            if line.startswith(">"):
                new_line = ">" + filename + "_" + line.lstrip(">")
                output.write(new_line)
            else:
                output.write(line)