import matplotlib
# matplotlib.use('qtagg')
# matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.ticker import FormatStrFormatter
plt.rcParams['figure.dpi'] = 300
import gc
import os


###-----Global variable-----  ###
# project folder path
programme_folder_path = os.getcwd()
# logo path
logo_path = os.path.join(programme_folder_path, '../Source-fig/gcg_logo.png')

class gcg_graph():
    def __init__(self, **kwargs):
        self.G_lines = ['-', '--', '-.', ':','-', '--', '-.', ':','-', '--', '-.', ':','-', '--', '-.', ':','-', '--', '-.', ':','-', '--', '-.', ':','-', '--', '-.', ':']
        self.G_markers = ['.', ',', 'o', 'v', '^', '<', '>', '1', '2', '3', '4', 's', 'p', '*', 'h', 'H', '+', 'x', 'D', 'd', '|', '_']
        self.G_colors = ['k', '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf', 'k', '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        for key, value in kwargs.items():
            setattr(self,key,value)
        pass

    def fig(self):
        hfont = {'fontname': 'Palatino Linotype', 'style': 'italic','fontsize':10.0}
        def get_ax_size(ax):
            bbox = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
            width, height = bbox.width, bbox.height
            width *= fig.dpi
            height *= fig.dpi
            return width, height
        if self.size=='A4-Landscape':
            fig = plt.figure(figsize=(11.69, 8.27))
            fig.patch.set_facecolor('none')
            # fig.patch.set_alpha(0)
            ax1 = fig.add_axes((0,0,1,1))
            # ax1.patch.set_alpha(0.5)
            #ax = fig.add_axes((left, bottom, width, height))
            ax1.set_xlim([0,297.2])
            ax1.set_ylim([0,209.8])
            x0 = 18.5; y0 = 23; x1 = 279.2; y1=184.7;
            ax1.add_patch(Rectangle((x0, y0), x1-x0, y1-y0,linewidth=1.5,edgecolor='k',facecolor='none'))
            x0 = 80.9; x1 = 109.3; y1=49;
            ax1.add_patch(Rectangle((x0, y0), x1-x0, y1-y0,linewidth=1.5,edgecolor='k',facecolor='none'))
            x0 = 109.3; x1 = 253; y1=36;
            ax1.add_patch(Rectangle((x0, y0), x1-x0, y1-y0,linewidth=1.5,edgecolor='k',facecolor='none'))
            y1=49;
            ax1.add_patch(Rectangle((x0, y0), x1-x0, y1-y0,linewidth=1.5,edgecolor='k',facecolor='none'))
            x0 = 253; x1 = 279.2;
            ax1.add_patch(Rectangle((x0, y0), x1-x0, y1-y0,linewidth=1.5,edgecolor='k',facecolor='none'))
            ax1.plot([18.5,279.2],[189.2,189.2],linewidth=1.5,color='k')
            ax1.plot([18.5,279.2],[16.7,16.7],linewidth=1.5,color='k')
            ax1.text(18.5, 13, str(self.clientN)+'/'+str(self.projectN), **hfont)
            ax1.text(18.5, 190, str(self.project), **hfont)
            ax1.text(18.5, 195, str(self.client), **hfont)
            t = ax1.text(250, 13, str(self.issue), **hfont)
            bb = t.get_window_extent(fig.canvas.get_renderer()).transformed(plt.gca().transData.inverted())
            t.set_position((279.2-(bb.x1-bb.x0), 13))
            t = ax1.text(250, 195, str(self.date), **hfont)
            bb = t.get_window_extent(fig.canvas.get_renderer()).transformed(plt.gca().transData.inverted())
            t.set_position((279.2-(bb.x1-bb.x0), 195))
            t = ax1.text(250, 190, 'Geotechnical Consulting Group', **hfont)
            bb = t.get_window_extent(fig.canvas.get_renderer()).transformed(plt.gca().transData.inverted())
            t.set_position((279.2-(bb.x1-bb.x0), 190))
            ax1.text(110, 45, str(self.client), **hfont)
            ax1.text(110, 38, str(self.project), **hfont)
            ax1.text(110, 32, str(self.maincaption), **hfont)
            ax1.text(110, 25, str(self.subcaption), **hfont)
            ax1.text(257, 35, 'Figure '+str(self.figN), **hfont)
            ax2 = fig.add_axes((0.265, 0.116, 0.111, 0.111))
            ax2.imshow(plt.imread(logo_path))
            ax2.set_axis_off()
            x0=0.14
            y0=0.30
            x1=0.92
            y1=0.85
        elif self.size=='A4-Portrait':
            fig = plt.figure(figsize=(8.27, 11.69))
            fig.patch.set_facecolor('none')
            # fig.patch.set_alpha(0)
            ax1 = fig.add_axes((0,0,1,1)) #ax = fig.add_axes((left, bottom, width, height))
            # ax1.patch.set_alpha(0.5)
            ax1.set_xlim([0,297.2])
            ax1.set_ylim([0,209.8])
            x0 = 35.5; y0 = 16.5; x1 = 262; y1=192;
            ax1.add_patch(Rectangle((x0, y0), x1-x0, y1-y0, linewidth=1.5, edgecolor='k', facecolor='none'))
            x0 = 35.5; x1 = 76; y1=34.4;
            ax1.add_patch(Rectangle((x0, y0), x1-x0, y1-y0, linewidth=1.5, edgecolor='k', facecolor='none'))
            x0 = 76; x1 = 227;
            ax1.add_patch(Rectangle((x0, y0), x1-x0, y1-y0, linewidth=1.5, edgecolor='k', facecolor='none'))
            x0 = 227; x1 = 262;
            ax1.add_patch(Rectangle((x0, y0), x1-x0, y1-y0,linewidth=1.5,edgecolor='k',facecolor='none'))
            x0 = 76; x1 = 227; y1=25.5;
            ax1.add_patch(Rectangle((x0, y0), x1-x0, y1-y0,linewidth=1.5,edgecolor='k',facecolor='none'))

            y1 = 195;
            ax1.plot([35.5,262],[y1,y1], linewidth=1.5, color='k')
            y1 = 11.7;
            ax1.plot([35.5,262],[y1,y1], linewidth=1.5, color='k')

            ax1.text(35.5, 9, str(self.clientN)+'/'+str(self.projectN), **hfont)
            ax1.text(35.5, 195.5, str(self.project), **hfont)
            ax1.text(35.5, 199, str(self.client), **hfont)

            t = ax1.text(250, 9, str(self.issue), **hfont)
            bb = t.get_window_extent(fig.canvas.get_renderer()).transformed(plt.gca().transData.inverted())
            t.set_position((262-(bb.x1-bb.x0), 9))

            t = ax1.text(250, 199, str(self.date), **hfont)
            bb = t.get_window_extent(fig.canvas.get_renderer()).transformed(plt.gca().transData.inverted())
            t.set_position((262-(bb.x1-bb.x0), 199))

            t = ax1.text(250, 195.5, 'Geotechnical Consulting Group', **hfont)
            bb = t.get_window_extent(fig.canvas.get_renderer()).transformed(plt.gca().transData.inverted())
            t.set_position((262-(bb.x1-bb.x0), 195.5))

            x0 = 78
            ax1.text(x0, 31, str(self.client), **hfont)
            ax1.text(x0, 27, str(self.project), **hfont)
            ax1.text(x0, 22, str(self.maincaption), **hfont)
            ax1.text(x0, 18, str(self.subcaption), **hfont)

            ax1.text(232, 24, 'Figure '+str(self.figN), **hfont)
            ax2 = fig.add_axes((0.13, 0.065, 0.111, 0.111))
            ax2.imshow(plt.imread(logo_path))
            ax2.set_axis_off()
            x0=0.20
            y0=0.21
            x1=0.86
            y1=0.90
        self.ax1=ax1
        self.fig = fig
        self.fig.subplots_adjust(left=x0, bottom=y0, right=x1, top=y1, wspace=0.13, hspace=0.13)

    def chart(self, layout, data_x, data_y, labels, styles, chart_set,chart_type):
        fig=self.fig
        ax = fig.add_subplot(layout)
        for i in range(len(data_x)):
            if styles[i]=="":
                style_ind = i
            else:
                style_ind=int(styles[i])
            ax.plot(data_x[i], data_y[i], color = self.G_colors[style_ind], marker=self.G_markers[style_ind], markevery=20, label=labels[i])

        if chart_type=='xy-graph':
            leg_w = 0.18
            title_thk=0.0

        if chart_type=='PSD':
            leg_w = 0.1
            title_thk=0.025 #for PSD only as need to put x axis on top



        ax.set_xlabel(chart_set[0], fontsize=int(chart_set[-1]), labelpad=0)
        ax.set_xscale(chart_set[1])
        if chart_set[2]!='-' and chart_set[3]!='-': ax.set_xlim(float(chart_set[2]), float(chart_set[3]))
        if chart_set[2]!='-' and chart_set[3]=='-': ax.set_xlim(float(chart_set[2]), None)
        if chart_set[2]=='-' and chart_set[3]!='-': ax.set_xlim(None, float(chart_set[3]))
        if chart_set[4]!='-': ax.xaxis.set_major_formatter(FormatStrFormatter(chart_set[4]))
        if chart_set[5]!='-': ax.xaxis.set_major_locator(plt.MultipleLocator(float(chart_set[5])))
        if chart_set[6]!='-': ax.xaxis.set_minor_locator(plt.MultipleLocator(float(chart_set[6])))
        if chart_set[7]=='YES':ax.grid(axis = 'x', which='major', color='#919191', linestyle='-', alpha=0.3)
        if chart_set[8]=='YES':ax.grid(axis = 'x', which='minor', color='#999999', linestyle='-', alpha=0.3)

        ax.set_ylabel(chart_set[9], fontsize=int(chart_set[-1]), labelpad=0)
        ax.set_yscale(chart_set[10])
        if chart_set[11]!='-' and chart_set[12]!='-': ax.set_ylim(float(chart_set[11]), float(chart_set[12]))
        if chart_set[11]!='-' and chart_set[12]=='-': ax.set_ylim(float(chart_set[11]), None)
        if chart_set[11]=='-' and chart_set[12]!='-': ax.set_ylim(None, float(chart_set[12]))
        if chart_set[13]!='-': ax.yaxis.set_major_formatter(FormatStrFormatter(chart_set[13]))
        if chart_set[14]!='-': ax.yaxis.set_major_locator(plt.MultipleLocator(float(chart_set[14])))
        if chart_set[15]!='-': ax.yaxis.set_minor_locator(plt.MultipleLocator(float(chart_set[15])))
        if chart_set[16]=='YES':ax.grid(axis = 'y', which='major', color='#919191', linestyle='-', alpha=0.3)
        if chart_set[17]=='YES':ax.grid(axis = 'y', which='minor', color='#999999', linestyle='-', alpha=0.3)
        ax.tick_params(axis='both', which='major', labelsize=int(chart_set[-1]))

        box = ax.get_position()
        x1 = box.x1
        ax.set_position([box.x0, box.y0, box.x1 - box.x0 - leg_w, box.y1 - box.y0-title_thk])
        box = ax.get_position()
        handles, labels = ax.get_legend_handles_labels()
        #labels = ['\n'.join(wrap(l, 16)) for l in labels]
        leg = ax.legend(labels, loc=3, borderaxespad=0, prop={"size":int(chart_set[-1])})
        fig.canvas.draw()
        leg_box = fig.transFigure.inverted().transform(leg.get_window_extent())
        leg_dy = leg_box[1][1] - leg_box[0][1]
        leg_coord = ax.transAxes.inverted().transform(fig.transFigure.transform((x1 + 0.005 - leg_w, box.y1 - leg_dy)))
        leg = ax.legend(labels, bbox_to_anchor=leg_coord, loc=3, borderaxespad=0)
        leg.get_frame().set_edgecolor('k')
        leg.get_frame().set_facecolor('white')
        leg.get_frame().set_alpha(1)
        leg.get_frame().set_linewidth(0.5)
        leg.get_frame().set_boxstyle('Square', pad=0.0)

        if chart_set[18] == 'YES':
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            corner1 = ax.transData.transform((xlim[0], ylim[0]))
            corner2 = ax.transData.transform((xlim[1], ylim[1]))
            dx_screen = corner2[0] - corner1[0]
            dy_screen = corner2[1] - corner1[1]
            dx_data = xlim[1] - xlim[0]
            dy_data = ylim[1] - ylim[0]
            x1 = xlim[0] + dy_data * dx_screen / dy_screen
            if x1 > xlim[1]:
                ax.set_xlim(xlim[0], x1)
            else:
                ax.set_ylim(-0.5 * dx_data * dy_screen / dx_screen, 0.5 * dx_data * dy_screen / dx_screen)

        self.ax=ax
        self.fig=fig

    def PSD_chart(self, chart_set):
        fig=self.fig
        ax=self.ax
        ax1=self.ax1
        for line in ax.lines:
            line.set_marker(None)
        ax.xaxis.tick_top()
        ax.xaxis.set_label_position('top')
        ax.xaxis.set_major_formatter(FormatStrFormatter('%1.3g'))

        ax.yaxis.set_major_formatter(FormatStrFormatter('%1.0f'))
        ax.yaxis.set_major_locator(plt.MultipleLocator(10))
        ax.yaxis.set_minor_locator(plt.MultipleLocator(5))

        grainsizes = [0.002, 0.0063, 0.02, 0.063, 0.2, 0.63, 2, 6.3, 20, 63]
        names = ['fine', 'medium', 'coarse', 'fine', 'medium', 'coarse', 'fine', 'medium', 'coarse']
        for i in range(-1 + len(grainsizes)):
            box = ax.transData.transform(
                [(grainsizes[i], -5), (grainsizes[i + 1], 0)])  # transfor ax coordinate to display coordinates
            box = ax1.transData.inverted().transform(box)  # transform display coordinates to ax1 coordinates
            ax1.add_patch(Rectangle(box[0], (box[1] - box[0])[0], (box[1] - box[0])[1], linewidth=0.5, edgecolor='k',
                                    facecolor='none'))  # post in ax1
            t = ax1.text(box[0][0], box[0][1], names[i], fontsize=int(chart_set[-1]))
            width_box = box[1][0] - box[0][0]
            txt = t.get_window_extent(fig.canvas.get_renderer())
            txt = ax1.transData.inverted().transform(txt)
            width_txt = txt[1][0] - txt[0][0]
            # t.set_position((box[0][0] + 0.5 * (width_box - width_txt), 0.45 * (box[0][1] + box[1][1])))
            t.set_position((box[0][0] + 0.5 * (width_box - width_txt), 0.5 * (box[0][1] + box[1][1])))



        grainsizes = [0.002, 0.063, 2, 63]
        names = ['Silt', 'Sand', 'Gravel']
        for i in range(-1 + len(grainsizes)):
            box = ax.transData.transform(
                [(grainsizes[i], -10), (grainsizes[i + 1], -5)])  # transfor ax coordinate to display coordinates
            box = ax1.transData.inverted().transform(box)  # transform display coordinates to ax1 coordinates
            ax1.add_patch(Rectangle(box[0], (box[1] - box[0])[0], (box[1] - box[0])[1], linewidth=0.5, edgecolor='k',
                                    facecolor='none'))  # post in ax1
            t = ax1.text(box[0][0], box[0][1], names[i], fontsize=int(chart_set[-1]))
            width_box = box[1][0] - box[0][0]
            txt = t.get_window_extent(fig.canvas.get_renderer())
            txt = ax1.transData.inverted().transform(txt)
            width_txt = txt[1][0] - txt[0][0]
            t.set_position((box[0][0] + 0.5 * (width_box - width_txt), 0.5 * (box[0][1] + box[1][1])))

        grainsizes = [0.001, 0.002]
        names = ['Clay']
        for i in range(-1 + len(grainsizes)):
            box = ax.transData.transform(
                [(grainsizes[i], -10), (grainsizes[i + 1], 0)])  # transfor ax coordinate to display coordinates
            box = ax1.transData.inverted().transform(box)  # transform display coordinates to ax1 coordinates
            ax1.add_patch(Rectangle(box[0], (box[1] - box[0])[0], (box[1] - box[0])[1], linewidth=0.5, edgecolor='k',
                                    facecolor='none'))  # post in ax1
            t = ax1.text(box[0][0], box[0][1], names[i], fontsize=int(chart_set[-1]))
            width_box = box[1][0] - box[0][0]
            txt = t.get_window_extent(fig.canvas.get_renderer())
            txt = ax1.transData.inverted().transform(txt)
            width_txt = txt[1][0] - txt[0][0]
            t.set_position((box[0][0] + 0.5 * (width_box - width_txt), 0.5 * (box[0][1] + box[1][1])))




    def show(self):
        plt.show()
    
    def save(self, folder_fig,fname, fext=".png"):
        fpath = os.path.join(folder_fig, fname + fext)
        fig=self.fig
        fig.savefig(fpath)
        plt.clf()
        plt.cla()
        plt.close()
        gc.collect()
