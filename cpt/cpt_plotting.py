# Superseded by cpt_figure_class
# Amb trial for interactive plots with bokeh
from bokeh.plotting import figure, show
from bokeh.layouts import gridplot
from bokeh.palettes import Category20c
from bokeh.models import Legend, HoverTool
from bokeh.io import save
from bokeh.models.annotations import Label
from matplotlib.colors import to_rgb, rgb_to_hsv
import os
# itertools handles the cycling through colors
#import itertools
# create a color iterator
#color_iter = itertools.cycle(palette[20])


###----- function to get list of label from dict -----  ###
def get_color_dict(df):
    color_dict = {}
    #set the palette to bokeh Category20b or c
    palette = Category20c[20]
    nb_unique_color = 5
    nb_color_per_plot = 4
    #only 4 color max per location for now,
    i = 0
    for location in df.CPT_name.dropna().unique():
        color_dict[location] = palette[nb_color_per_plot*(i%nb_unique_color):
                                       nb_color_per_plot*((i%nb_unique_color)+1)]
        i+=1
    return color_dict

###----- function to get list of label from dict -----  ###
def get_label_list(code_list,label_dict,option):
    label_list = []
    for i,sub_list in enumerate(code_list):
        #check if nested lists
        if isinstance(sub_list, list):
            label_list.append([])
            for element in sub_list:
                label_list[i].append(label_dict[element][option])
        else:
            label_list.append(label_dict[sub_list][option])
    return label_list

# def get_plot_lists(df_plot,df_series,df_axis,index,single):
#     plot_list = []
#     axis_list = []
#     if single:
#
#     else:
#
#     return plot_list,axis_list

#amb - try interactive plots with bokeh
def single_interactive_plot(df, plot_list, color_dict, name_list, xy_label_list, xy_limit_list, multiplier_list,SOIL_UNIT_TABLE=None,
                                      stratigraphy_color_dict=None):
    #assuming the name and label list are formated for matplotlib (where $ is used for math)
    # name_list_n = [sub.replace('$', '$$') for sub in name_list]
    xy_label_list_n = [[sub.replace('$', '$$') for sub in list] for list in xy_label_list]
    legend_list = []
    fig = []
    fig_width = 600 #150 ppi*6 + legend
    fig_height = 1200 #150ppi*8
    fig.append(figure(
        x_axis_label=xy_label_list_n[0][0],
        y_axis_label=xy_label_list_n[1][0],
        x_axis_location='above',
        width=fig_width,
        height=fig_height,
        sizing_mode='scale_height'
    ))
    fig[0].y_range.flipped = True
    for location in df.CPT_name.dropna().unique():
        for i, plot in enumerate(plot_list):
            #x, z = df[plot_list[i]] * float(multiplier_list[i]), df['Depth']
            x = df.loc[(df.CPT_name==location)|(df.CPT_name.isnull()),plot_list[i]] * float(multiplier_list[i])
            z = df.loc[(df.CPT_name == location)|(df.CPT_name.isnull()), 'Depth']
            #cur_color = next(color_iter)
            line_series = fig[0].line(
                x, z,
                #legend_label= str(location) + ' - ' + name_list[i],
                #color=color_list[i],
                color=color_dict[location][i]
            )
            scatter_series = fig[0].scatter(
                x,z,
                color=color_dict[location][i],
                marker='dot',
                size=12
            )
            legend_list.append((str(location) + ' - ' + name_list[i],
                                      [line_series, scatter_series]))

    legend_0 = Legend(items=legend_list)
    legend_0.click_policy = "hide"
    fig[0].add_layout(legend_0, 'below')
    #fig.add_layout(fig.legend[0], 'right')
    fig[0].add_tools(HoverTool(tooltips=[("(x,y)", "($x, $y)")],muted_policy='ignore'))
    if not(SOIL_UNIT_TABLE is None and stratigraphy_color_dict is None):
        fig.append(plot_interactive_stratigraphy_column(fig[0],fig_height,SOIL_UNIT_TABLE,stratigraphy_color_dict))
    # tools_for_plot = [PanTool(), BoxZoomTool(), WheelZoomTool(), ResetTool(), SaveTool(),HoverTool()]
    return gridplot([fig],sizing_mode='scale_height',toolbar_location='left',merge_tools = True)

def side_by_side_interactive_plot(df, plot_list, color_dict, name_list, xy_label_list, xy_limit_list, multiplier_list,
                                  SOIL_UNIT_TABLE=None, stratigraphy_color_dict=None):
        # assuming the name and label list are formated for matplotlib (where $ is used for math)
        #name_list_n = [[sub.replace('$', '$$') for sub in list] for list in name_list]
        xy_label_list_n = [[sub.replace('$', '$$') for sub in list] for list in xy_label_list]
        fig =[]
        fig_width = 300
        fig_height = 750  # 150ppi*5
        for i, sub_list in enumerate(plot_list):
            fig.append(figure(
                        x_axis_label=xy_label_list_n[0][i],
                        x_axis_location='above',
                        width=fig_width,
                        height=fig_height
                        #sizing_mode='scale_height'
            ))
            fig[i].y_range.flipped = True
            if i==0:  # for plots in first col
                fig[i].yaxis.axis_label = xy_label_list[1][0]
            else:
                fig[i].y_range=fig[0].y_range

            legend_list = []
            for location in df.CPT_name.dropna().unique():
                for j, plot in enumerate(sub_list):
                    #x, z = df[sub_list[j]] * float(multiplier_list[i][j]), df['Depth']
                    x = df.loc[(df.CPT_name == location) | (df.CPT_name.isnull()), sub_list[j]] * float(
                        multiplier_list[i][j])
                    z = df.loc[(df.CPT_name == location) | (df.CPT_name.isnull()), 'Depth']
                    #cur_color = next(color_iter)
                    line_series = fig[i].line(
                        x, z,
                        #legend_label='{}'.format(name_list[i][j]),
                        color=color_dict[location][j]
                        #color=color_list[i][j]
                    )
                    scatter_series = fig[i].scatter(
                        x, z,
                        color=color_dict[location][j],
                        marker='dot',
                        size=12
                    )
                    legend_list.append((str(location) + ' - ' + name_list[i][j],
                                        [line_series, scatter_series]))
            legend_0 = Legend(items=legend_list)
            legend_0.click_policy = "hide"
            fig[i].add_layout(legend_0, 'below')
            fig[i].add_tools(HoverTool(tooltips=[("(x,y)", "($x, $y)")],muted_policy='ignore'))
        if not(SOIL_UNIT_TABLE is None and stratigraphy_color_dict is None):
            fig.append(
                plot_interactive_stratigraphy_column(fig[0], fig_height,
                                                     SOIL_UNIT_TABLE, stratigraphy_color_dict))
        return gridplot([fig],sizing_mode='scale_height',toolbar_location='left',merge_tools = True)

def plot_interactive_stratigraphy_column(ref_fig,fig_height,SOIL_UNIT_TABLE, stratigraphy_color_dict):
    fig = figure(
        x_axis_location='above',
        width=round(fig_height/7),
        height=fig_height, #150ppi*11.69
        #sizing_mode='scale_height'
    )
    fig.y_range = ref_fig.y_range
    fig.y_range.flipped = True
    fig.xaxis.visible = False
    fig.xgrid.visible = False
    for k, soil_block in enumerate(list(SOIL_UNIT_TABLE.UNIQUE_GEOL)):
        depth_base = SOIL_UNIT_TABLE.iloc[k]['DEPTH_BASE']
        depth_top = SOIL_UNIT_TABLE.iloc[k]['DEPTH_TOP']
        #thickness = depth_top - depth_base
        soil_color = stratigraphy_color_dict.get(SOIL_UNIT_TABLE.iloc[k]['GEOL_UNIT'])
        # create the rectangle and add patch
        fig.vbar(x=1,
             bottom = depth_top,
             top= depth_base,
             fill_color = soil_color,
             line_color = 'black')
        #Check how dark the colour is - use whitish font for label on dark
        rgb_color = to_rgb(soil_color)
        # print(sum(rgb_color)/len(rgb_color))
        if sum(rgb_color)/len(rgb_color) < 0.4:
            font_color='ghostwhite'
        else:
            font_color='black'
        # add geol unit label to the rectangle
        label = Label(x=0.75, y=(depth_base+depth_top)/2.0, x_offset=0, y_offset=0,
                      text=SOIL_UNIT_TABLE.iloc[k]['GEOL_UNIT'],
                      text_font_size = '10px',text_color=font_color)
        fig.add_layout(label)
    return fig

def save_interactive_fig(fig, folder_fig, fname, fext='.html'):
    """
    Saves figure into default folder_fig (defined globally)
    """
    fpath = os.path.join(folder_fig, fname + fext)
    save(fig,fpath)
    return