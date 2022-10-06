# Importing libraries
from pathlib import Path
import pandas as pd
import numpy as np
# machine learning librairies
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.mixture import GaussianMixture
from sklearn.cluster import SpectralClustering
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import silhouette_score
# plotting libraries
import seaborn as sns
import matplotlib.pyplot as plt
from bokeh.plotting import figure, show
from bokeh.transform import factor_cmap, factor_mark
from bokeh.layouts import gridplot
from bokeh.palettes import Category10
from bokeh.models import ColumnDataSource
from bokeh.io import save, output_file

sns.set_theme()
palette_10 = Category10[10]

###-----Note this is to try some machine learning algorithm -----  ###
#This is not for actual work at the moment - just for amb to play with

###-----Load data-----  ###
#load the pandas!
location_id = 'WTG-BH-02'
# input_folder_path = Path('S:/Clients/T-Z/Thor Wind Farm/02_Working/Gint_databases')
input_folder_path = Path('S:/Clients/T-Z/Thor Wind Farm/02_Working/CPT-data/WTG/'+location_id)
# file_name = 'EOS-all-CPT_data-python-process_01.xlsx'
# input_file_name = 'EOS-all-CPT_data-python-process_01.csv'
input_file_name = location_id +'_CPT_processed_data.csv'
input_columns = ['Depth','SCPT_RES','SCPT_FRES','SCPT_PWP2','SCPT_FRR','GEOL_UNIT','Qtn','Fr','Bq_corr','Bq_uncorr','Ic','u0']
# df = pd.read_excel(Path(folder_path) / file_name,usecols=columns_input)
df_main = pd.read_csv( input_folder_path / input_file_name,usecols=input_columns)
# df_main = df_main.dropna()

###-----Define outputs -----  ###
output_folder_path = Path('S:/Clients/T-Z/Thor Wind Farm/02_Working/CPT-data/WTG/ML-trials')

###-----Select features and format data -----  ###
#Add a delta_u = u2-uo
df_main['delta_u_uncorr'] = df_main['SCPT_PWP2'] - df_main['u0']/1000
#try with raw data first - should I normalise it?
# feature_list = ['Depth','SCPT_RES','SCPT_FRES','SCPT_PWP2']
# feature_list = ['SCPT_RES','SCPT_FRES','SCPT_PWP2']
# feature_list = ['SCPT_RES','SCPT_FRR','SCPT_PWP2']
# feature_list = ['Depth','SCPT_RES','SCPT_FRR','SCPT_PWP2']
# feature_list = ['Depth','SCPT_RES','SCPT_FRR']
feature_list = ['Depth','SCPT_RES','SCPT_FRR','delta_u_uncorr']
#try with Robertson (2016) parameters
# feature_list = ['Depth','Qtn','Fr','Bq_corr']
# feature_list = ['Depth','Qtn','Fr','Bq_uncorr']

#Get list of features
feature_str = ' '.join(map(str, feature_list))
print(feature_str)

#Convert and normalise data
X = df_main[feature_list].dropna().to_numpy()
print(X.shape)
# scaler = StandardScaler()
scaler = MinMaxScaler()
X = scaler.fit_transform(X)

###----- Vizualisations -----  ###

def plot_projection(x,y,hue,title, path, file_name):
    fig, axs =  plt.subplots(figsize=(10, 5))
    sns.scatterplot(x=x,y=x,hue=hue,ax=axs)
    axs.set(title = title)
    plt.savefig(path / file_name)
    plt.show()
    plt.close(fig)

#-- T-SNE projection --#
# perplexity = 100
# X_tsne = TSNE(n_components=2, perplexity=perplexity, learning_rate='auto', init='random').fit_transform(X)
# tsne_title= 'Perplexity = '+str(perplexity) + ' Features = ' + feature_str
# tsne_file = 'EOS-all-CPT_TSNE-perp'+str(perplexity)+'.svg'
# plot_projection(x=X_tsne[:,0],y=X_tsne[:,1],hue=df_main['GEOL_UNIT'],title=tsne_title,path = output_folder_path,file_name=tsne_file)

#-- PCA projection --#
# pca_proj = PCA().fit(X)
# X_pca = pca_proj.transform(X)
# print(X_pca)
# pca_title= 'PCA projection - Features = ' + feature_str
# pca_file = 'EOS-all-CPT_PCA-projection.svg'
# plot_projection(x=X_pca[:,0],y=X_pca[:,1],hue=df_main['GEOL_UNIT'],title=pca_title,path = output_folder_path,file_name=pca_file)

###-----Clustering with Gaussian Mixtures -----  ###

#Set parameters for model
chosen_K = 5
min_no_cluster = 2
max_no_cluster = 10
init_conditions = 'k-means++'
n_init = 10

def run_GaussianMix(X,k_min,k_max,**kwargs):
    gm = {}
    for i in range(k_min,k_max+1):
        gm[i] = GaussianMixture(n_components=i,**kwargs).fit(X)
    return gm

def get_cluster_scores(gm,X):
    df = pd.DataFrame(columns=['no_cluster','BIC','BIC_grad','AIC','Silhouette'],
                      index = [range(len(gm))])
    i= 0
    for k in gm:
        df.loc[i, 'no_cluster'] = k
        df.loc[i,'BIC'] = gm[k].bic(X)
        df.loc[i,'AIC'] = gm[k].aic(X)
        df.loc[i,'Silhouette']  = silhouette_score(X, gm[k].predict(X), metric='euclidean')
        i+=1
    df['BIC_grad'] = df.BIC.shift(-1)-df.BIC
    return df

def plot_cluster_scores(df,path,file_name):
    n_plot = df.shape[1]-1
    fig,axs = plt.subplots(n_plot,figsize=(6.3,n_plot*3.3),sharex =True)
    plot_list = list(df.columns)[1:]
    for i in range(n_plot):
        sns.lineplot(data=df,x='no_cluster',y=plot_list[i],ax=axs[i])
        axs[i].set(xlabel='Number of cluster', ylabel=plot_list[i]+' score')
    plt.tight_layout()
    plt.savefig( path / file_name )
    plt.close(fig)

def get_predictions(df,gm_dict,X,feature_list):
    for k in gm_dict:
        df.loc[df[feature_list].notna().all(axis=1),'gmm_predict_c'+str(k)] = gm_dict[k].predict(X)

def plot_model_vs_stratigraphy(df,col_name,model_name,feature_list, path, file_name,interactive=False,palette=None):
    if not interactive:
        fig, axs = plt.subplots(nrows=1, ncols=2,
                        sharey=True,figsize=(15, 17))
        axs[0].invert_yaxis()
        sns.scatterplot(data =df, x=col_name,y='Depth',hue=model_name,ax=axs[0])
        sns.scatterplot(data =df, x=col_name,y='Depth',hue='GEOL_UNIT',ax=axs[1])
        axs[0].set(xlabel=col_name, ylabel='Depth (m below mudline)')
        axs[1].set(xlabel=col_name, ylabel='Depth (m below mudline)')
        axs[0].set(title ='Features ='+feature_list)
        plt.tight_layout()
        plt.savefig( path / (file_name + '.svg'))
        plt.show()
        plt.close(fig)
    else:
        fig = []
        #first fig - model cluster
        fig.append(figure(
            x_axis_label=col_name,
            y_axis_label='Depth (m below mudline)',
            x_axis_location='above',
            #width=1241, #150 ppi*8.27 + legend
            #height=1754, #150ppi*11.69
            sizing_mode='scale_height'
        ))
        fig[0].y_range.flipped = True
        for i, cluster in enumerate(df[model_name].unique()):
            fig[0].scatter(x=df.loc[df[model_name] == cluster,col_name],
                           y=df.loc[df[model_name] == cluster,'Depth'],
                           color=palette[i],
                           legend_label= str(cluster)
                           )
        fig[0].legend.click_policy = "hide"
        #Second fig -
        fig.append(figure(
            x_axis_label=col_name,
            y_range = fig[0].y_range,
            x_axis_location='above',
            #width=1241, #150 ppi*8.27 + legend
            #height=1754, #150ppi*11.69
            sizing_mode='scale_height'
        ))
        fig[1].y_range.flipped = True
        for i, unit in enumerate(df['GEOL_UNIT'].unique()):
            fig[1].scatter(x=df.loc[df['GEOL_UNIT'] == unit, col_name],
                           y=df.loc[df['GEOL_UNIT'] == unit, 'Depth'],
                           color=palette[i],
                           legend_label=str(unit)
                           )
        fig[1].legend.click_policy="hide"
        combined_fig = gridplot([fig],width=17*75,height=15*75)
        #show(combined_fig)
        #output_file(path / (file_name + '.html'))
        save(obj = combined_fig, filename = path / (file_name + '.html'))

#check the best number of cluster - run GM with multiple k
# gmm_all = run_GaussianMix(X,min_no_cluster,max_no_cluster, init_params=init_conditions,n_init=10)
# df_gmm_scores = get_cluster_scores(gmm_all,X)
# plot_cluster_scores(df_gmm_scores,output_folder_path,'EOS-all-CPT_GMM-scores_K-mean-imp.svg')
# get_predictions(df_main,gmm_all,X)

#Run gm on selected K only
gm = GaussianMixture(n_components=chosen_K, init_params=init_conditions,n_init=n_init).fit(X)
# gm = GaussianMixture(n_components=chosen_K, init_params='random',n_init=n_init).fit(X)
col_res_name = 'gmm_predict_c' + str(chosen_K)
# print(df_main.loc[df_main[feature_list].notna().all(axis=1)])
df_main.loc[df_main[feature_list].notna().all(axis=1),col_res_name] = gm.predict(X)
# print(df_main[col_res_name])

#For plotting results
plot_x_col ='Ic'
plot_model_vs_stratigraphy(df_main[df_main[col_res_name].notna()],plot_x_col,col_res_name,feature_str,output_folder_path,
                           location_id+'-CPT_GMM-prediction_c'+str(chosen_K)+'_'+plot_x_col,interactive=True,palette=palette_10)
plot_x_col ='SCPT_RES'
plot_model_vs_stratigraphy(df_main[df_main[col_res_name].notna()],plot_x_col,col_res_name,feature_str,output_folder_path,
                           location_id+'-CPT_GMM-prediction_c'+str(chosen_K)+'_'+plot_x_col,interactive=True,palette=palette_10)


###-----Clustering with Spectral Clustering -----  ###

# spec_cluster = SpectralClustering(n_clusters=5,affinity='nearest_neighbors', n_neighbors=10,assign_labels='cluster_qr')
# df_main['spec_clus_predict_c4'] = spec_cluster.fit_predict(X)
# #For plotting results
# plot_model_vs_stratigraphy(df_main,'Ic','spec_clus_predict_c4',feature_str,output_folder_path,'EOS-all-CPT_Spectral-prediction_c4_Ic.svg')

