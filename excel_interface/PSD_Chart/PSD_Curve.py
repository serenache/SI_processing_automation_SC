import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.ticker import FormatStrFormatter

hfont = {'fontname': 'Palatino Linotype', 'style': 'italic'}
fig = plt.figure(figsize=(14, 10))
ax1 = fig.add_axes((0, 0, 1, 1))
layout = 111
data_x = [
    [0.00253781, 0.00492637, 0.00612101, 0.00728499, 0.00887775, 0.0100419, 0.0107167, 0.0243597, 0.0367928, 0.0513465,
     0.0643828, 0.0786252, 0.0883587,
     0.114089, 0.254947, 0.466226, 0.662241, 0.794005, 0.910438, 1.07284, 3.88267, 5.15996, 6.28508, 9.87324],
    [76.20, 50.80, 38.10, 25.40, 19.02, 9.53, 4.76, 2.00, 1.18, 0.59, 0.43, 0.30, 0.16, 0.07, 0.06, 0.04, 0.03, 0.02,
     0.01, 0.01, 0.01, 0.01, 0.00, 0.00, 0.00, 0.00]]
data_y = [
    [27.9538, 31.1018, 34.1238, 36.894, 40.5456, 43.9454, 43.693, 46.3182, 49.8265, 53.08, 55.4542, 55.4343, 69.9013,
     72.277, 73.914, 76.0546, 79.8321, 84.9948, 89.1501, 95.446, 96.957, 97.9643, 98.468, 100],
    [100.00, 100.00, 100.00, 100.00, 100.00, 100.00, 100.00, 97.86, 88.43, 66.01, 50.46, 40.50, 33.28, 25.75, 24.50,
     23.13, 22.78, 21.41, 20.38, 19.69, 19.69, 17.98, 15.57, 14.54, 13.51, 10.66]]
labels = ['PSD_A', 'PSD_B']
chart_set = [12.0]
ax = fig.add_subplot(layout)
for i in range(len(data_x)):
    ax.plot(data_x[i], data_y[i], label=labels[i])
ax.set_xlabel('Particle Size [mm]', fontsize=int(chart_set[-1]), labelpad=5)
ax.set_xscale('log')
ax.set_xlim(0.001, 100.0)
ax.xaxis.set_major_formatter(FormatStrFormatter('%1.3g'))
ax.grid(axis='x', which='major', color='#919191', linestyle='-', alpha=0.3)
ax.grid(axis='x', which='minor', color='#999999', linestyle='-', alpha=0.3)
ax.xaxis.tick_top()
ax.xaxis.set_label_position('top')

ax.set_ylabel('Percentage Passing [%]', fontsize=int(chart_set[-1]), labelpad=0)
ax.set_yscale('linear')
ax.set_ylim(0, 100.0)
ax.yaxis.set_major_formatter(FormatStrFormatter('%1.0f'))
ax.yaxis.set_major_locator(plt.MultipleLocator(10))
ax.yaxis.set_minor_locator(plt.MultipleLocator(5))
ax.grid(axis='y', which='major', color='#919191', linestyle='-', alpha=0.3)
ax.grid(axis='y', which='minor', color='#999999', linestyle='-', alpha=0.3)
ax.tick_params(axis='both', which='major', labelsize=int(chart_set[-1]))

box = ax.get_position()
box.x0 = 0.05
box.x1 = 0.99
box.y1 = 0.94
leg_w = 0.08
x1 = box.x1
ax.set_position([box.x0, box.y0, box.x1 - box.x0 - leg_w, box.y1 - box.y0])

box = ax.get_position()
handles, labels = ax.get_legend_handles_labels()
leg = ax.legend(labels, loc=3, borderaxespad=0, prop={"size": int(chart_set[-1])})
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
    t.set_position((box[0][0] + 0.5 * (width_box - width_txt), 0.45 * (box[0][1] + box[1][1])))

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
    t.set_position((box[0][0] + 0.5 * (width_box - width_txt), 0.45 * (box[0][1] + box[1][1])))

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
    t.set_position((box[0][0] + 0.5 * (width_box - width_txt), 0.45 * (box[0][1] + box[1][1])))

# plt.show()

plt.savefig('test.jpg')