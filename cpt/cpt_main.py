# Importing libraries
import os
import pandas as pd
import pyodbc
import numpy as np
import cpt_processing as calc
import cpt_plotting as plot
from cpt_figure_class import CPT_figure
import cpt_figure_class

###-----Ignore warning-----  ###
import warnings

warnings.filterwarnings("ignore")

###-----Functions-----  ###
###-----Function to extract values from input dataframe-----  ###
def extract_values_from_input_df(df,variable):
    value=df.loc[variable].at['Value']
    return value

###-----Function to extract a list of values from input dataframe-----  ###
def extract_list_from_input_df(df,variable):
    list=df.loc[variable].tolist()
    return list

###-----Function to check if a folder exist and otherwise create it-----  ###
def check_path_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return

###-----main function to return the dataframe dictionary as excel for checking purposes-----  ###
def pd_to_excel(df, output_folder_path):
    excel_path = os.path.join(output_folder_path, SCPT_Location[0]+"_CPT_processed_data.xlsx")
    df.to_excel(excel_path)
    return

def pd_to_csv(df, output_folder_path):
    csv_path = os.path.join(output_folder_path, SCPT_Location[0]+"_CPT_processed_data.csv")
    df.to_csv(csv_path)
    return

def load_df(file_path):
    #could add an option for pickle file later if it get too slow with csv
    file_ext = os.path.splitext(file_path)[1]
    if 'xls' in file_ext.lower():
        df = pd.read_excel(file_path)
    elif 'csv' in file_ext.lower():
        df = pd.read_csv(file_path)
    return df

###-----Global variable-----  ###
#Valid for all CPTs
# dictionary of constants for G0=-A*eff_p^(na)
G0_constants = {'A': [6000, 8000, 10000, 12000, 14000], 'na': [0.5, 0.5, 0.5, 0.5, 0.5]}

# dictionary for Ic limits
# Ic_limits = {'Limit': [0, 1.31, 2.05, 2.6, 2.95, 3.6, 99],
#              'Description': ['GS \nto S', 'S \nto SM', 'SM \nto MS', 'MC \nto CM', 'CM \nto C', 'OP', 'ND']}
Ic_limits = {'Limit': [0, 1.31, 2.05, 2.6, 2.95, 3.6, 99],
             'Description': ['Gravelly SAND  \nto SAND', 'SAND to  \nSilty SAND', 'Silty SAND  \nto \nSandy SILT',
                             'Clayey \nSILT  \nto Silty \nCLAY', 'Silty CLAY \nto CLAY','Organic \nCLAY \nand \nPEAT', 'ND']}
# dictionary for Dr limits
Dr_limits = {'Limit': [0, 15, 35, 65, 85],
             'Description': ['Very \nloose', 'Loose', 'Medium \ndense', 'Dense', 'Very \ndense']}

# path for input excel file
programme_folder_path = os.getcwd()
# input_excel_path=os.path.join(programme_folder_path, '../Input_files/Python_CPT_Input_Template.xlsx')
input_excel_path=os.path.join(programme_folder_path, '../Input_files/Python_Multiple-CPT_Input_Template.xlsx')

# Read input excel file for global variables, input for single plot and side by side plot
# global_variable_df = pd.read_excel(input_excel_path, sheet_name='Global_variable', index_col=0)
global_variable_df = pd.read_excel(input_excel_path, sheet_name='Global_variable')
single_plot_input_df = pd.read_excel(input_excel_path, sheet_name='Single_plot_input')
side_by_side_plot_input_df = pd.read_excel(input_excel_path, sheet_name='Side_by_side_plot_input')
stratigraphy_color_input_df = pd.read_excel(input_excel_path,sheet_name='Stratigraphy_color_dict')
series_input_df = pd.read_excel(input_excel_path, sheet_name='Series_info').set_index('series name')
axis_input_df = pd.read_excel(input_excel_path, sheet_name='Axis_info').set_index('axis name')
# print(series_input_df)
# print(axis_input_df)

###----------------------------------------------------------------------------------  ###
#Loop through the CPT location to process
for i in range(len(global_variable_df)):
    print(i)
    # figure extension: e.g. '.svg', '.png'
    #ext_fig = extract_values_from_input_df(global_variable_df,'Figure_extension')
    ext_fig = global_variable_df.at[i,'Figure_extension']

    # project folder path
    # proj_folder_path = extract_values_from_input_df(global_variable_df,'Project folder path')
    proj_folder_path = global_variable_df.at[i,'Project folder path']
    check_path_exists(proj_folder_path)

    # Input folder path for excels or database file
    # input_folder_path = extract_values_from_input_df(global_variable_df,'Input folder path')
    input_folder_path = global_variable_df.at[i,'Input folder path']
    # check_path_exists(input_folder_path)

    # output folder path for the processed excel file
    # output_folder_path = extract_values_from_input_df(global_variable_df,'Output folder path')
    output_folder_path = global_variable_df.at[i,'Output folder path']
    check_path_exists(output_folder_path)

    # folder path for saving figures
    # folder_fig = extract_values_from_input_df(global_variable_df,'Figure folder path')
    folder_fig = global_variable_df.at[i,'Figure folder path']
    check_path_exists(folder_fig)

    ###-----User input-----  ### True or False
    # load_gINT_database_as_dataframe_and_merge = extract_values_from_input_df(global_variable_df,'Load gINT database')  # True if you want to load tables from .gpj file as dataframe and merge- see Hornsea-Two as example
    load_gINT_database_as_dataframe_and_merge = global_variable_df.at[i,'Load gINT database']
    # load_excel_table_as_dataframe_and_merge = extract_values_from_input_df(global_variable_df,'Load excel files') # True if you want to load tables from your excel file in AGS format - see RWE Taiwan as example
    load_excel_table_as_dataframe_and_merge = global_variable_df.at[i,'Load excel files']
    # process_CPT = extract_values_from_input_df(global_variable_df,'Process CPT')
    process_CPT = global_variable_df.at[i,'Process CPT']
    # plot_CPT = extract_values_from_input_df(global_variable_df,'Plot CPT')
    plot_CPT = global_variable_df.loc[i,'Plot CPT']

    # Path for the database
    if load_gINT_database_as_dataframe_and_merge:
        # db_path = os.path.join(input_folder_path,extract_values_from_input_df(global_variable_df,'database file name')) # This is a gINT database file for Hornsea 2, and can be accessed using Access.
        db_path = os.path.join(input_folder_path, global_variable_df.at[i,'database file name'])

    if load_excel_table_as_dataframe_and_merge:
        # Path for the Excel for unprocessed tables if you want processing and plotting
        # SCPT_path = os.path.join(input_folder_path,extract_values_from_input_df(global_variable_df,'SCPT file name'))
        SCPT_path = os.path.join(input_folder_path, global_variable_df.at[i,'SCPT file name'])
        # SCPG_path = os.path.join(input_folder_path,extract_values_from_input_df(global_variable_df,'SCPG file name'))
        SCPG_path = os.path.join(input_folder_path, global_variable_df.at[i,'SCPG file name'])
        # SOIL_UNIT_path = os.path.join(input_folder_path,extract_values_from_input_df(global_variable_df,'SOIL_UNIT file name'))
        SOIL_UNIT_path = os.path.join(input_folder_path,
                                      global_variable_df.at[i,'SOIL_UNIT file name'])
        # SOIL_PROPERTY_path = os.path.join(input_folder_path,extract_values_from_input_df(global_variable_df,'SOIL_PROPERTY file name'))
        SOIL_PROPERTY_path = os.path.join(input_folder_path,
                                          global_variable_df.at[i,'SOIL_PROPERTY file name'])

    # folder path for the processed Excel dataframe if you want plotting only
    if not process_CPT:
    # df_path = os.path.join(input_folder_path,extract_values_from_input_df(global_variable_df,'Processed excel file name'))
        df_path = os.path.join(input_folder_path,
                           global_variable_df.at[i,'Processed data file name'])

    # Unit weight of water
    # gamma_w = extract_values_from_input_df(global_variable_df,'gamma w')
    gamma_w = global_variable_df.at[i,'gamma w']
    # Elevation of water table
    # Elev_WT = extract_values_from_input_df(global_variable_df,'Elevation of water table')
    Elev_WT = global_variable_df.at[i,'Elevation of water table']

    # SCPT location that we want to plot --> specified by user
    # SCPT_Location = extract_list_from_input_df(global_variable_df,'SCPT location')  # ['BH06-TAICHUNG'] for RWE Taiwan project and for ['WTG_L097_028'] Hornsea Two Project
    SCPT_Location = global_variable_df.filter(like='SCPT location').iloc[i].dropna().to_list()
    print(SCPT_Location)
    # if pd.isna(SCPT_Location[1]):
    #     SCPT_Location.remove(np.nan)

    ###----------------------------------------------------------------------------------  ###

    ###-----start from the gINT database file, connect to it, retrieve the tables and load each as panda dataframe-----  ###
    if load_gINT_database_as_dataframe_and_merge:

        ###-----Connection to the database-----  ###
        # Connect to the database. First have to install access drivers:
        # https://www.microsoft.com/en-us/download/details.aspx?id=13255
        connStr = (
                r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
                r"DBQ=%s;" % db_path
        )
        cnxn = pyodbc.connect(connStr)

        ###-----Retrieve all headings of the tables to make sure db is connected-----  ###
        cursor = cnxn.cursor()
        # for row in cursor.tables():
        #     print(row.table_name)

        ###-----Retrieve our desired tables and load each of them as individual panda dataframe-----  ###
        sql_SCPT = "Select * From [SCPT]"
        sql_SCPG = "Select * From [SCPG]"
        SCPT = pd.read_sql(sql_SCPT, cnxn)
        SCPG = pd.read_sql(sql_SCPG, cnxn)
        try:
            sql_SOIL_UNIT = "Select * From [SOIL_UNIT]"
            SOIL_UNIT = pd.read_sql(sql_SOIL_UNIT, cnxn)
        except:
            SOIL_UNIT = pd.DataFrame(columns=['PointID', 'Depth', 'DEPTH_BASE', 'GEOL_UNIT'])
        try:
            sql_SOIL_PROPERTY = "Select * From [SOIL_PROPERTY]"
            SOIL_PROPERTY = pd.read_sql(sql_SOIL_PROPERTY, cnxn)
        except:
            SOIL_PROPERTY = pd.DataFrame(
                columns=['ItemKey', 'SOIL_CLASS', 'UNIT_WEIGHT', 'K0', 'Phi', 'Nkt_UB', 'Nkt_LB', 'Kg'])

        ###-----Merging the dataframes-----  ###
        merged_SCPT = calc.merge_tables(SCPT, SCPG, SCPT_Location, SOIL_UNIT, SOIL_PROPERTY)

        ###-----Creating a color dict for all the stratigraphy present in the whole site-----  ###
        #AMB comment: Why having it twice?  Why not running it once after you load data (either way)?
        #stratigraphy_color_dict = cpt_figure_class.create_stratigraphy_color_dict(SOIL_PROPERTY)
    ###----------------------------------------------------------------------------------  ###

    ###-----start from the gINT database file, connect to it, retrieve the tables and load each as panda dataframe-----  ###
    if load_excel_table_as_dataframe_and_merge:
        # Dictionary to convert some AGS name column names to be compatible with the codes in cpt_processing
        col_name_conversion = {'LOCA_ID': 'PointID', 'SCPG_TESN': 'ItemKey', 'SCPT_DPTH': 'Depth'}
        # You should have added a column in the SCPG.xlsx called 'Location_ID' in the SCPG excel which is the location of the CPT

        ###-----Retrieve our desired tables from Excel and load each of them as individual panda dataframe-----  ###
        SCPT = pd.read_excel(SCPT_path)
        try:
            SCPT.rename(columns=col_name_conversion, inplace=True)
        except:
            pass

        SCPG = pd.read_excel(SCPG_path)
        try:
            SCPG.rename(columns=col_name_conversion, inplace=True)
        except:
            pass

        try:
            SOIL_UNIT = pd.read_excel(SOIL_UNIT_path)
        except:
            SOIL_UNIT = pd.DataFrame(columns=['PointID', 'Depth', 'DEPTH_BASE', 'GEOL_UNIT'])
        try:
            SOIL_PROPERTY = pd.read_excel(SOIL_PROPERTY_path)
        except:
            SOIL_PROPERTY = pd.DataFrame(
                columns=['ItemKey', 'SOIL_CLASS', 'UNIT_WEIGHT', 'K0', 'Phi', 'Nkt_UB', 'Nkt_LB', 'Kg'])

        ###-----Merging the dataframes-----  ###
        merged_SCPT = calc.merge_tables(SCPT, SCPG, SCPT_Location, SOIL_UNIT, SOIL_PROPERTY)

        ###-----Creating a color dict for all the stratigraphy present in the whole site-----  ###
        #stratigraphy_color_dict = cpt_figure_class.create_stratigraphy_color_dict(SOIL_PROPERTY)

    ###----------------------------------------------------------------------------------  ###

    #Dictionary for Stratigraphy colors - need to add an if for the case where the sheet is empty - then use sc function
    stratigraphy_color_dict = dict(stratigraphy_color_input_df.values)


    ###-----Process CPT data with a given dataframe-----  ###
    if process_CPT:
        print(SCPT_Location)
        # if we are not starting from
        if load_gINT_database_as_dataframe_and_merge:
            df = merged_SCPT
        elif load_excel_table_as_dataframe_and_merge:
            df = merged_SCPT
        processed_CPT = calc.process_CPT(df, gamma_w, G0_constants, Elev_WT=Elev_WT)
        # pd_to_excel(processed_CPT, output_folder_path)
        pd_to_csv(processed_CPT, output_folder_path)
        # if CPT.Location_ID == SCPT_Location:
        #     CPT.df = processed_CPT
    ###----------------------------------------------------------------------------------  ###


    ###-----Plotting-----  ###
    if plot_CPT:
        # get the main CPT location
        main_CPT = SCPT_Location[0]
        main_option=[main_CPT,np.nan]
        # get the other CPT locations that you may want to compare
        if len(SCPT_Location)>1:
            list_of_other_CPT = SCPT_Location[1:]

        # get the dataframe
        if process_CPT:
            df = processed_CPT
        else:
            # df = pd.read_excel(df_path)
            df = load_df(df_path)

        df_main = df[df['Location_ID'].isin(main_option)]

        #get color dict
        plot_color_dict = plot.get_color_dict(df)
        #dictionary for axis labels
        axis_label_dict = { # 2 options: full name or math notation
            'depth': ['Depth below mudline (m)','Depth below mudline (m)'],
            'qc': [r'Cone resistance (MPa)',r'$q_c \mathrm{ (MPa)}$'],
            'rf': [r'Friction ratio (%)', r'$R_f \mathrm{ (\%)}$'],
            'u2': [r'Pore water pressure (MPa)',r'$u_2 \mathrm{ (MPa)}$'],
            'phi':[r'Angle of shearing resistance (degree)',r'$\phi (\degree)$'],
            'su': [r'Undrained Strength (kPa)',r'$S_u \mathrm{ (kPa)}$'],
            'dr': [r'Relative density (%)', r'$D_r \mathrm{ (\%)}$'],
            'go': [r'Shear modulus (MPa)', r'$G_{0} \mathrm{ (MPa)}$'],
            'ic': [r'$I_c \mathrm{ values}$',r'$I_c \mathrm{ values}$'],
            'eff_sig_y': [r'Yield stress (kPa)',r'$\sigma^''_y \mathrm{ (kPa)}$'],
            'OCR': [r'OCR', 'OCR']
            }

        #Dictionary for plot label (related to plot column name) - [mplt,bokeh]
        plot_label_dict = {
            'SCPT_RES'  : [r'$q_c$','qc'],
            'qt_uncorr' : [r'$q_t$','qt'],
            'qt_corr'   : [r'$q_t$ (corr)',r'qt (corr)'],
            'Rf'        : [r'$R_f$',r'Rf'],
            'SCPT_PWP2' : [r'$u_2$',r'u2'],
            'u2_corr'   : [r'$u_2$ (corr)',r'u2 (corr)'],
            'u0'        : [r'$u_0$',r'u0'],
            'Su_UB'     : [r'$ Su_{UB}$',r'Su-UB'],
            'Su_LB'     : [r'$ Su_{LB}$',r'Su-LB'],
            'peak_phi_UB': [r'$ \phi_{Peak, UB}$',r'Peak (UB)'],
            'peak_phi_LB': [r'$ \phi_{Peak, LB}$',r'Peak (LB)'],
            'Dr_Baldi'  : [r'$D_r$ (Baldi et al., 1986)',r'Baldi'],
            'Dr_Jam_sat': [r'$D_r$ saturated \n (Jamiolkowski et al., 2003)',r'sat Jam'],
            'G0_A'      : [r'$ G_{0}/p^{0.5}$' + '={}'.format(G0_constants['A'][0]), r'$ G0/p^0.5' + '={}'.format(G0_constants['A'][0])],
            'G0_B'      : [r'$ G_{0}/p^{0.5}$' + '={}'.format(G0_constants['A'][1]), r'$ G0/p^0.5' + '={}'.format(G0_constants['A'][1])],
            'G0_C'      : [r'$ G_{0}/p^{0.5}$' + '={}'.format(G0_constants['A'][2]), r'$ G0/p^0.5' + '={}'.format(G0_constants['A'][2])],
            'G0_D'      : [r'$ G_{0}/p^{0.5}$' + '={}'.format(G0_constants['A'][3]), r'$ G0/p^0.5' + '={}'.format(G0_constants['A'][3])],
            'G0_E'      : [r'$ G_{0}/p^{0.5}$' + '={}'.format(G0_constants['A'][4]), r'$ G0/p^0.5' + '={}'.format(G0_constants['A'][4])],
            'G0_RS'     : [r'$ G_{0}$' + ' Rix & Stokoe (1992)',r'$Rix & Stokoe (1992)'],
            'G0_ICP'    : [r'$ G_{0}$' + ' Jardine et al. (2005)',r'$Jardine et al. (2005)'],
            'Ic'        : ['r$I_c$',r'Ic'],
            'eff_sig_y_UB' : [r'$\sigma^''_{y, UB}',r'eff_sig_y (UB)'],
            'eff_sig_y_LB': [r'$\sigma^''_{y, LB}', r'eff_sig_y (LB)'],
            'OCR_UB': [r'OCR (UB)', r'OCR (UB)'],
            'OCR_LB': [r'OCR (LB)', r'OCR (LB)']
        }

        # define the soil unit table for plotting stratigraphy
        SOIL_UNIT_TABLE = df_main[['GEOL_UNIT', 'DEPTH_TOP', 'DEPTH_BASE','Location_ID','CPT_name','UNIQUE_GEOL']].drop_duplicates().dropna()

        #-------------------------------------------------------------------------------------------------------------------
        # Plot side by side graphs of qc, Rf, u
        plot_list1 = [['SCPT_RES', 'qt_uncorr', 'qt_corr'], ['Rf'], ['SCPT_PWP2', 'u2_corr', 'u0']]
        color_list1 = [['#0070C0', '#4BACC6', '#6E548D'], ['#00B050'], ['#A8423F', '#00B050', '#1F497D']]
        # name_list1 = [[r'$q_c$', r'$q_t$', r'$q_t$ (corr)'], [r'$R_f$'], [r'$u_2$', r'$u_2$ (corr)', r'$u_0$']]
        name_list1 = plot.get_label_list(plot_list1, plot_label_dict, 0)
        # xy_label_list1 = [[r'$q_c\mathrm{(MPa)}$', r'$R_f (\%)$', r'$u_2\mathrm{(MPa)}$'], ['Depth below mudline (m)']]
        xy_label_list = [['qc', 'rf', 'u2'], ['depth']]
        xy_label_list1 = plot.get_label_list(xy_label_list, axis_label_dict, 0)
        xy_limit_list1 = [[[0, None], [0, None], [0, None]], [None, 0]]
        multiplier_list1 = [[1, 1, 1], [1], [1, 1, 0.001]]
        template_dict1={'size':'A4-Landscape', 'client':'RWE', 'project':'RWE-Taiwan', 'clientN':'2232', 'projectN':'10001', 'issue':'Rev0', 'date':'11/7/22', 'maincaption':'CPT plot',
                                   'subcaption':'Interpreted CPT data', 'figN':'1'}
        fig1=CPT_figure('A4-Landscape','side_by_side',plot_list1)
        fig1.side_by_side(df_main, plot_list1, color_list1, name_list1, xy_label_list1, xy_limit_list1, multiplier_list1)
        fig1.savefig(folder_fig,'Graph_qc_Rf_u', fext=ext_fig)

        #amb - Try interactive plotting with bokeh
        fig1_i = plot.side_by_side_interactive_plot(df, plot_list1, plot_color_dict, name_list1,
                                                    xy_label_list1, xy_limit_list1, multiplier_list1,
                                                    SOIL_UNIT_TABLE, stratigraphy_color_dict)
        plot.save_interactive_fig(fig1_i,folder_fig,'Graph_qc_Rf_u')
        #Plot other CPT locations to side by side graphs of qc, Rf, u, and compare
        #AMB - I think it is best to create a new different figure for that.
        # if len(SCPT_Location)>1:
        #     color_list1_other = [[['#641E16', '#C0392B', '#F1948A'] , ['#641E16'], ['#641E16', '#C0392B', '#F1948A']],[['#E09448', '#5C3610', '#F2D1B0'] , ['#AFF3BA'], ['#E09448', '#5C3610', '#F2D1B0']]]
        #     fig1.add_CPT_to_plot(df, plot_list1, color_list1_other, name_list1, xy_label_list1, xy_limit_list1, multiplier_list1, list_of_other_CPT)
        #     fig1.savefig(folder_fig, 'Graph_qc_Rf_u_compared', fext=ext_fig)



        # Plot side by side graphs of qc, Rf, u, Su, phi
        plot_list_1a = [['SCPT_RES', 'qt_uncorr', 'qt_corr'], ['Rf'], ['SCPT_PWP2', 'u2_corr', 'u0'], ['Su_UB', 'Su_LB'],
                        ['peak_phi_UB', 'peak_phi_LB']]
        color_list_1a = [['#0070C0', '#4BACC6', '#6E548D'], ['#00B050'], ['#A8423F', '#00B050', '#1F497D'],
                         ['#1F497D', '#4BACC6'], ['#1F497D', '#4BACC6']]
        # name_list_1a = [[r'$q_c$', r'$q_t$', r'$q_t$ (corr)'], [r'$R_f$'], [r'$u_2$', r'$u_2$ (corr)', r'$u_0$'],
        #                 [r'$ Su_{UB}$' + '\n (Lunne et al., 1997)', r'$ Su_{LB}$' + '\n (Lunne et al., 1997)'],
        #                 [r'$ \phi_{Peak, UB}$' + ' (Schmertmann, 1978)', r'$ \phi_{Peak, LB}$' + ' (Schmertmann, 1978)']]
        name_list_1a = plot.get_label_list(plot_list_1a,plot_label_dict,0)
        # xy_label_list_1a = [[r'$q_c\.(MPa)$', r'$R_f\.(\%)$', r'$u_2\.(MPa)$', r'$S_u\.(kPa)$', r'$\phi\.(\degree)$'],
        #                     ['Depth below mudline (m)']]
        xy_label_list = [['qc','rf', 'u2', 'su', 'phi'],['depth']]
        xy_label_list_1a = plot.get_label_list(xy_label_list,axis_label_dict,0)
        xy_limit_list_1a = [[[0, 50], [0, 10], [0, 2], [0, 350], [0, 50]], [None, 0]]
        multiplier_list_1a = [[1, 1, 1], [1], [1, 1, 0.001], [1, 1], [1, 1]]

        fig_1a=CPT_figure('A4-Landscape','side_by_side',plot_list_1a)
        fig_1a.side_by_side(df_main, plot_list_1a, color_list_1a, name_list_1a, xy_label_list_1a, xy_limit_list_1a,
                                   multiplier_list_1a)
        fig_1a.savefig(folder_fig, 'Graph_qc_Rf_u_Su_phi', fext=ext_fig)
        #amb - Try interactive plotting with bokeh
        fig1a_i = plot.side_by_side_interactive_plot(df, plot_list_1a, plot_color_dict, name_list_1a,
                                                     xy_label_list_1a,xy_limit_list_1a, multiplier_list_1a,
                                                     SOIL_UNIT_TABLE, stratigraphy_color_dict)
        plot.save_interactive_fig(fig1a_i,folder_fig, 'Graph_qc_Rf_u_Su_phi')

        #Plot other CPT locations to side by side graphs of qc, Rf, u, Su, phi and compare
        # if len(SCPT_Location)>1:
        #     color_list_1a_other = [[['#641E16', '#C0392B', '#F1948A'] , ['#641E16'], ['#641E16', '#C0392B', '#F1948A'],
        #                      ['#641E16', '#C0392B'], ['#641E16', '#C0392B']],[['#E09448', '#5C3610', '#F2D1B0'] , ['#AFF3BA'], ['#E09448', '#5C3610', '#F2D1B0'],['#E09448', '#5C3610'],['#E09448', '#5C3610']]]
        #     fig_1a.add_CPT_to_plot(df, plot_list_1a, color_list_1a_other, name_list_1a, xy_label_list_1a, xy_limit_list_1a,
        #                                multiplier_list_1a, list_of_other_CPT)
        #     fig_1a.savefig(folder_fig, 'Graph_qc_Rf_u_Su_phi_compared', fext=ext_fig)



        # Plot side by side graphs of qc, Rf, u, Su, Dr
        plot_list_1b = [['SCPT_RES', 'qt_uncorr', 'qt_corr'], ['Rf'], ['SCPT_PWP2', 'u2_corr', 'u0'], ['Su_UB', 'Su_LB'],
                        ['Dr_Baldi', 'Dr_Jam_sat']]
        color_list_1b = [['#0070C0', '#4BACC6', '#6E548D'], ['#00B050'], ['#A8423F', '#00B050', '#1F497D'],
                         ['#1F497D', '#4BACC6'], ['#1F497D', '#4BACC6']]
        # name_list_1b = [[r'$q_c$', r'$q_t$', r'$q_t$ (corr)'], [r'$R_f$'], [r'$u_2$', r'$u_2$ (corr)', r'$u_0$'],
        #                 [r'$ Su_{UB}$' + '\n (Lunne et al., 1997)', r'$ Su_{LB}$' + '\n (Lunne et al., 1997)'],
        #                 [r'$D_r$ (Baldi et al., 1986)',r'$D_r$ saturated \n (Jamiolkowski et al., 2003)']]
        name_list_1b = plot.get_label_list(plot_list_1b,plot_label_dict,1)
        # xy_label_list_1b = [[r'$q_c\mathrm{ (MPa)}$', r'$R_f\mathrm{ (\%)}$', r'$u_2\mathrm{ (MPa)}$', r'$S_u\mathrm{ (kPa)}$', r'$D_r\mathrm{ (\%)}$'],
        #                     ['Depth below mudline (m)']]
        xy_label_list = [['qc', 'rf', 'u2','su', 'dr'], ['depth']]
        xy_label_list_1b = plot.get_label_list(xy_label_list,axis_label_dict,0)
        xy_limit_list_1b = [[[0, 50], [0, 10], [0, 2], [0, 350], [0, 100]], [None, 0]]
        multiplier_list_1b = [[1, 1, 1], [1], [1, 1, 0.001], [1, 1], [1, 1]]
        fig_1b = CPT_figure('A4-Landscape', 'side_by_side', plot_list_1b)
        fig_1b.side_by_side(df_main, plot_list_1b, color_list_1b, name_list_1b, xy_label_list_1b, xy_limit_list_1b,
                                   multiplier_list_1b)
        fig_1b.savefig(folder_fig, 'Graph_qc_Rf_u_Su_Dr', fext=ext_fig)
        #amb - Interactive plotting with bokeh
        fig1b_i = plot.side_by_side_interactive_plot(df, plot_list_1b, plot_color_dict, name_list_1b,
                                                     xy_label_list_1b, xy_limit_list_1b, multiplier_list_1b,
                                                     SOIL_UNIT_TABLE, stratigraphy_color_dict)
        plot.save_interactive_fig(fig1b_i,folder_fig, 'Graph_qc_Rf_u_Su_Dr')

        #Plot other CPT locations to side by side graphs of qc, Rf, u, Su, Dr and compare
        # if len(SCPT_Location)>1:
        #     fig_1b.add_CPT_to_plot(df, plot_list_1b, color_list_1a_other, name_list_1b, xy_label_list_1b, xy_limit_list_1b,
        #                                multiplier_list_1b, list_of_other_CPT)
        #     fig_1b.savefig(folder_fig, 'Graph_qc_Rf_u_Su_Dr_compared', fext=ext_fig)


        # save the figure in GCG's template
        # fig_path = os.path.join(folder_fig, 'Graph_qc_Rf_u_Su_Dr'+ext_fig)
        # fig_1b_gcg=cpt_figure_class.put_figure_in_GCG_Template_and_save(fig_path, template_dict1,)
        # cpt_figure_class.savefig(folder_fig, fig_1b_gcg, 'Graph_qc_Rf_u_Su_Dr_template', fext=ext_fig)

        #-------------------------------------------------------------------------------------------------------------------
        # Plot side by side graphs of qc, eff_sig_y, OCR
        plot_list1c = [['SCPT_RES', 'qt_uncorr', 'qt_corr'], ['eff_sig_y_UB','eff_sig_y_LB'], ['OCR_UB','OCR_LB']]
        color_list1c = [['#0070C0', '#4BACC6', '#6E548D'], ['#ED7D31','#FFFF66'], ['#ED7D31','#FFFF66']]
        name_list1c = plot.get_label_list(plot_list1c, plot_label_dict, 0)
        xy_label_list = [['qc', 'eff_sig_y', 'OCR'], ['depth']]
        xy_label_list1c = plot.get_label_list(xy_label_list, axis_label_dict, 0)
        xy_limit_list1c = [[[0, None], [0, None], [0, 5]], [None, 0]]
        multiplier_list1c = [[1, 1, 1], [1,1], [1,1]]
        fig1c=CPT_figure('A4-Landscape','side_by_side',plot_list1c)
        fig1c.side_by_side(df_main, plot_list1c, color_list1c, name_list1c, xy_label_list1c, xy_limit_list1c, multiplier_list1c)
        fig1c.savefig(folder_fig,'Graph_qc_sigy_OCR', fext=ext_fig)

        #amb - Try interactive plotting with bokeh
        fig1c_i = plot.side_by_side_interactive_plot(df, plot_list1c, plot_color_dict, name_list1c,
                                                    xy_label_list1c, xy_limit_list1c, multiplier_list1c,
                                                    SOIL_UNIT_TABLE, stratigraphy_color_dict)

        #SC: seems to have issues with the interactive plot for this figure. Comment it out firt. To be investigated later
        # plot.save_interactive_fig(fig1c_i,folder_fig,'Graph_qc_sigy_OCR')

        #Plot other CPT locations to side by side graphs of qc, Rf, u, and compare
        #AMB - I think it is best to create a new different figure for that.
        # if len(SCPT_Location)>1:
        #     color_list1c_other = [[['#641E16', '#C0392B', '#F1948A'] ,['#4472C4','#66FFFF'], ['#4472C4','#66FFFF']],[['#A8423F', '#00B050', '#1F497D'],['#70AD47','#CCFFCC'],['#70AD47','#CCFFCC']],[['#641E16', '#C0392B', '#F1948A'] ,['#4472C4','#66FFFF']]]
        #     fig1c.add_CPT_to_plot(df, plot_list1c, color_list1c_other, name_list1c, xy_label_list1c, xy_limit_list1c, multiplier_list1c, list_of_other_CPT)
        #     fig1c.savefig(folder_fig, 'Graph_qc_sigy_OCR_compared', fext=ext_fig)




        #-------------------------------------------------------------------------------------------------------------------
        # Plot single plot
        plot_list2 = ['SCPT_RES', 'qt_uncorr', 'qt_corr']
        color_list2 = ['#0070C0', '#4BACC6', '#6E548D']
        # name_list2 = [r'$q_c$', r'$q_t$ (uncorr)', r'$q_t$ (corr)']
        name_list2 = plot.get_label_list(plot_list2, plot_label_dict, 0)
        # xy_label_list2 = [[r'$q_c \mathrm{ (MPa)}$'], ['Depth below mudline (m)']]
        xy_label_list2 = [['qc'], ['depth']]
        xy_label_list2 = plot.get_label_list(xy_label_list,axis_label_dict,0)
        multiplier_list2 = [1, 1, 1]
        xy_limit_list2 = [[0, None], [None, 0]]
        template_dict2={'size':'A4-Portrait', 'client':'RWE', 'project':'RWE-Taiwan', 'clientN':'2232', 'projectN':'10001', 'issue':'Rev0', 'date':'11/7/22', 'maincaption':'CPT plot',
                                   'subcaption':'Interpreted CPT data', 'figN':'2'}
        fig2=CPT_figure('A4-Portrait', 'single_plot', plot_list2)
        fig2.single_plot(df_main, plot_list2, color_list2, name_list2, xy_label_list2, xy_limit_list2, multiplier_list2)
        fig2.savefig(folder_fig, 'Graph_qc', fext=ext_fig)

        #amb - Try interactive plotting with bokeh
        fig2_i = plot.single_interactive_plot(df, plot_list2, plot_color_dict, name_list2,
                                              xy_label_list2, xy_limit_list2, multiplier_list2,
                                              SOIL_UNIT_TABLE, stratigraphy_color_dict)
        plot.save_interactive_fig(fig2_i,folder_fig, 'Graph_qc')


        # save the figure in GCG's template
        # fig_path_2 = os.path.join(folder_fig, 'Graph_qc.png')
        # fig_2_gcg=cpt_figure_class.put_figure_in_GCG_Template_and_save(fig_path_2, template_dict2)
        # cpt_figure_class.savefig(folder_fig, fig_2_gcg, 'Graph_qc_template', fext=ext_fig)

        # -------------------------------------------------------------------------------------------------------------------
        # Plots with soil stratigraphy next to it - only plot for 1 SCPT location.
        fig1_strat=CPT_figure('A4-Landscape', 'side_by_side_with_stratigraphy', plot_list1)
        fig1_strat.side_by_side_with_stratigraphy(df_main, plot_list1, color_list1, name_list1, xy_label_list1,
                                                         xy_limit_list1,
                                                         multiplier_list1,
                                                         SOIL_UNIT_TABLE,
                                                         stratigraphy_color_dict)
        fig1_strat.savefig(folder_fig, 'stratigraphy_with_Graph_qc_Rf_u', fext=ext_fig)

        fig1a_strat = CPT_figure('A4-Landscape', 'side_by_side_with_stratigraphy', plot_list_1a)
        fig1a_strat.side_by_side_with_stratigraphy(df_main, plot_list_1a, color_list_1a, name_list_1a, xy_label_list_1a,
                                                          xy_limit_list_1a,
                                                          multiplier_list_1a,
                                                          SOIL_UNIT_TABLE,
                                                          stratigraphy_color_dict)
        fig1a_strat.savefig(folder_fig, 'stratigraphy_with_Graph_qc_Rf_u_su_phi', fext=ext_fig)

        fig1b_strat = CPT_figure('A4-Landscape', 'side_by_side_with_stratigraphy', plot_list_1b)
        fig1b_strat.side_by_side_with_stratigraphy(df_main, plot_list_1b, color_list_1b, name_list_1b, xy_label_list_1b,
                                                          xy_limit_list_1b,
                                                          multiplier_list_1b,
                                                          SOIL_UNIT_TABLE,
                                                          stratigraphy_color_dict)
        fig1b_strat.savefig(folder_fig, 'stratigraphy_with_Graph_qc_Rf_u_su_Dr', fext=ext_fig)

        fig2a=CPT_figure('A4-Portrait', 'single_plot_with_stratigraphy', plot_list2)
        fig2a.single_plot_with_stratigraphy(df_main, plot_list2, color_list2, name_list2, xy_label_list2, xy_limit_list2,
                                                   multiplier_list2,
                                                   SOIL_UNIT_TABLE,
                                                   stratigraphy_color_dict)
        fig2a.savefig(folder_fig, 'stratigraphy_with_Graph_qc', fext=ext_fig)

        # Plot of Dr with Stratigraphy
        plot_list3 = ['Dr_Baldi', 'Dr_Jam_sat']
        color_list3 = ['#386192', '#FF0000']
        # name_list3 = ['Dr (Baldi et al., 1986)', 'Dr saturated (Jamiolkowski et al., 2003)']
        name_list3 = plot.get_label_list(plot_list3, plot_label_dict, 0)
        # xy_label_list3 = [[r'$D_r (\%)$'], ['Depth below mudline (m)']]
        xy_label_list = [['dr'], ['depth']]
        xy_label_list3 = plot.get_label_list(xy_label_list,axis_label_dict,0)
        xy_limit_list3 = [[0, 100], [None, 0]]
        multiplier_list3 = [1, 1]

        fig3 = CPT_figure('A4-Portrait', 'single_plot_with_stratigraphy', plot_list3)
        fig3.single_plot_with_stratigraphy(df_main, plot_list3, color_list3, name_list3, xy_label_list3,
                                                           xy_limit_list3, multiplier_list3,
                                                           SOIL_UNIT_TABLE,
                                                           stratigraphy_color_dict, Dr_limits)
        fig3.savefig(folder_fig, 'stratigraphy_with_Graph_Dr', fext=ext_fig)
        # Try interactive plotting with bokeh
        fig3_i = plot.single_interactive_plot(df, plot_list3, plot_color_dict, name_list3,
                                              xy_label_list3, xy_limit_list3, multiplier_list3,
                                              SOIL_UNIT_TABLE, stratigraphy_color_dict)
        plot.save_interactive_fig(fig3_i, folder_fig, 'Graph_Dr')

        # Plot of phi with Stratigraphy
        plot_list4 = ['peak_phi_UB', 'peak_phi_LB']
        color_list4 = ['#1F497D', '#4BACC6']
        name_list4 = [r'$ \phi_{Peak, UB}$' + ' (Schmertmann, 1978)', r'$ \phi_{Peak, LB}$' + ' (Schmertmann, 1978)']
        name_list4 = plot.get_label_list(plot_list4,plot_label_dict,0)
        # xy_label_list4 = [[r'$ \phi (\degree)$'], ['Depth below mudline (m)']]
        xy_label_list = [['dr'], ['depth']]
        xy_label_list4 = plot.get_label_list(xy_label_list,axis_label_dict,0)
        xy_limit_list4 = [[0, None], [None, 0]]
        multiplier_list4 = [1, 1]
        fig4 = CPT_figure('A4-Portrait', 'single_plot_with_stratigraphy', plot_list4)
        fig4.single_plot_with_stratigraphy(df_main, plot_list4, color_list4, name_list4,
                                           xy_label_list4, xy_limit_list4,multiplier_list4,
                                           SOIL_UNIT_TABLE, stratigraphy_color_dict)
        fig4.savefig(folder_fig, 'stratigraphy_with_Graph_phi', fext=ext_fig)
        # Try interactive plotting with bokeh
        fig4_i = plot.single_interactive_plot(df, plot_list4, plot_color_dict, name_list4,
                                              xy_label_list4, xy_limit_list4, multiplier_list4,
                                              SOIL_UNIT_TABLE, stratigraphy_color_dict)
        plot.save_interactive_fig(fig4_i, folder_fig, 'Graph_phi')

        # Plots of G0 with Stratigraphy
        plot_list5 = ['G0_A', 'G0_B', 'G0_C', 'G0_D', 'G0_E', 'G0_RS', 'G0_ICP']
        color_list5 = ['#BFBFBF', '#BFBFBF', '#BFBFBF', '#BFBFBF', '#BFBFBF', '#1F497D', '#4BACC6']
        # name_list5 = [
        #     r'$ G_{0}/p^{0.5}$' + '={}'.format(G0_constants['A'][0]),
        #     r'$ G_{0}/p^{0.5}$' + '={}'.format(G0_constants['A'][1]),
        #     r'$ G_{0}/p^{0.5}$' + '={}'.format(G0_constants['A'][2]),
        #     r'$ G_{0}/p^{0.5}$' + '={}'.format(G0_constants['A'][3]),
        #     r'$ G_{0}/p^{0.5}$' + '={}'.format(G0_constants['A'][4]),
        #     r'$ G_{0}$' + ' Rix & Stokoe (1992)',
        #     r'$ G_{0}$' + ' Jardine et al. (2005)']
        name_list5 = plot.get_label_list(plot_list5,plot_label_dict,0)
        # xy_label_list5 = [[r'$ G_{0}$' + '(MPa)'], ['Depth below mudline (m)']]
        xy_label_list = [['go'], ['depth']]
        xy_label_list5 = plot.get_label_list(xy_label_list,axis_label_dict,0)
        xy_limit_list5 = [[0, None], [None, 0]]
        multiplier_list5 = [1, 1, 1, 1, 1, 1, 1]
        fig5 = CPT_figure('A4-Portrait', 'single_plot_with_stratigraphy', plot_list5)
        fig5.single_plot_with_stratigraphy(df_main, plot_list5, color_list5, name_list5, xy_label_list5, xy_limit_list5,
                                                  multiplier_list5,
                                                  SOIL_UNIT_TABLE,
                                                  stratigraphy_color_dict)
        fig5.savefig(folder_fig, 'stratigraphy_with_Graph_G0', fext=ext_fig)



        # Plot of Su with Stratigraphy
        plot_list6 = ['Su_UB', 'Su_LB']
        color_list6 = ['#1F497D', '#4BACC6']
        # name_list6 = [r'$ Su_{UB}$' + ' (Lunne et al., 1997)', r'$ Su_{LB}$' + ' (Lunne et al., 1997)']
        name_list6 = plot.get_label_list(plot_list6, plot_label_dict, 0)
        # xy_label_list6 = [[r'$S_u$ (kPa)'], ['Depth below mudline (m)']]
        xy_label_list = [['su'], ['depth']]
        xy_label_list6 = plot.get_label_list(xy_label_list, axis_label_dict, 0)
        xy_limit_list6 = [[0, 500], [None, 0]]
        multiplier_list6 = [1, 1]
        fig6 = CPT_figure('A4-Portrait', 'single_plot_with_stratigraphy', plot_list6)
        fig6.single_plot_with_stratigraphy(df_main, plot_list6, color_list6, name_list6, xy_label_list6, xy_limit_list6,
                                                  multiplier_list6,
                                                  SOIL_UNIT_TABLE,
                                                  stratigraphy_color_dict)
        fig6.savefig(folder_fig, 'stratigraphy_with_Graph_Su', fext=ext_fig)

        # Try interactive plotting with bokeh
        fig6_i = plot.single_interactive_plot(df, plot_list6, plot_color_dict, name_list6,
                                              xy_label_list6, xy_limit_list6, multiplier_list6,
                                              SOIL_UNIT_TABLE, stratigraphy_color_dict)
        plot.save_interactive_fig(fig6_i, folder_fig, 'Graph_Su')

        # Plot of IC values
        plot_list7 = ['Ic']
        color_list7 = ['#0070C0']
        name_list7 = plot.get_label_list(plot_list7, plot_label_dict, 0)
        # xy_label_list7 = [['Ic values'], ['Depth below mudline (m)']]
        xy_label_list = [['ic'], ['depth']]
        xy_label_list7 = plot.get_label_list(xy_label_list, axis_label_dict, 0)
        xy_limit_list7 = [[0, 4], [None, 0]]
        multiplier_list7 = [1, 1]
        fig7 = CPT_figure('A4-Portrait', 'single_plot', plot_list7)
        fig7.single_plot(df_main, plot_list7, color_list7, name_list7, xy_label_list7,
                                                 xy_limit_list7,
                                                 multiplier_list7)
        fig7.savefig(folder_fig, 'Graph_Ic', fext=ext_fig)

        fig7_strat = CPT_figure('A4-Portrait', 'single_plot_with_stratigraphy', plot_list7)
        fig7_strat.single_plot_with_stratigraphy(df_main, plot_list7, color_list7, name_list7, xy_label_list7,
                                                           xy_limit_list7,
                                                           multiplier_list7,
                                                           SOIL_UNIT_TABLE,
                                                           stratigraphy_color_dict, Ic_limits)
        fig7_strat.savefig(folder_fig, 'Graph_Ic', fext=ext_fig)

        # Try interactive plotting with bokeh
        fig7_strat_i = plot.single_interactive_plot(df, plot_list7, plot_color_dict, name_list7,
                                              xy_label_list7, xy_limit_list7, multiplier_list7,
                                              SOIL_UNIT_TABLE, stratigraphy_color_dict)
        plot.save_interactive_fig(fig7_strat_i, folder_fig, 'Graph_Ic')


    # ###-----Create a class instance for each CPT location-----  ###
    # Location_ID_column = SCPG[['Location_ID']].replace("", float("NaN")).drop_duplicates().dropna()
    # for i, row in Location_ID_column.iterrows():
    #     CPT()
    #     CPT.Location_ID = row.values[0]
