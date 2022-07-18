import csv

#This file will contain functions that will be used for specific data processing needs

#In this case we would have to be familiar with it and know that this takes 4 inputs
#file name
#var1 - Column with time of each data point
#var2 - p' at each time

#We should look for a balance between 20 inputs (frequency, tolerance, units, etc) that will have to be in the excel file
#and the user experience in the excel interface

def fun1_M(file, var1, var2, label, M, lin_start, style):
    print('    Plotting function for M')

    var1_col = int(var1.split("-")[0])
    var2_col = int(var2.split("-")[0])

    X_data = []
    Y_data = []
    X_data2 = []
    Y_data2 = []
    f = open('.\data_files\\'+file)
    wbData = csv.reader(f)
    i = 1
    for line in wbData:
        if i > lin_start:
            test = isnumber(line[var1_col-1]) + isnumber(line[var2_col-1])
            if test == 0:
                X_data2.append(float(line[var1_col-1]))
                Y_data2.append(float(line[var2_col-1]))
            else:
                break
        i=i+1
    f.close()
    Label_data = [label]
    Style_data = [style]
    X_data.append(X_data2)
    Y_data.append(Y_data2)
    X_data.append([0,100])
    Y_data.append([0,100*float(M)])
    X_data.append([0,100])
    Y_data.append([0,-100*float(M)])
    Label_data.append("M")
    Label_data.append("")
    Style_data.append(0)
    Style_data.append(0)
    return X_data, Y_data, Label_data, Style_data

def fun1_dp0T(file, var1, var2, label, lin_start, style):
    print('    Plotting function for dp/po x Number of Cycles')
    var1_col = int(var1.split("-")[0])
    var2_col = int(var2.split("-")[0])

    X_data = []
    Y_data = []

    f = open('.\data_files\\'+file)
    wbData = csv.reader(f)
    i = 1
    for line in wbData:
        if i > lin_start:
            test = isnumber(line[var1_col-1])+ isnumber(line[var2_col-1])
            if test == 0:
                time_hours = float(line[var1_col-1])
                time_seconds = time_hours*3600
                cycles = time_seconds/10
                N = cycles%1
                if N < 0.01 or 1-N < 0.01: #filter for integer cycles
                    X_data.append(cycles)
                    Y_data.append(float(line[var2_col-1]))
            else:
                break
        i=i+1
    f.close()
    return [X_data],[Y_data],[label],[style]

def isnumber(s):
    try:
        float(s)
        return 0
    except ValueError:
        return 1