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
                                                             
                                                             The sep argument is there for grouping results based on groups of excel output spreadsheets. For example, 
                                                             if there are two sample locations separated in different spreadsheets (ex. Location1_Day#.xlsx, Location2_Day#.xslx), 
                                                             the user would input 'Location1,Location2' for this argument. The text strings used must be present within the
                                                             output spreadsheets (it is also case-sensitive). If there is only one grouping, still include the name of the grouping
                                                             but without a comma.
                                                             
                                                             For the line argument, specify the row number of the header from the output readings in the raw
                                                             data document. For the default excel output from the i-control software, the first column of the
                                                             raw reads will be denoted with '<>'.
                                                             
                                                             The out argument specifies the directory where the output files will created'''),
                                 epilog="Written by Adam Breister, ambreist@ncsu.edu")

parser.add_argument('-p', '--path', help="Specify path to directory with plate reader output excel spreadsheets (default: './')", nargs=1, default="./")
parser.add_argument('-s', '--substrate', help="Specify path to text file with ordered list of substrates (A1,A2...B1,B2...H11,H12) with each substrate on separate line", nargs=1, required=True)
parser.add_argument('-l', '--line', help="Specify the row number that the header for the raw data table is (default: '30')", nargs=1, default=30, type=int)
parser.add_argument('-o', '--out', help="Specify directory where output files will be generated (default: './')", nargs=1, default="./", type=str)

args = parser.parse_args()

substrates = args.substrate[0]
start_line = args.line[0]

if args.path[0].endswith("/"):
    path_to_files = args.path[0]
else:
    path_to_files = args.path[0] + "/"

if args.out[0].endswith("/"):
    output_directory = args.out[0]
else:
    output_directory = args.out[0] + "/"

def read_input_spreadsheets(input_file,start):
    rows_to_skip = start - 1
    input_spreadsheet = pd.read_excel(input_file, skiprows=rows_to_skip, nrows=9, usecols="B:M", sheet_name=None)

    ecoplate_value_dict = {}

    for sample_names in input_spreadsheet.keys():
        if sample_names == "Sheet1":
            continue
        else:
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

list_of_substrates = ["Water","β-Methyl-D-Glucoside","D-Galactonic Acid γ-Lactone",
"L-Arginine",
"Water",
"β-Methyl-D-Glucoside",
"D-Galactonic Acid γ-Lactone",
"L-Arginine",
"Water",
"β-Methyl-D-Glucoside",
"D-Galactonic Acid γ-Lactone",
"L-Arginine",
"Pyruvic Acid Methyl Ester",
"D-Xylose",
"D-Galacturonic Acid",
"L-Asparagine",
"Pyruvic Acid Methyl Ester",
"D-Xylose",
"D-Galacturonic Acid",
"L-Asparagine",
"Pyruvic Acid Methyl Ester",
"D-Xylose",
"D-Galacturonic Acid",
"L-Asparagine",
"Tween 40",
"i-Erythritol",
"2-Hydroxy Benzoic Acid",
"L-Phenylalanine",
"Tween 40",
"i-Erythritol",
"2-Hydroxy Benzoic Acid",
"L-Phenylalanine",
"Tween 40",
"i-Erythritol",
"2-Hydroxy Benzoic Acid",
"L-Phenylalanine",
"Tween 80",
"D-Mannitol",
"4-Hydroxy Benzoic Acid",
"L-Serine",
"Tween 80",
"D-Mannitol",
"4-Hydroxy Benzoic Acid",
"L-Serine",
"Tween 80",
"D-Mannitol",
"4-Hydroxy Benzoic Acid",
"L-Serine",
"α-Cyclodextrin",
"N-Acetyl-D-Glucosamine",
"γ-Amino Butyric Acid ",
"L-Threonine",
"α-Cyclodextrin",
"N-Acetyl-D-Glucosamine",
"γ-Amino Butyric Acid ",
"L-Threonine",
"α-Cyclodextrin",
"N-Acetyl-D-Glucosamine",
"γ-Amino Butyric Acid ",
"L-Threonine",
"Glycogen",
"D-Glucosaminic Acid",
"Itaconic Acid",
"β-HydroxyGlycyl-L-Glutamic Acid",
"Glycogen",
"D-Glucosaminic Acid",
"Itaconic Acid",
"β-HydroxyGlycyl-L-Glutamic Acid",
"Glycogen",
"D-Glucosaminic Acid",
"Itaconic Acid",
"β-HydroxyGlycyl-L-Glutamic Acid",
"D-Cellobiose",
"Glucose1-Phosphate",
"α-Keto Butyric Acid",
"Phenylethylamine",
"D-Cellobiose",
"Glucose1-Phosphate",
"α-Keto Butyric Acid",
"Phenylethylamine",
"D-Cellobiose",
"Glucose1-Phosphate",
"α-Keto Butyric Acid",
"Phenylethylamine",
"α-D-Lactose",
"D,L-α-Glycerol Phosphate",
"D-Malic Acid",
"Putrescine",
"α-D-Lactose",
"D,L-α-Glycerol Phosphate",
"D-Malic Acid",
"Putrescine",
"α-D-Lactose",
"D,L-α-Glycerol Phosphate",
"D-Malic Acid",
"Putrescine"]

well_metadata_df = pd.DataFrame({"Well Name":well_ids, "Well Substrate":list_of_substrates})

with pd.ExcelWriter(output_directory + "Reordered_Ecoplate_Data.xlsx") as writer:
    for sheetname in full_reordered_data_dict.keys():
        values_dataframe = pd.DataFrame(full_reordered_data_dict[sheetname])
        metadata_values_dataframe = pd.concat([well_metadata_df, values_dataframe], axis=1)

        metadata_values_dataframe.to_excel(writer, sheet_name=sheetname, index=False)


def calculate_awcd(all_data_dict, metadata):
    combined_awcd = {}
    
    for sheetname_2 in all_data_dict.keys():
        only_values_dataframe = pd.DataFrame(all_data_dict[sheetname_2])
        ecoplate_data = pd.concat([metadata, only_values_dataframe], axis=1)

        ecoplate_data.drop("Well Name", axis=1, inplace=True)


        grouped_average_ecoplate_data = ecoplate_data.groupby("Well Substrate").mean()
        grouped_average_ecoplate_data.reset_index(inplace=True)


        water_index = grouped_average_ecoplate_data.loc[grouped_average_ecoplate_data["Well Substrate"]=="Water", :].index[0]
        water_absorbance_series = grouped_average_ecoplate_data.iloc[water_index]
        grouped_average_ecoplate_data.drop([water_index], inplace=True)
        new_water_absorbance_series = water_absorbance_series.drop(labels='Well Substrate')

        subtracted_all_absorbance = grouped_average_ecoplate_data.subtract(new_water_absorbance_series).drop(["Well Substrate"], axis=1)
        subtracted_all_absorbance[subtracted_all_absorbance < 0] = 0

        average_well_color_development = subtracted_all_absorbance.sum()/31
        average_well_color_development.name = sheetname_2.rsplit("_", 1)[0]

        combined_awcd[sheetname_2] = average_well_color_development

    return combined_awcd

awcd_dict = calculate_awcd(full_reordered_data_dict, well_metadata_df)


with pd.ExcelWriter(output_directory + "Ecoplate_Average_Well_Color_Development.xlsx") as writer_2:
    if "," in separator:
        for splits in separator.split(","):
            specific_series = pd.Series()
            for names in awcd_dict.keys():
                if splits in names:
                    specific_series = pd.concat([specific_series, awcd_dict[names]], axis=1)
            
            specific_series.drop(0, axis=1, inplace=True)

            specific_series.to_excel(writer_2, sheet_name=splits, index=True)
    else:
        specific_series = pd.Series()
        for names in awcd_dict.keys():
            if separator in names:
                specific_series = pd.concat([specific_series, awcd_dict[names]], axis=1)
            
        specific_series.drop(0, axis=1, inplace=True)

        specific_series.to_excel(writer_2, sheet_name=separator, index=True)