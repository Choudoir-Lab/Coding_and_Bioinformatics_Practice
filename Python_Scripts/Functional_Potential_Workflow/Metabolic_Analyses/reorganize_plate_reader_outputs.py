import pandas as pd
import sys
import os
import argparse
import textwrap

parser = argparse.ArgumentParser(prog="ecoplate_calculations.py", 
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 description=textwrap.dedent('''\
                                                             Tool to organize output data of Biolog EcoPlate readings from the Tecan i-control software.
                                                             -------------------------------------------------------------------------------------------
                                                             This tool currently only takes readings of one wavelength per sample.

                                                             The path specified must include all excel spreadsheet outputs from the Tecan i-control software.
                                                             
                                                             The sep argument is there for grouping results based on metadata. For example, if there are two 
                                                             sample locations, the argument would be 'Location1,Location2'. For this to work properly, this
                                                             text string must be within the filename of each output spreadsheet for that group (case-sensitive).
                                                             If there is only one grouping, still include the name of the grouping but with no comma.
                                                             
                                                             For the line argument, specify the row number of the header from the output readings in the raw
                                                             data document. For the default excel output from the i-control software, the first column of the
                                                             raw reads will be denoted with '<>'.
                                                             
                                                             The output files will appear in the same directory as this script is run from'''),
                                 epilog="Written by Adam Breister, ambreist@ncsu.edu")

parser.add_argument('-p', '--path', help="Specify path to directory with plate reader output excel spreadsheets (default: './')", nargs=1, default="./")
parser.add_argument('-s', '--substrate', help="Specify path to text file with ordered list of substrates (A1,A2...B1,B2...H11,H12) with each substrate on separate line", nargs=1, required=True)
parser.add_argument('-l', '--line', help="Specify the row number that the header for the raw data table is (default: '30')", nargs=1, default=30, type=int)

args = parser.parse_args()

path_to_files = args.path[0]
substrates = args.substrate[0]
start_line = args.line[0]


def read_input_spreadsheets(input_file,start):
    rows_to_skip = start - 1
    input_spreadsheet = pd.read_excel(input_file, skiprows=rows_to_skip, nrows=9, usecols="B:M", sheet_name=None)

    ecoplate_value_dict = {}

    for sample_names in input_spreadsheet.keys():
        list_of_rows_spreadsheet = input_spreadsheet[sample_names].values.tolist()

        flat_list = []

        for lists in list_of_rows_spreadsheet:
            for item in lists:
                flat_list.append(item)

        ecoplate_value_dict[sample_names] = flat_list

    return ecoplate_value_dict


directory_list = os.listdir(path_to_files)
full_reordered_data_dict = {}

print("Files Being Read:\n")
for filename in directory_list:
    if filename.endswith(".xlsx") and "~" not in filename:
        relative_path = path_to_files + filename
        print(relative_path)
        full_reordered_data_dict[filename.rsplit(".", 1)[0] + "_reordered"] = read_input_spreadsheets(relative_path, start_line)
print("\nDone Reading Files")

well_ids = []

for i in range(65,73):
    for n in range(1,13):
        well_ids.append(chr(i) + str(n))

list_of_substrates = []

with open(substrates, "r") as input:
    for line in input:
        list_of_substrates.append(line.strip())

well_metadata_df = pd.DataFrame({"Well Name":well_ids, "Well Substrate":list_of_substrates})

with pd.ExcelWriter("Reordered_Ecoplate_Data.xlsx") as writer:
    for sheetname in full_reordered_data_dict.keys():
        values_dataframe = pd.DataFrame(full_reordered_data_dict[sheetname])
        metadata_values_dataframe = pd.concat([well_metadata_df, values_dataframe], axis=1)

        metadata_values_dataframe.to_excel(writer, sheet_name=sheetname, index=False)