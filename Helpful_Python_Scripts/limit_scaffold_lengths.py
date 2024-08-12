from Bio import SeqIO
import argparse
import textwrap
import os

parser = argparse.ArgumentParser(prog="get_index_seqs.py", 
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 description=textwrap.dedent('''\
                                                             Tool to remove scaffolds with sequences less than a specified threshold.
                                                             ------------------------------------------------------------------------

                                                             Only scaffolds greater than or equal to the length specified will be kept.

                                                             When input is a directory, a table is generated with input filenames, 
                                                             initial number of scaffolds and the resulting number of scaffolds after
                                                             removal.
                                                            '''),
                                 epilog="Written by Adam Breister, ambreist@ncsu.edu")

parser.add_argument('-f', '--file', help="Specify file path to singular fasta file", nargs=1, default=None)
parser.add_argument('-d', '--dir', help="Specify file path to directory containing fasta files", nargs=1, default=None)
parser.add_argument('-l', '--length', help="Specify minimum length cutoff of scaffolds", nargs=1, default=None, metavar="LEN")

args = parser.parse_args()

def limit_length(input_file, output_file, length):
    input_scaffolds = 0
    output_scaffolds = 0
    with open(input_file, "r") as input, open(output_file, "w") as output:
        for record in SeqIO.parse(input, "fasta"):
            input_scaffolds += 1
            if len(record.seq) >= int(length):
                SeqIO.write(record, output, "fasta")
                output_scaffolds += 1
    return input_scaffolds, output_scaffolds


if args.file != None:
    filename = args.file[0]
    output_filename = filename.rsplit(".", 1)[0] + "_min_" + args.length[0] + "." + filename.rsplit(".", 1)[1]
    input_num_scaffolds, output_num_scaffolds = limit_length(filename, output_filename, args.length[0])
    print(filename + "  |  " + str(input_num_scaffolds) + " scaffolds")
    print(output_filename + "  |  " + str(output_num_scaffolds) + " scaffolds")


if args.dir != None:
    directory = os.listdir(args.dir[0])

    log_information_dict = {}
    
    for file in directory:
        filename = args.dir[0].rstrip("/") + "/" + file
        output_filename = filename.rsplit(".", 1)[0] + "_min_" + args.length[0] + "." + filename.rsplit(".", 1)[1]
        input_num_scaffolds, output_num_scaffolds = limit_length(filename, output_filename, args.length[0])

        log_information_dict[filename] = [input_num_scaffolds, output_num_scaffolds]


    with open(args.dir[0].rstrip("/") + "/" + "limit_scaffold_length_log.csv", "w") as log_file:
        log_file.write("Input FASTA File,Input Number of Scaffolds,Output Number of Scaffolds\n")
        for filename in log_information_dict.keys():
            log_file.write(str(filename) + "," + str(log_information_dict[filename][0]) + "," + str(log_information_dict[filename][1]) + "\n")


