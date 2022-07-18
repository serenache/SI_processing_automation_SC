import csv
import xlrd
from os import getcwd
from gcg_template import gcg_graph
import gcg_plot_functions
import gc
import os

# read excel interface
programme_folder_path = os.getcwd()
input_excel_path=os.path.join(programme_folder_path, '../Input_files/Interfacev2.xls')
wb = xlrd.open_workbook(input_excel_path, formatting_info=True)
sht = wb.sheet_by_name('GRAPHS')
input_data_files_path=sht.cell_value(0, 1)
output_folder_path=sht.cell_value(1, 1)
ext_fig=sht.cell_value(2, 1)

#global variable
plots = []
sub_charts = []


#get dictionary of the GCG template page
def get_GCG_template_dict():
    i=3
    client=sht.cell_value(i,1)
    project = sht.cell_value(i+1, 1)
    clientN = sht.cell_value(i+2, 1)
    projectN=sht.cell_value(i+3, 1)
    issue=sht.cell_value(i+4, 1)
    date=sht.cell_value(i+5, 1)
    template_dict = {'client': client, 'project': project, 'clientN': clientN,
                      'projectN': projectN, 'issue': issue, 'date': date}
    return template_dict

# check if isnumber
def isnumber(s):
    try:
        float(s)
        return 0
    except ValueError:
        return 1

def get_pageNmax(plots,sub_charts):
    for i in range (15,sht.nrows):
        #check column 1 - Page
        if sht.cell_value(i,0) != '':
            if len(sub_charts) != 0:
                sub_charts.append(i)
                plots.append(sub_charts)
            sub_charts=[]
        if sht.cell_value(i,1) != '':
            sub_charts.append(i)
    sub_charts.append(i+1)
    plots.append(sub_charts)
    pageNmax = len(plots)
    print(pageNmax)
    return pageNmax

def get_chart_set():
    chart_lin = plot_lines[chartN]
    linA = plot_lines[chartN]
    linB = plot_lines[chartN + 1]
    seriesN = linB - linA
    print(f"#Chart starting on line {chart_lin + 1}")
    layout = int(sht.cell_value(chart_lin, 1))
    chart_set = []
    for i in range(15, 34):
        chart_set.append(sht.cell_value(rowx=chart_lin, colx=i))
    chart_set.append(sht.cell_value(rowx=chart_lin, colx=2))  # font setting


#main flow
template_dict=get_GCG_template_dict()
pageNmax=get_pageNmax(plots,sub_charts)

#Loop going through each page
for pageN in range(pageNmax):
    print("\nNew Page")
    plot_lines = plots[pageN]
    page_lin = plot_lines[0]
    page_size = sht.cell_value(page_lin,0)
    maincaption= sht.cell_value(page_lin,3)
    subcaption = sht.cell_value(page_lin, 4)
    figN=maincaption= sht.cell_value(page_lin,5)

    # add to template dict
    template_dict.update({'size':page_size,'maincaption':maincaption,
                               'subcaption':subcaption, 'figN':figN})

    # get chart type
    chart_type=sht.cell_value(page_lin,6)
    # plot according to different chart type. Haven't added for CPT yet.

    if chart_type=='CPT':
        sub_chart_type=sht.cell_value(page_lin,7)
        #read processed excel as dataframe
        #filter desired location
        #specify column name --> create plot list
        #specify label name --> create name list
        # probably need to create a big group name list --> create x-y label list
        #create xy-limit list
        #create multiplier list --> need to add
        #create colour list
        # call function from cpt figure

        pass

    if chart_type=='xy-graph' or chart_type=='PSD':
        #Create page class
        page = gcg_graph(**template_dict)
        page.fig()

        #Loop going through each chart in page
        for chartN in range(len(plot_lines)-1):
            chart_lin = plot_lines[chartN]
            linA = plot_lines[chartN]
            linB = plot_lines[chartN+1]
            seriesN = linB-linA
            print(f"#Chart starting on line {chart_lin+1}")
            layout = int(sht.cell_value(chart_lin,1))
            chart_set =[]
            for i in range(15,34):
                chart_set.append(sht.cell_value(rowx=chart_lin, colx=i))
            chart_set.append(sht.cell_value(rowx=chart_lin, colx=2)) #font setting
            X_data=[]
            Y_data=[]
            Label_data=[]
            Style_data=[]
            #Go through each data line
            for i in range(linA, linB):
                print(f"##Data Source {sht.cell_value(i,8)}")
                data_lim = sht.cell_value(i,12)[1:-1].split(":")
                if data_lim[0]=="":
                    lin_start=0
                else:
                    lin_start=int(data_lim[0])
                if sht.cell_value(i,9)=="-":
                    operations = sht.cell_value(i, 13)
                    X_data2, Y_data2, labels, styles = eval('gcg_plot_functions.'+operations[:-1]+','+str(lin_start)+','+str(sht.cell_value(i, 14))+','+'r"'+input_data_files_path+'"'+')')
                    for j in range(len(styles)):
                        Label_data.append(labels[j])
                        Style_data.append(styles[j])
                        X_data.append(X_data2[j])
                        Y_data.append(Y_data2[j])
                else:
                    Label_data.append(sht.cell_value(i, 11))
                    Style_data.append(sht.cell_value(i, 14))
                    try:
                        xcol = int(sht.cell_value(i, 9).split("-")[0])
                        ycol = int(sht.cell_value(i, 10).split("-")[0])
                    except:
                        xcol = int(sht.cell_value(i, 9))
                        ycol = int(sht.cell_value(i, 10))
                    X_data2 = []
                    Y_data2 = []
                    f = open(os.path.join(input_data_files_path,sht.cell_value(i,8)))
                    wbData = csv.reader(f)
                    data_line_index = 1 #count lines in data file
                    for data_line in wbData:
                        if data_line_index > lin_start:
                            test = isnumber(data_line[xcol-1])+ isnumber(data_line[ycol-1])
                            if test == 0:
                                X_data2.append(float(data_line[xcol-1]))
                                Y_data2.append(float(data_line[ycol-1]))
                            else:
                                break
                        else:
                            data_line_index=data_line_index+1
                    f.close()

                    if data_lim[1]!="":
                        X_data2=eval("X_data2[:"+data_lim[1]+"]")
                        Y_data2=eval("Y_data2[:"+data_lim[1]+"]")
                    X_data.append(X_data2)
                    Y_data.append(Y_data2)

            page.chart(layout, X_data, Y_data, Label_data, Style_data, chart_set, chart_type)
            if chart_type =='PSD':
                page.PSD_chart(chart_set)

        page.save(output_folder_path, str(pageN), ext_fig)
        del page
        gc.collect()
