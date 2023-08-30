import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# SC's plotting module. To be replaced with AMB's revised plotting module
import cpt_plotting as plot

# Global variables/ user input
# Number of readings over which the moving average and moving standard deviation will be calculated: n_average (3 readings above until 3 readings below each data point)
n_average=7
# Minimum layer thickness: n_min
d_min=1
#Maximum number of layers: n_layer (may need to iteratively try)
n_layer=20
#Threshold value (SBT_thres_dist) for the distance of the respective points  (log(qt/pa), log(Rf)) in Robertson’s diagram of two adjacent layers: Typically in the range of 0.1 – 0.3
SBT_thres_dist=0.1
#Best-fit percentile
best_fit_percentile=0.4
#Lower bound percentile
lower_bound_percentile=0.05
# Atmospheric pressure
pa=101.325




# Read Excel, to be replaced by getting the excel from the input spreadsheet
df = pd.read_csv(r'C:\Users\sc\PycharmProjects\SI_processing_automation_SC\Output_files\Processed-CPT\JDN\A2 (2018)_CPT_processed_data.csv')



# Cleaning the data
def check_data(df):
    df['Qtn'].replace('', np.nan, inplace=True)
    df[df['Qtn']>1000]=np.nan
    df['Fr'].replace('', np.nan, inplace=True)
    df[df['Fr']<=0]=np.nan
    df.dropna(subset=['Qtn'], inplace=True)
    df.dropna(subset=['Fr'], inplace=True)
    # check if numeric only
    # other checks to be implemented



# Calculate log10(Qtn) and log10(Fr)
def calc_log10(df, Qtn,Fr):
    #df['log(qt/pa)']=np.log10(df['qt_corr']/pa)
    #df['log(Rf)']=np.log10(df['Rf'])
    df['log_Qtn']=np.log10(Qtn)
    df['log_Fr']=np.log10(Fr)




# Calculate Moving average and Moving Standard deviations over n_average
def calc_moving_average(df, log_Qtn, log_Fr):
    # Get moving averages
    df['Qtn_moving_average']=log_Qtn.rolling(n_average, center=True).mean()
    df['Fr_moving_average']=log_Fr.rolling(n_average, center=True).mean()


def calc_moving_std(df, log_Qtn, log_Fr):
    df['Qtn_moving_STDEV']=log_Qtn.rolling(n_average, center=True).std()
    df['Fr_moving_STDEV'] = log_Fr.rolling(n_average, center=True).std()
    df['sum_moving_STDEV']= df['Qtn_moving_STDEV']+df['Fr_moving_STDEV']



def trial_plot(df):
    plot_list=['Qtn_moving_STDEV', 'Fr_moving_STDEV','sum_moving_STDEV' ]
    name_list=[ ['Qtn_moving_STDEV'], ['Fr_moving_STDEV'],['sum_moving_STDEV'] ]
    f, axs = plt.subplots(figsize=(8.27, 11.69))
    for i, plot in enumerate(plot_list):
        x, z = df[plot_list[i]], df['Depth']
        axs.plot(
            x, z,
            label='{}'.format(name_list[i]),
            ls='-',  # linestyle
            # marker='o', mfc='none',  # marker and marker face color
            #color=color_list[i]
        )
    f.savefig(r'C:\Users\sc\PycharmProjects\SI_processing_automation_SC\Output_files\trial.png')



# Find the highest standard deviation (peak)
def find_max_std(df):
    layer_dict={}
    peak=df['sum_moving_STDEV'].max
    corresponding_depth=df
    # key = depth
    value = peak

    layer_dict[key] = value
    # layer_dict = {
    #     key1: value1,
    #     key2: value2,
    #     key3: value3,
    # }
    df[df['Fr']<=0]=np.nan
    df.dropna(subset=['Qtn'], inplace=True)

# Store the corresponding depth in a dictionary: Layer_dict={Depth: Standard deviation}
# Remove all standard deviations within a distance, dmin, around this level
# Search for the next peak in standard deviation


# Optional:
# For all peaks (depths) in the list Calculate average values of log(qt/Pa) and log (Rf)
# If the distance of the respective points (log(qt/pa), log(Rf)) in Robertson's diagram of
# 2 adjacent layers is less than a certain threshold value, delete this peak and depth


# Decompose the CPT into sub-layers based on the remaining peaks (depths) in the list
# Calculate averaged CPT parameters for all sublayers
# Add new columns (layer depth, averaged parameters)


# main
check_data(df)
calc_log10(df, df['Qtn'],df['Fr'])
calc_moving_average(df, df['log_Qtn'], df['log_Fr'])
calc_moving_std(df, df['log_Qtn'], df['log_Fr'])
trial_plot(df)
