# import library
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import patches
import os
from excel_interface.gcg_template import gcg_graph

###----- use custom mplstyle file to define a template -----###
mpl.style.use('CPT.mplstyle')

###----- static method -----###
###----- function to put the figure produced in GCG's template-----  ###
    # currently I am putting the image already produced in the GCG's frame and adjust its position
def put_figure_in_GCG_Template_and_save(fig_path, template_dict):
    page = gcg_graph(**template_dict)
    page.fig()
    ax = page.fig.add_subplot(1, 1, 1)
    ax.imshow(plt.imread(fig_path))
    ax.set_axis_off()
    box = ax.get_position()
    # print(box.x0, box.y0,box.x1, box.y1)
    ax.set_position([box.x0 - 0.07, box.y0 - 0.06, (box.x1 - box.x0) * 1.13, (box.y1 - box.y0) * 1.13])
    f = page.fig
    return f

###----- function to save figure (here it is static method, not a class method)-----  ###
def savefig(folder_fig, f, fname, fext='.png'):
    """
    Saves figure into default folder_fig (defined globally)
    """
    fpath = os.path.join(folder_fig, fname + fext)
    f.savefig(fpath)
    return

###-----Creating a color dict for all the stratigraphy present in the whole site-----  ###
# so the same geol unit will always have the same colour
# random color list for the stratigraphy (currently there is 15 colours, can add more if needed)
def create_stratigraphy_color_dict(SOIL_PROPERTY):
    random_color_list = ['#585232', '#948A54', '#D8E4BC', '#B3E3C6', '#4F81BD', '#4BACC6', '#CCC0DA', '#B29FF7',
                         '#8064A2',
                         '#DA9694', '#B7423F', '#752B29', '#FFD68B', '#F59E01', '#744B00']
    # random hatch pattern list (hatching is not implemented yet)
    # hatch_pattern_list = ['-', '.', 'x', '\\', '/', '+', '//', '\'', 'o', 'O' ]
    stratigraphy_color_dict = {}
    # hatch_pattern_dict = {}
    for k, soil_block in enumerate(list(SOIL_PROPERTY.ItemKey)):
        stratigraphy_color_dict[soil_block] = random_color_list[k]
        # hatch_pattern_dict[soil_block] = hatch_pattern_list[k]
    return stratigraphy_color_dict

###----- function to plot stratigraphy column -----  ###
def plot_stratigraphy_column(ax2, SOIL_UNIT_TABLE, stratigraphy_color_dict):
    ax2.axis("off")
    for k, soil_block in enumerate(list(SOIL_UNIT_TABLE.GEOL_UNIT)):
        depth_base = SOIL_UNIT_TABLE.iloc[k]['DEPTH_BASE']
        depth_top = SOIL_UNIT_TABLE.iloc[k]['DEPTH_TOP']
        thickness = depth_top - depth_base
        soil_color = stratigraphy_color_dict.get(soil_block)
        # create the rectangle and add patch
        rectangle = patches.Rectangle((0, depth_base), 1, thickness, linewidth=1.5,
                                      edgecolor='black', facecolor=soil_color)
        ax2.add_patch(rectangle)
        # add geol unit label to the rectangle
        rx, ry = rectangle.get_xy()
        cx = rx + rectangle.get_width() / 2.0
        cy = ry + rectangle.get_height() / 2.0
        anno_opts = dict(color='black', xy=(cx, cy),
                         va='center', ha='center', fontsize=10)
        ax2.annotate('{}'.format(soil_block), **anno_opts)
    return

###-----Class CPT figure-----  ###
class CPT_figure():
    #instantiate the class with figure and axs
    def __init__(self,size,fig_type,plot_list):
        self.size=size
        self.fig_type=fig_type
        self.plot_list=plot_list
        # Determine the fig size
        if self.size=='A4-Landscape':
            fig_size = (11.69, 8.27)
        if self.size == 'A4-Portrait':
            fig_size = (8.27, 11.69)

        # instantiate the figure and axs depending on the fig type specified
        if self.fig_type=='single_plot':
            f, axs = plt.subplots(figsize=fig_size)
            axs.invert_yaxis()
        if self.fig_type=='side_by_side':
            f, axs = plt.subplots(
                nrows=1, ncols=len(self.plot_list),  # number of rows and columns of subplots
                sharey=True,  # set the same y axis for subplots
                figsize=fig_size # set that the y axis (depth) is inverted (only need to set here as we share y axis)
            )
            axs[0].invert_yaxis()
        if self.fig_type=='single_plot_with_stratigraphy':
            f, axs = plt.subplots(
                nrows=1, ncols=2,
                gridspec_kw={'width_ratios': [1, 0.1]},
                sharey=True,
                figsize=fig_size
            )
            axs[0].invert_yaxis()
        if self.fig_type=='side_by_side_with_stratigraphy':
            # setting a smaller width for the stratigraphy column
            width_ratio_list = []
            for m in range(len(plot_list)):
                width_ratio_list.append(1)
            # set width ratio for the stratigraphy column
            width_ratio_list.append(0.1)
            # creating a graph space with a row of subplots
            f, axs = plt.subplots(
                nrows=1, ncols=len(plot_list) + 1,  # number of rows and columns of subplots
                gridspec_kw={'width_ratios': width_ratio_list},
                sharey=True,  # set the same y axis for subplots
                figsize=(11.69, 8.27)
            )
            axs[0].invert_yaxis()  # set that the y axis (depth) is inverted (only need to set here as we share y axis)

        self.f=f
        self.axs=axs

    ###----- function to save figures to specific folder-----  ###
    # pre-define format: png
    def savefig(self, folder_fig, fname, fext='.png'):
        """
        Saves figure into default folder_fig (defined globally)
        """
        fpath = os.path.join(folder_fig, fname + fext)
        f=self.f
        f.savefig(fpath)
        return

    ###----- function to plot one graph with depth -----  ###
    def single_plot(self, df, plot_list, color_list, name_list, xy_label_list, xy_limit_list, multiplier_list):
        ax=self.axs
        f=self.f
        for i, plot in enumerate(plot_list):
            x, z = df[plot_list[i]] * float(multiplier_list[i]), df['Depth']
            ax.plot(
                x, z,
                label='{}'.format(name_list[i]),
                ls='-',  # linestyle
                # marker='o', mfc='none',  # marker and marker face color
                color=color_list[i]
            )

        ax.legend(loc='upper right') #bbox_to_anchor=(0.5, 0)
        ax.grid()
        ax.set_xlabel(xy_label_list[0][0])
        ax.set_ylabel(xy_label_list[1][0])
        ax.set_xlim(xy_limit_list[0])
        ax.set_ylim(xy_limit_list[1])
        ax.xaxis.set_ticks_position('top')
        ax.xaxis.set_label_position('top')
        self.axs=ax
        self.f=f



    ###----- function to plot and compare data side by side with depth -----  ###
    def side_by_side(self,df, plot_list, color_list, name_list, xy_label_list, xy_limit_list, multiplier_list):
        axs = self.axs
        f=self.f
        for i, sub_list in enumerate(plot_list):
            ax = axs.flatten()[i]
            for j, plot in enumerate(sub_list):
                x, z = df[sub_list[j]] * float(multiplier_list[i][j]), df['Depth']
                ax.plot(
                    x, z,
                    label='{}'.format(name_list[i][j]),
                    ls='-',  # linestyle
                    # marker='o', mfc='none',  # marker and marker face color
                    color=color_list[i][j]
                )

            ax.set_xlabel(xy_label_list[0][i], fontsize=15)
            if np.isin(i, [0]):  # for plots in first col
                ax.set_ylabel(xy_label_list[1][0], fontsize=15)

            # for all plots
            ax.legend(bbox_to_anchor=(0.5, 0), fontsize=10, borderpad=1)
            ax.grid()
            ax.set_xlim(xy_limit_list[0][i])
            ax.set_ylim(xy_limit_list[1])
            try:
                major_ticks = np.linspace(xy_limit_list[0][i][0], xy_limit_list[0][i][1], 2)
                ax.set_xticks(major_ticks)
                minor_ticks = np.linspace(xy_limit_list[0][i][0], xy_limit_list[0][i][1], 5)
                ax.set_xticks(minor_ticks, minor=True)
                ax.grid(which="minor", alpha=0.6)
            except:
                pass
            ax.xaxis.set_ticks_position('top')
            ax.xaxis.set_label_position('top')
            ax.tick_params(axis='both', which='major', labelsize=15)
        f.tight_layout()  # remove blank space
        self.axs=axs
        self.f=f

    ###----- function to add CPTs from other locations to single plot -----  ###
    # This will only be used for plots without stratigraphy, otherwise it will be confusing
    def add_CPT_to_plot(self, df, plot_list, color_list, name_list, xy_label_list, xy_limit_list, multiplier_list,
                        list_of_other_CPT):
        cleaned_list = [x for x in list_of_other_CPT if str(x) != 'nan']
        fig_type = self.fig_type
        for i, cpt_location in enumerate(cleaned_list):
            option = [cpt_location, np.nan]
            df_selected = df[df['Location_ID'].isin(option)]
            if fig_type == 'single_plot':
                self.single_plot(df_selected, plot_list, color_list, name_list, xy_label_list, xy_limit_list,
                                 multiplier_list)
            if fig_type == 'side_by_side':
                self.side_by_side(df_selected, plot_list, color_list, name_list, xy_label_list, xy_limit_list,
                                  multiplier_list)

    ###----- function to plot single plot, with a stratigraphy column,
    # and horizontal line separating each stratigraphy-----  ###
    def single_plot_with_stratigraphy(self,df, plot_list, color_list, name_list, xy_label_list, xy_limit_list,
                                      multiplier_list,
                                      SOIL_UNIT_TABLE,
                                      stratigraphy_color_dict, classification_dict=None):
        axs = self.axs
        f=self.f
        ax = axs.flatten()[0]  # for the first subplot
        for i, plot in enumerate(plot_list):
            x, z = df[plot_list[i]] * float(multiplier_list[i]), df['Depth']
            ax.plot(
                x, z,
                label='{}'.format(name_list[i]),
                ls='-',  # linestyle
                # marker='o', mfc='none',  # marker and marker face color
                color=color_list[i]
            )

        # plot horizontal line for stratigraphy
        for k, soil_block in enumerate(list(SOIL_UNIT_TABLE.GEOL_UNIT)):
            depth_base = SOIL_UNIT_TABLE.iloc[k]['DEPTH_BASE']
            soil_color = stratigraphy_color_dict.get(soil_block)
            ax.axhline(depth_base, color=soil_color, alpha=0.7, linestyle='-.')

        if classification_dict != None:
            # plot vertical line to define classification boundary
            # get y-limit of the current axes
            bottom, top = ax.get_ylim()
            for a, limit in enumerate(classification_dict['Limit']):
                ax.axvline(limit, color='#A6A6A6', alpha=0.7)
                description = classification_dict['Description'][a]
                ax.text(limit, bottom, description, wrap=True, fontsize=12)

        ax.legend(bbox_to_anchor=(0.5, 0))
        ax.grid()
        ax.set_xlabel(xy_label_list[0][0])
        ax.set_ylabel(xy_label_list[1][0])
        ax.set_xlim(xy_limit_list[0])
        ax.set_ylim(xy_limit_list[1])
        ax.xaxis.set_ticks_position('top')
        ax.xaxis.set_label_position('top')

        # Plotting the stratigraphy column
        ax2 = axs.flatten()[1]
        plot_stratigraphy_column(ax2, SOIL_UNIT_TABLE, stratigraphy_color_dict)
        f.tight_layout()  # remove blank space
        self.axs = axs
        self.f = f

    ###----- function to plot and compare data side by side with depth, with a stratigraphy column,
    # and horizontal line separating each stratigraphy-----  ###
    def side_by_side_with_stratigraphy(self,df, plot_list, color_list, name_list, xy_label_list, xy_limit_list,
                                       multiplier_list,
                                       SOIL_UNIT_TABLE,
                                       stratigraphy_color_dict):
        axs = self.axs
        f=self.f
        # Plotting each subplot
        for i, sub_list in enumerate(plot_list):
            ax = axs.flatten()[i]  # going into the subplot

            # plotting all the data needed in the subplot
            for j, plot in enumerate(sub_list):
                x, z = df[sub_list[j]] * float(multiplier_list[i][j]), df['Depth']
                ax.plot(
                    x, z,
                    label='{}'.format(name_list[i][j]),
                    ls='-',  # linestyle
                    # marker='o', mfc='none',  # marker and marker face color
                    color=color_list[i][j]
                )
            # plot horizontal line for stratigraphy
            for k, soil_block in enumerate(list(SOIL_UNIT_TABLE.GEOL_UNIT)):
                depth_base = SOIL_UNIT_TABLE.iloc[k]['DEPTH_BASE']
                soil_color = stratigraphy_color_dict.get(soil_block)
                ax.axhline(depth_base, color=soil_color, alpha=0.7, linestyle='-.')

            ax.set_xlabel(xy_label_list[0][i], fontsize=15)
            if np.isin(i, [0]):  # for plots in first col
                ax.set_ylabel(xy_label_list[1][0], fontsize=15)

            # for all plots
            ax.legend(bbox_to_anchor=(0.5, 0), fontsize=10)
            ax.grid()
            ax.set_xlim(xy_limit_list[0][i])
            ax.set_ylim(xy_limit_list[1])
            try:
                major_ticks = np.linspace(xy_limit_list[0][i][0], xy_limit_list[0][i][1], 2)
                ax.set_xticks(major_ticks)
                minor_ticks = np.linspace(xy_limit_list[0][i][0], xy_limit_list[0][i][1], 5)
                ax.set_xticks(minor_ticks, minor=True)
                ax.grid(which="minor", alpha=0.6)
            except:
                pass
            ax.xaxis.set_ticks_position('top')
            ax.xaxis.set_label_position('top')
            ax.tick_params(axis='both', which='major', labelsize=15)

        # Plotting the stratigraphy column
        ax2 = axs.flatten()[len(plot_list)]
        plot_stratigraphy_column(ax2, SOIL_UNIT_TABLE, stratigraphy_color_dict)
        f.tight_layout()  # remove blank space
        self.axs = axs
        self.f = f






