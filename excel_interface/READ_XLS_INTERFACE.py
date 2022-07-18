import csv
import xlrd
from os import getcwd
from gcg_template import gcg_graph
import gcg_plot_functions
import gc

path = getcwd()
wb = xlrd.open_workbook(path+"\Interfacev2.xls", formatting_info=True)

def isnumber(s):
    try:
        float(s)
        return 0
    except ValueError:
        return 1

sht = wb.sheet_by_name('GRAPHS')

plots = []
sub_charts=[]
for i in range (2,sht.nrows):
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

#Loop going through each page
for pageN in range(pageNmax):
    print("\nNew Page")
    plot_lines = plots[pageN]
    page_lin = plot_lines[0]
    page_size = sht.cell_value(page_lin,0)
    
    #Create page class
    page = gcg_graph(page_size)
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
        for i in range(10,29):
            chart_set.append(sht.cell_value(rowx=chart_lin, colx=i))
        chart_set.append(sht.cell_value(rowx=chart_lin, colx=2)) #font setting
        X_data=[]
        Y_data=[]
        Label_data=[]
        Style_data=[]
        #Go through each data line
        for i in range(linA, linB):
            print(f"##Data Source {sht.cell_value(i,3)}")
            data_lim = sht.cell_value(i,7)[1:-1].split(":")
            if data_lim[0]=="":
                lin_start=0
            else:
                lin_start=int(data_lim[0])
            if sht.cell_value(i,4)=="-":
                operations = sht.cell_value(i, 8)
                X_data2, Y_data2, labels, styles = eval('gcg_plot_functions.'+operations[:-1]+','+str(lin_start)+','+str(sht.cell_value(i, 9))+')')
                for j in range(len(styles)):
                    Label_data.append(labels[j])
                    Style_data.append(styles[j])
                    X_data.append(X_data2[j])
                    Y_data.append(Y_data2[j])
            else:
                Label_data.append(sht.cell_value(i, 6))
                Style_data.append(sht.cell_value(i, 9))
                xcol = int(sht.cell_value(i, 4).split("-")[0])
                ycol = int(sht.cell_value(i, 5).split("-")[0])
                X_data2 = []
                Y_data2 = []
                f = open(path+"\data_files\\"+sht.cell_value(i,3))
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
        page.chart(layout, X_data, Y_data, Label_data, Style_data, chart_set)
    page.save(str(pageN),".png")
    del page
    gc.collect()
