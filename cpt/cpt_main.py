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

###-----Function to extract values from input dataframe-----  ###
def extract_values_from_input_df(df,variable):
    value=df.loc[variable].at['Value']
    return value

###-----Function to extract a list of values from input dataframe-----  ###
def extract_list_from_input_df(df,variable):
    list=df.loc[variable].tolist()
    return list


###-----Global variable-----  ###
# path for input excel file
programme_folder_path = os.getcwd()
input_excel_path=os.path.join(programme_folder_path, '../Input_files/Python_CPT_Input_Template.xlsx')

# Read input excel file for global variables, input for single plot and side by side plot
global_variable_df = pd.read_excel(input_excel_path, sheet_name='Global_variable', index_col=0)
single_plot_input_df = pd.read_excel(input_excel_path, sheet_name='Single_plot_input')
side_by_side_plot_input_df = pd.read_excel(input_excel_path, sheet_name='Side_by_side_plot_input')
stratigraphy_color_input_df = pd.read_excel(input_excel_path,sheet_name='stratigraphy_color_dict')

# figure extension: e.g. '.svg', '.png'
ext_fig = extract_values_from_input_df(global_variable_df,'Figure_extension')

# project folder path
proj_folder_path = extract_values_from_input_df(global_variable_df,'Project folder path')

# Input folder path for excels or database file
input_folder_path=extract_values_from_input_df(global_variable_df,'Input folder path')

# folder path for saving figures
folder_fig = extract_values_from_input_df(global_variable_df,'Figure folder path')

# output folder path for the processed excel file
output_folder_path=extract_values_from_input_df(global_variable_df,'Output folder path')


###-----User input-----  ### True or False
load_gINT_database_as_dataframe_and_merge = extract_values_from_input_df(global_variable_df,'Load gINT database')  # True if you want to load tables from .gpj file as dataframe and merge- see Hornsea-Two as example
load_excel_table_as_dataframe_and_merge = extract_values_from_input_df(global_variable_df,'Load excel files')  # True if you want to load tables from your excel file in AGS format - see RWE Taiwan as example
process_CPT = extract_values_from_input_df(global_variable_df,'Process CPT')
plot_CPT = extract_values_from_input_df(global_variable_df,'Plot CPT')


# Path for the database
if load_gINT_database_as_dataframe_and_merge:
    db_path = os.path.join(input_folder_path,extract_values_from_input_df(global_variable_df,'database file name')) # This is a gINT database file for Hornsea 2, and can be accessed using Access.

# Path for the Excel for unprocessed tables if you want processing and plotting
SCPT_path = os.path.join(input_folder_path,extract_values_from_input_df(global_variable_df,'SCPT file name'))
SCPG_path = os.path.join(input_folder_path,extract_values_from_input_df(global_variable_df,'SCPG file name'))
SOIL_UNIT_path = os.path.join(input_folder_path,extract_values_from_input_df(global_variable_df,'SOIL_UNIT file name'))
SOIL_PROPERTY_path = os.path.join(input_folder_path,extract_values_from_input_df(global_variable_df,'SOIL_PROPERTY file name'))

# folder path for the processed Excel dataframe if you want plotting only
df_path = os.path.join(input_folder_path,extract_values_from_input_df(global_variable_df,'database file name'))

# Unit weight of water
gamma_w = extract_values_from_input_df(global_variable_df,'gamma w')
# Elevation of water table
Elev_WT = extract_values_from_input_df(global_variable_df,'Elevation of water table')
# dictionary of constants for G0=-A*eff_p^(na)
G0_constants = {'A': [6000, 8000, 10000, 12000, 14000], 'na': [0.5, 0.5, 0.5, 0.5, 0.5]}

# dictionary for Ic limits
Ic_limits = {'Limit': [0, 1.31, 2.05, 2.6, 2.95, 3.6, 99],
             'Description': ['GS \nto S', 'S \nto SM', 'SM \nto MS', 'MC \nto CM', 'CM \nto C', 'OP', 'ND']}
# dictionary for Dr limits
Dr_limits = {'Limit': [0, 15, 35, 65, 85],
             'Description': ['Very \nloose', 'Loose', 'Medium \ndense', 'Dense', 'Very \ndense']}
# SCPT location that we want to plot --> specified by user
SCPT_Location = extract_list_from_input_df(global_variable_df,'SCPT location')  # ['BH06-TAICHUNG'] for RWE Taiwan project and for ['WTG_L097_028'] Hornsea Two Project

###----------------------------------------------------------------------------------  ###



###----------------------------------------------------------------------------------  ###

###-----main function to return the dataframe dictionary as excel for checking purposes-----  ###
def pd_to_excel(df, output_folder_path):
    excel_path = os.path.join(output_folder_path, "CPT_processed_data-v2.xlsx")
    df.to_excel(excel_path)
    return


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
    for row in cursor.tables():
        print(row.table_name)

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
    processed_CPT = calc.process_CPT(df, gamma_w, G0_constants, Elev_WT=0)
    pd_to_excel(processed_CPT, output_folder_path)
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
        df = pd.read_excel(df_path)

    df_main = df[df['Location_ID'].isin(main_option)]



    # define the soil unit table for plotting stratigraphy
    SOIL_UNIT_TABLE = df_main[['GEOL_UNIT', 'DEPTH_TOP', 'DEPTH_BASE','Location_ID']].drop_duplicates().dropna()

    # Plot side by side graphs of qc, Rf, u
    plot_list1 = [['SCPT_RES', 'qt_uncorr', 'qt_corr'], ['Rf'], ['SCPT_PWP2', 'u2_corr', 'u0']]
    color_list1 = [['#0070C0', '#4BACC6', '#6E548D'], ['#00B050'], ['#A8423F', '#00B050', '#1F497D']]
    name_list1 = [[r'$q_c$', r'$q_t$', r'$q_t$ (corr)'], [r'$R_f$'], [r'$u_2$', r'$u_2$ (corr)', r'$u_0$']]
    xy_label_list1 = [[r'$q_c$ (MPa)', r'$R_f$ (%)', r'$u_2$ (MPa)'], ['Depth below mudline (m)']]
    xy_limit_list1 = [[[0, None], [0, None], [0, None]], [None, 0]]
    multiplier_list1 = [[1, 1, 1], [1], [1, 1, 0.001]]
    template_dict1={'size':'A4-Landscape', 'client':'RWE', 'project':'RWE-Taiwan', 'clientN':'2232', 'projectN':'10001', 'issue':'Rev0', 'date':'11/7/22', 'maincaption':'CPT plot',
                               'subcaption':'Interpreted CPT data', 'figN':'1'}
    fig1=CPT_figure('A4-Landscape','side_by_side',plot_list1)
    fig1.side_by_side(df_main, plot_list1, color_list1, name_list1, xy_label_list1, xy_limit_list1, multiplier_list1)
    fig1.savefig(folder_fig,'Graph_qc_Rf_u', fext=ext_fig)

    #Plot other CPT locations to side by side graphs of qc, Rf, u, and compare
    color_list1_other = [['#641E16', '#C0392B', '#F1948A'] , ['#641E16'], ['#641E16', '#C0392B', '#F1948A']]
    fig1.add_CPT_to_plot(df, plot_list1, color_list1_other, name_list1, xy_label_list1, xy_limit_list1, multiplier_list1, list_of_other_CPT)
    fig1.savefig(folder_fig, 'Graph_qc_Rf_u_compared', fext=ext_fig)



    # Plot side by side graphs of qc, Rf, u, Su, phi
    plot_list_1a = [['SCPT_RES', 'qt_uncorr', 'qt_corr'], ['Rf'], ['SCPT_PWP2', 'u2_corr', 'u0'], ['Su_UB', 'Su_LB'],
                    ['peak_phi_UB', 'peak_phi_LB']]
    color_list_1a = [['#0070C0', '#4BACC6', '#6E548D'], ['#00B050'], ['#A8423F', '#00B050', '#1F497D'],
                     ['#1F497D', '#4BACC6'], ['#1F497D', '#4BACC6']]
    name_list_1a = [[r'$q_c$', r'$q_t$', r'$q_t$ (corr)'], [r'$R_f$'], [r'$u_2$', r'$u_2$ (corr)', r'$u_0$'],
                    [r'$ Su_{UB}$' + '\n (Lunne et al., 1997)', r'$ Su_{LB}$' + '\n (Lunne et al., 1997)'],
                    [r'$ \phi_{Peak, UB}$' + ' (Schmertmann, 1978)', r'$ \phi_{Peak, LB}$' + ' (Schmertmann, 1978)']]
    xy_label_list_1a = [[r'$q_c$ (MPa)', r'$R_f$ (%)', r'$u_2$ (MPa)', r'$S_u$ (kPa)', r'$ \phi (\degree)$'],
                        ['Depth below mudline (m)']]
    xy_limit_list_1a = [[[0, 50], [0, 10], [0, 2], [0, 350], [0, 50]], [None, 0]]
    multiplier_list_1a = [[1, 1, 1], [1], [1, 1, 0.001], [1, 1], [1, 1]]

    fig_1a=CPT_figure('A4-Landscape','side_by_side',plot_list_1a)
    fig_1a.side_by_side(df_main, plot_list_1a, color_list_1a, name_list_1a, xy_label_list_1a, xy_limit_list_1a,
                               multiplier_list_1a)
    fig_1a.savefig(folder_fig, 'Graph_qc_Rf_u_Su_phi', fext=ext_fig)

    #Plot other CPT locations to side by side graphs of qc, Rf, u, Su, phi and compare
    color_list_1a_other = [['#641E16', '#C0392B', '#F1948A'] , ['#641E16'], ['#641E16', '#C0392B', '#F1948A'],
                     ['#641E16', '#C0392B'], ['#641E16', '#C0392B']]
    fig_1a.add_CPT_to_plot(df, plot_list_1a, color_list_1a_other, name_list_1a, xy_label_list_1a, xy_limit_list_1a,
                               multiplier_list_1a, list_of_other_CPT)
    fig_1a.savefig(folder_fig, 'Graph_qc_Rf_u_Su_phi_compared', fext=ext_fig)


    # Plot side by side graphs of qc, Rf, u, Su, Dr
    plot_list_1b = [['SCPT_RES', 'qt_uncorr', 'qt_corr'], ['Rf'], ['SCPT_PWP2', 'u2_corr', 'u0'], ['Su_UB', 'Su_LB'],
                    ['Dr_Baldi', 'Dr_Jam_sat']]
    color_list_1b = [['#0070C0', '#4BACC6', '#6E548D'], ['#00B050'], ['#A8423F', '#00B050', '#1F497D'],
                     ['#1F497D', '#4BACC6'], ['#1F497D', '#4BACC6']]
    name_list_1b = [[r'$q_c$', r'$q_t$', r'$q_t$ (corr)'], [r'$R_f$'], [r'$u_2$', r'$u_2$ (corr)', r'$u_0$'],
                    [r'$ Su_{UB}$' + '\n (Lunne et al., 1997)', r'$ Su_{LB}$' + '\n (Lunne et al., 1997)'],
                    ['Dr (Baldi et al., 1986)', 'Dr saturated \n (Jamiolkowski et al., 2003)']]
    xy_label_list_1b = [[r'$q_c$ (MPa)', r'$R_f$ (%)', r'$u_2$ (MPa)', r'$S_u$ (kPa)', r'$D_r$ (%)'],
                        ['Depth below mudline (m)']]
    xy_limit_list_1b = [[[0, 50], [0, 10], [0, 2], [0, 350], [0, 100]], [None, 0]]
    multiplier_list_1b = [[1, 1, 1], [1], [1, 1, 0.001], [1, 1], [1, 1]]
    fig_1b = CPT_figure('A4-Landscape', 'side_by_side', plot_list_1b)
    fig_1b.side_by_side(df_main, plot_list_1b, color_list_1b, name_list_1b, xy_label_list_1b, xy_limit_list_1b,
                               multiplier_list_1b)
    fig_1b.savefig(folder_fig, 'Graph_qc_Rf_u_Su_Dr', fext=ext_fig)


    #Plot other CPT locations to side by side graphs of qc, Rf, u, Su, Dr and compare
    fig_1b.add_CPT_to_plot(df, plot_list_1b, color_list_1a_other, name_list_1b, xy_label_list_1b, xy_limit_list_1b,
                               multiplier_list_1b, list_of_other_CPT)
    fig_1b.savefig(folder_fig, 'Graph_qc_Rf_u_Su_Dr_compared', fext=ext_fig)


    # save the figure in GCG's template
    # fig_path = os.path.join(folder_fig, 'Graph_qc_Rf_u_Su_Dr'+ext_fig)
    # fig_1b_gcg=cpt_figure_class.put_figure_in_GCG_Template_and_save(fig_path, template_dict1,)
    # cpt_figure_class.savefig(folder_fig, fig_1b_gcg, 'Graph_qc_Rf_u_Su_Dr_template', fext=ext_fig)

    # Plot single plot
    plot_list2 = ['SCPT_RES', 'qt_uncorr', 'qt_corr']
    color_list2 = ['#0070C0', '#4BACC6', '#6E548D']
    name_list2 = ['qc', 'qt (uncorr)', 'qt (corr)']
    xy_label_list2 = [['qc (MPa)'], ['Depth below mudline (m)']]
    multiplier_list2 = [1, 1, 1]
    xy_limit_list2 = [[0, None], [None, 0]]
    template_dict2={'size':'A4-Portrait', 'client':'RWE', 'project':'RWE-Taiwan', 'clientN':'2232', 'projectN':'10001', 'issue':'Rev0', 'date':'11/7/22', 'maincaption':'CPT plot',
                               'subcaption':'Interpreted CPT data', 'figN':'2'}
    fig2=CPT_figure('A4-Portrait', 'single_plot', plot_list2)
    fig2.single_plot(df_main, plot_list2, color_list2, name_list2, xy_label_list2, xy_limit_list2, multiplier_list2)
    fig2.savefig(folder_fig, 'Graph_qc', fext=ext_fig)

    # Plot other CPT locations to single plot
    color_list2_other = ['#641E16', '#C0392B', '#F1948A']
    fig2.add_CPT_to_plot(df, plot_list2, color_list2_other, name_list2, xy_label_list2, xy_limit_list2, multiplier_list2, list_of_other_CPT)
    fig2.savefig(folder_fig, 'Graph_qc_compared', fext=ext_fig)

    # save the figure in GCG's template
    # fig_path_2 = os.path.join(folder_fig, 'Graph_qc.png')
    # fig_2_gcg=cpt_figure_class.put_figure_in_GCG_Template_and_save(fig_path_2, template_dict2)
    # cpt_figure_class.savefig(folder_fig, fig_2_gcg, 'Graph_qc_template', fext=ext_fig)

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
    name_list3 = ['Dr (Baldi et al., 1986)', 'Dr saturated (Jamiolkowski et al., 2003)']
    xy_label_list3 = [[r'$D_r$ (%)'], ['Depth below mudline (m)']]
    xy_limit_list3 = [[0, 100], [None, 0]]
    multiplier_list3 = [1, 1]

    fig3 = CPT_figure('A4-Portrait', 'single_plot_with_stratigraphy', plot_list3)
    fig3.single_plot_with_stratigraphy(df_main, plot_list3, color_list3, name_list3, xy_label_list3,
                                                       xy_limit_list3, multiplier_list3,
                                                       SOIL_UNIT_TABLE,
                                                       stratigraphy_color_dict, Dr_limits)
    fig3.savefig(folder_fig, 'stratigraphy_with_Graph_Dr', fext=ext_fig)

    # Plot of phi with Stratigraphy
    plot_list4 = ['peak_phi_UB', 'peak_phi_LB']
    color_list4 = ['#1F497D', '#4BACC6']
    name_list4 = [r'$ \phi_{Peak, UB}$' + ' (Schmertmann, 1978)', r'$ \phi_{Peak, LB}$' + ' (Schmertmann, 1978)']
    xy_label_list4 = [[r'$ \phi (\degree)$'], ['Depth below mudline (m)']]
    xy_limit_list4 = [[0, None], [None, 0]]
    multiplier_list4 = [1, 1]
    fig4 = CPT_figure('A4-Portrait', 'single_plot_with_stratigraphy', plot_list4)
    fig4.single_plot_with_stratigraphy(df_main, plot_list4, color_list4, name_list4, xy_label_list4, xy_limit_list4,
                                              multiplier_list4,
                                              SOIL_UNIT_TABLE,
                                              stratigraphy_color_dict)
    fig4.savefig(folder_fig, 'stratigraphy_with_Graph_phi', fext=ext_fig)

    # Plots of G0 with Stratigraphy
    plot_list5 = ['G0_A', 'G0_B', 'G0_C', 'G0_D', 'G0_E', 'G0_RS', 'G0_ICP']
    color_list5 = ['#BFBFBF', '#BFBFBF', '#BFBFBF', '#BFBFBF', '#BFBFBF', '#1F497D', '#4BACC6']
    name_list5 = [
        r'$ G_{0}/p^{0.5}$' + '={}'.format(G0_constants['A'][0]),
        r'$ G_{0}/p^{0.5}$' + '={}'.format(G0_constants['A'][1]),
        r'$ G_{0}/p^{0.5}$' + '={}'.format(G0_constants['A'][2]),
        r'$ G_{0}/p^{0.5}$' + '={}'.format(G0_constants['A'][3]),
        r'$ G_{0}/p^{0.5}$' + '={}'.format(G0_constants['A'][4]),
        r'$ G_{0}$' + ' Rix & Stokoe (1992)',
        r'$ G_{0}$' + ' Jardine et al. (2005)']
    xy_label_list5 = [[r'$ G_{0}$' + '(MPa)'], ['Depth below mudline (m)']]
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
    name_list6 = [r'$ Su_{UB}$' + ' (Lunne et al., 1997)', r'$ Su_{LB}$' + ' (Lunne et al., 1997)']
    xy_label_list6 = [[r'$S_u$ (kPa)'], ['Depth below mudline (m)']]
    xy_limit_list6 = [[0, 500], [None, 0]]
    multiplier_list6 = [1, 1]
    fig6 = CPT_figure('A4-Portrait', 'single_plot_with_stratigraphy', plot_list6)
    fig6.single_plot_with_stratigraphy(df_main, plot_list6, color_list6, name_list6, xy_label_list6, xy_limit_list6,
                                              multiplier_list6,
                                              SOIL_UNIT_TABLE,
                                              stratigraphy_color_dict)
    fig6.savefig(folder_fig, 'stratigraphy_with_Graph_Su', fext=ext_fig)

    # Plot of IC values
    plot_list7 = ['Ic']
    color_list7 = ['#0070C0']
    name_list7 = [SCPT_Location]
    xy_label_list7 = [['Ic values'], ['Depth below mudline (m)']]
    xy_limit_list7 = [[0, 4], [None, 0]]
    multiplier_list7 = [1, 1]
    fig7 = CPT_figure('A4-Portrait', 'single_plot_with_stratigraphy', plot_list7)
    fig7.single_plot_with_stratigraphy(df_main, plot_list7, color_list7, name_list7, xy_label_list7,
                                                       xy_limit_list7,
                                                       multiplier_list7,
                                                       SOIL_UNIT_TABLE,
                                                       stratigraphy_color_dict, Ic_limits)
    fig7.savefig(folder_fig, 'stratigraphy_with_Graph_Ic', fext=ext_fig)

# ###-----Create a class instance for each CPT location-----  ###
# Location_ID_column = SCPG[['Location_ID']].replace("", float("NaN")).drop_duplicates().dropna()
# for i, row in Location_ID_column.iterrows():
#     CPT()
#     CPT.Location_ID = row.values[0]
