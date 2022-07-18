###-----This is a module for importing data from raw CPT files (text file) -----  ###
#Library import
import pandas as pd
from pathlib import Path

###-----Inputs for importing data -----  ###
parent_folder_path = 'S:/Clients/T-Z/Thor Wind Farm/02_Working/CPT-data/'
folder_path = [parent_folder_path+'EOS-BH-01 ASCII/',parent_folder_path+'EOS-BH-01A ASCII/']
location_ID = ['EOS-BH-01','EOS-BH-01']
point_ID = ['EOS-BH-01','EOS-BH-01A']
file_extension = 'A00'
skip_rows = [i for i in range(17)]
skip_rows.append(18)
skip_rows.append(19)
col_widths = [10, 11, 11, 11, 12, 11, 11, 12]
col_import = lambda x: ("Depth" in x) or ("Cone" in x) or ("Friction" in x) or ("Pore 2" in x)or ("Fric. Ratio" in x)

#Dictionary to convert column name to AGS name
col_name_conversion = {'Depth':'SCPT_DPTH','Cone':'SCPT_RES','Friction':'SCPT_FRES','Pore 2':'SCPT_PWP2',
                       'Fric. Ratio':'SCPT_FRR','Push':'SCPG_TESN'}

###----- Function for importing data for 1 CPT location (different pushes) -----  ###
def collate_CPT_push(folder_path,col_widths,skip_rows,col_import,col_name_conversion,location,point_id):
    '''
    Function to collate data from text files containing the raw data for different CPT pushes at a given location
    Function assumes that all the files are in the same folder, have the same extensions, and the text files have
    a uniform format organised by fixed width columns (NOT csv with separator).
    :param folder_path: string
    :param col_widths: list of integers, giving the width of each columns (in number of character)
    :param skip_rows: list of integers, the number of the lines to skip
    :param col_import: either a list of the name to import or can be a lambda function to select column according to criteria
    :param col_name_conversion: dictionary, to convert the column names to the AGS 4 naming convention
    :param loc: string, location identification
    :return: a panda dataframe with the CPT push collated in the form of an AGS4
    '''
    #get list of all file with proper extension
    path_list = Path(folder_path).glob('**/*.'+file_extension)
    #Create an empty dataframe
    main_df = pd.DataFrame()
    for path in path_list:
        print(path)
        temp_df = pd.read_fwf(path, widths=col_widths, skiprows=skip_rows, header=0, usecols=col_import)
        ind=path.stem.find('CPT')
        temp_df['Push'] = path.stem[ind:ind+5]
        temp_df['LOCA_ID']=location
        temp_df['PointID']=point_id
        main_df = main_df.append(temp_df, ignore_index = True)
    #Rename the col name to match AGS
    main_df.rename(columns=col_name_conversion, inplace=True)
    return main_df

###----- Function for collating data from several CPT location -----  ###
def collate_CPTs(folder_path,col_widths,skip_rows,col_import,col_name_conversion,location,point_id):
    '''
    Function to collate data from text files containing the raw data for different CPT pushes at several locations
    :param folder_path: List of strings, each folder is assumed to contrain the raw data for 1 CPT location
    :param col_widths: list of integers, giving the width of each columns (in number of character)
    :param skip_rows: list of integers, the number of the lines to skip
    :param col_import: either a list of the name to import or can be a lambda function to select column according to criteria
    :param col_name_conversion: dictionary, to convert the column names to the AGS 4 naming convention
    :param location: list of string, location identification (can have several CPTs at 1 location)
    :param point_id: list of string, point identification (should only have 1 CPT per point, but can have several pushes)
    :return: a panda dataframe with the CPT collated in the form of an AGS4
    '''
    main_df = pd.DataFrame()
    for i in range(len(folder_path)):
        temp_df = collate_CPT_push(folder_path[i],col_widths,skip_rows,col_import,col_name_conversion,location[i],point_id[i])
        main_df = main_df.append(temp_df, ignore_index=True)
    return main_df

###----- Collate data and save data frame -----  ###
#data = collate_CPT_push(folder_path,col_widths,skip_rows,col_import,col_name_conversion,loc='EOS-BH-01')
data = collate_CPTs(folder_path,col_widths,skip_rows,col_import,col_name_conversion,location_ID,point_ID)
data.to_csv(Path(parent_folder_path)/'EOS-BH-01_CPT.csv')
print(data)