import sys
import pandas as pd
from Bio import SeqIO

fasta_file = sys.argv[1]
hmmsearch_output = sys.argv[2]

sequence_dictionary = SeqIO.index(fasta_file, "fasta")
hmmsearch_table = pd.read_csv(hmmsearch_output, delimiter="\t")

protein_sequence_list = hmmsearch_table['protein'].tolist()

sequence_record_list = []

for protein in protein_sequence_list:
    sequence_record_list.append(sequence_dictionary[protein])

output_file = fasta_file.rsplit("/", 1)[0] + fasta_file.split("/")[-1].rsplit(".", 1) + "_hmm_profiles_seqs.faa"

SeqIO.write(sequence_record_list, output_file, "fasta")



