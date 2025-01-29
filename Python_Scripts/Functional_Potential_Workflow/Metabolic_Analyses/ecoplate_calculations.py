import pandas as pd
import sys
import os
import argparse
import textwrap
import numpy as np

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
parser.add_argument('-s', '--sep', help="Comma-separated list of strings that distinguish groupings in input spreadsheets", nargs=1, required=True)
parser.add_argument('-l', '--line', help="Specify the row number that the header for the raw data table is (default: '30')", nargs=1, default=30, type=int)
parser.add_argument('-o', '--out', help="Specify directory where output files will be generated (default: './')", nargs=1, default="./", type=str)
parser.add_argument('-r', '--rich', help="Corrected OD value threshold to identify utilized substrates (default: 0.15)", nargs=1, default=0.15, type=float)

args = parser.parse_args()

separator = args.sep[0]


if type(args.line) is not int:
    start_line = args.line[0]
else:
    start_line = args.line

if type(args.rich) is not float:
    threshold = args.rich[0]
else:
    threshold = args.rich

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

def get_average_absorbance_values(data_dict, metadata_table, sheet_name):
    
    only_values_dataframe = pd.DataFrame(data_dict[sheet_name])
    ecoplate_data = pd.concat([metadata_table, only_values_dataframe], axis=1)

    ecoplate_data.drop("Well Name", axis=1, inplace=True)


    grouped_average_ecoplate = ecoplate_data.groupby("Well Substrate").mean()
    grouped_average_ecoplate.reset_index(inplace=True)


    water_index = grouped_average_ecoplate.loc[grouped_average_ecoplate["Well Substrate"]=="Water", :].index[0]
    water_absorbance_series = grouped_average_ecoplate.iloc[water_index]
    grouped_average_ecoplate.drop([water_index], inplace=True)
    final_water_absorbance_series = water_absorbance_series.drop(labels='Well Substrate')

    return final_water_absorbance_series, grouped_average_ecoplate

def calculate_awcd(all_data_dict, metadata):
    combined_awcd = {}
    
    for sheetname_awcd in all_data_dict.keys():
        new_water_absorbance_series, grouped_average_ecoplate_data = get_average_absorbance_values(all_data_dict, metadata, sheetname_awcd)

        subtracted_all_absorbance = grouped_average_ecoplate_data.subtract(new_water_absorbance_series).drop(["Well Substrate"], axis=1)
        subtracted_all_absorbance[subtracted_all_absorbance < 0] = 0

        average_well_color_development = subtracted_all_absorbance.sum()/31
        average_well_color_development.name = sheetname_awcd.rsplit("_", 1)[0]
        combined_awcd[sheetname_awcd] = average_well_color_development

    return combined_awcd

def calculate_sawcd(all_data_dict, metadata, substrate_guilds_inv):
    combined_sawcd = {}
    
    for sheetname_sawcd in all_data_dict.keys():
        new_water_absorbance_series, grouped_average_ecoplate_data = get_average_absorbance_values(all_data_dict, metadata, sheetname_sawcd)

        grouped_average_ecoplate_data.set_index("Well Substrate", inplace=True)

        subtracted_all_absorbance = grouped_average_ecoplate_data.subtract(new_water_absorbance_series)
        subtracted_all_absorbance[subtracted_all_absorbance < 0] = 0

        subtracted_all_absorbance.reset_index(level=0, inplace=True)
        
        subtracted_all_absorbance["Substrate Guild"] = subtracted_all_absorbance["Well Substrate"].map(substrate_guilds_inv)
        subtracted_all_absorbance.drop(["Well Substrate"], axis=1, inplace=True)
        
        guild_average_ecoplate_data = subtracted_all_absorbance.groupby("Substrate Guild").mean()
        guild_average_ecoplate_data_transposed = guild_average_ecoplate_data.T


        combined_sawcd[sheetname_sawcd] = guild_average_ecoplate_data_transposed

    return combined_sawcd

def calculate_diversity(all_data_dict, metadata, cutoff):
    combined_shannon_div = {}
    combined_shannon_even = {}
    combined_substrate_richness = {}
    
    for sheetname_div in all_data_dict.keys():
        new_water_absorbance_series, grouped_average_ecoplate_data = get_average_absorbance_values(all_data_dict, metadata, sheetname_div)

        subtracted_all_absorbance = grouped_average_ecoplate_data.subtract(new_water_absorbance_series).drop(["Well Substrate"], axis=1)
        subtracted_all_absorbance[subtracted_all_absorbance < 0] = 0

        full_plate_total_corrected_absorbance = subtracted_all_absorbance.sum(axis=0)
        
        corrected_absorbance_fraction = subtracted_all_absorbance.div(full_plate_total_corrected_absorbance)

        def mapping_condition(x):
            if x==0:
                pass
            else:
                return np.log(x)


        natural_log_corrected_absorbance_fraction = corrected_absorbance_fraction.map(mapping_condition)
        
        
        mult_natural_log_corrected_absorbance_fraction = natural_log_corrected_absorbance_fraction.mul(corrected_absorbance_fraction)
        sum_mult_natural_log_corrected_absorbance_fraction = mult_natural_log_corrected_absorbance_fraction.sum()

        shannon_diversity = -(sum_mult_natural_log_corrected_absorbance_fraction)
        substrate_richness = subtracted_all_absorbance[subtracted_all_absorbance >= cutoff].count()
        natural_log_substrate_richness = substrate_richness.apply(mapping_condition)
        shannon_evenness = shannon_diversity / natural_log_substrate_richness

        shannon_evenness[shannon_evenness==np.inf] = np.nan

        shannon_diversity.name = sheetname_div.rsplit("_", 1)[0]
        shannon_evenness.name = sheetname_div.rsplit("_", 1)[0]
        substrate_richness.name = sheetname_div.rsplit("_", 1)[0]

        combined_shannon_div[sheetname_div] = shannon_diversity
        combined_shannon_even[sheetname_div] = shannon_evenness
        combined_substrate_richness[sheetname_div] = substrate_richness

    return combined_shannon_div, combined_shannon_even, combined_substrate_richness

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
"γ-Amino Butyric Acid",
"L-Threonine",
"α-Cyclodextrin",
"N-Acetyl-D-Glucosamine",
"γ-Amino Butyric Acid",
"L-Threonine",
"α-Cyclodextrin",
"N-Acetyl-D-Glucosamine",
"γ-Amino Butyric Acid",
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

substrate_guilds = {"Amino Acids": ["L-Arginine", "L-Asparagine", "L-Phenylalanine", "L-Serine", "β-HydroxyGlycyl-L-Glutamic Acid", "L-Threonine"], 
                    "Amines": ["Phenylethylamine", "Putrescine"], 
                    "Carbohydrates": ["D-Mannitol", "Glucose1-Phosphate", "D,L-α-Glycerol Phosphate", "β-Methyl-D-Glucoside", "D-Galactonic Acid γ-Lactone", 
                                      "i-Erythritol", "D-Xylose", "N-Acetyl-D-Glucosamine", "D-Cellobiose", "α-D-Lactose"], 
                    "Carboxylic Acids": ["D-Glucosaminic Acid", "D-Malic Acid", "Itaconic Acid", "Pyruvic Acid Methyl Ester", "D-Galacturonic Acid", "α-Keto Butyric Acid", 
                                         "γ-Amino Butyric Acid"], 
                    "Phenolic Compounds": ["2-Hydroxy Benzoic Acid", "4-Hydroxy Benzoic Acid"],
                    "Polymers": ["Tween 40", "Tween 80", "α-Cyclodextrin", "Glycogen"]}

inverted_substrate_guilds = {}
for guilds in substrate_guilds.keys():
    for substrate in substrate_guilds[guilds]:
        inverted_substrate_guilds[substrate] = guilds


well_metadata_df = pd.DataFrame({"Well Name":well_ids, "Well Substrate":list_of_substrates})

## Checking for and making new directory for output files

output_folder_name = output_directory + "Ecoplate_Calculations/"

if not os.path.isdir(output_folder_name):
    os.makedirs(output_folder_name)

## Outputting Excel Spreadsheet with Reordered Absorbance Readings

with pd.ExcelWriter(output_folder_name + "Reordered_Ecoplate_Data.xlsx") as writer:
    for sheetname in sorted(full_reordered_data_dict.keys()):
        values_dataframe = pd.DataFrame(full_reordered_data_dict[sheetname])
        metadata_values_dataframe = pd.concat([well_metadata_df, values_dataframe], axis=1)

        metadata_values_dataframe.to_excel(writer, sheet_name=sheetname, index=False)

## Running Functions to Perform Calculations

awcd_dict = calculate_awcd(full_reordered_data_dict, well_metadata_df)
sawcd_dict = calculate_sawcd(full_reordered_data_dict, well_metadata_df, inverted_substrate_guilds)
shannon_div_dict, shannon_even_dict, substrate_rich_dict = calculate_diversity(full_reordered_data_dict, well_metadata_df, threshold)

## Outputing Excel Spreadsheet with AWCD values

with pd.ExcelWriter(output_folder_name + "Ecoplate_Average_Well_Color_Development.xlsx") as writer_2:
    if "," in separator:
        for splits in separator.split(","):
            specific_series = pd.Series()
            for names in sorted(awcd_dict.keys()):
                if splits in names:
                    specific_series = pd.concat([specific_series, awcd_dict[names]], axis=1)
            
            specific_series.drop(0, axis=1, inplace=True)

            specific_series.to_excel(writer_2, sheet_name=splits, index=True)
    else:
        specific_series = pd.Series()
        for names in sorted(awcd_dict.keys()):
            if separator in names:
                specific_series = pd.concat([specific_series, awcd_dict[names]], axis=1)
            
        specific_series.drop(0, axis=1, inplace=True)

        specific_series.to_excel(writer_2, sheet_name=separator, index=True)

## Outputting Excel Spreadsheet with SAWCD values

with pd.ExcelWriter(output_folder_name + "Ecoplate_Substrate_Average_Well_Color_Development.xlsx") as writer_3:
    for names in sorted(sawcd_dict.keys()):
        output_sheet = sawcd_dict[names]

        output_sheet.to_excel(writer_3, sheet_name=names, index=True)

## Outputting Excel Spreadsheet with Diversity, Richness, and Evenness

with pd.ExcelWriter(output_folder_name + "Ecoplate_Community_Metrics.xlsx") as writer_4:
    if "," in separator:
        for splits in separator.split(","):
            temp_sd = pd.Series()
            temp_se = pd.Series()
            temp_sr = pd.Series()

            for names in sorted(shannon_div_dict.keys()):
                if splits in names:
                    temp_sd = pd.concat([temp_sd, shannon_div_dict[names]], axis=1)
            for names in sorted(shannon_even_dict.keys()):
                if splits in names:
                    temp_se = pd.concat([temp_se, shannon_even_dict[names]], axis=1)
            for names in sorted(substrate_rich_dict.keys()):
                if splits in names:
                    temp_sr = pd.concat([temp_sr, substrate_rich_dict[names]], axis=1)
                        
            temp_sd.drop(0, axis=1, inplace=True)
            temp_se.drop(0, axis=1, inplace=True)
            temp_sr.drop(0, axis=1, inplace=True)

            temp_sd.to_excel(writer_4, sheet_name=splits + " Shannon Diversity", index=True)
            temp_sr.to_excel(writer_4, sheet_name=splits + " Substrate Richness", index=True)
            temp_se.to_excel(writer_4, sheet_name=splits + " Shannon Evenness", index=True)
    else:
        temp_sd = pd.Series()
        temp_se = pd.Series()
        temp_sr = pd.Series()

        for names in sorted(shannon_div_dict.keys()):
            if splits in names:
                temp_sd = pd.concat([temp_sd, shannon_div_dict[names]], axis=1)
        for names in sorted(shannon_even_dict.keys()):
            if splits in names:
                temp_se = pd.concat([temp_se, shannon_even_dict[names]], axis=1)
        for names in sorted(substrate_rich_dict.keys()):
            if splits in names:
                temp_sr = pd.concat([temp_sr, substrate_rich_dict[names]], axis=1)
                        
        temp_sd.drop(0, axis=1, inplace=True)
        temp_se.drop(0, axis=1, inplace=True)
        temp_sr.drop(0, axis=1, inplace=True)

        temp_sd.to_excel(writer_4, sheet_name=splits + " Shannon Diversity", index=True)
        temp_sr.to_excel(writer_4, sheet_name=splits + " Substrate Richness", index=True)
        temp_se.to_excel(writer_4, sheet_name=splits + " Shannon Evenness", index=True)

