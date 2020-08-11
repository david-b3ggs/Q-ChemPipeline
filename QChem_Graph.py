from QChemOutputParser import Parser
import sys
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt
import os.path
#List of "keys" for the dictionaries return by the parser

# 'Final_Hatree_Energy'
# 'Final_EV_Energy'
# 'Max_Mode'
# 'HOMO_Hartree'
# 'HOMO_eV'
# 'HOMO-1_Hartree'
# 'HOMO-1_eV'
# 'LOMO_Hartree'
# 'LOMO_eV'
# 'LOMO+1_Hartree'
# 'LOMO+1_eV'
# 'Energy_Gap_Hartree'
# 'Energy_Gap_eV'

# .png .eps

# Function used to simplified the creation of Bar Graphs taking in the information for both axis
def createBarGraph(key, x_axis, y_axis, show_plot = False):
    y_pos = np.arange(len(x_axis))
    plt.bar(x_axis, y_axis, align='center', alpha=0.5)
    plt.ylabel(key)
    plt.title(f'{key} Bar Graph')
    directory = "BarGraph_Figures"

    path = os.path.join(os.getcwd(), directory)
    print(path)

    try:
        os.mkdir(path)
    except OSError as error:
        print("Directory already exists")
    filename = key + '.png'
    plt.savefig(path + "/" + filename)
    if show_plot == True:
        plt.show()




# Function that will extract data from a Parser object depending on the key selected. (Possible keys shown above)
# Returns both the x and y axis of data

def BarGraphInfoExtracter(key, Parser):
    try:
        f = open('fileNames.txt', "r")
        fileNames = f.readlines()
    except OSError:
        print("Could not find file")
        sys.exit()

    x_axis = []
    y_axis = []

    directory = "OutputFiles"

    path = os.path.join(os.getcwd(), directory)
    print(path)

    try:
        os.mkdir(path)
    except OSError as error:
        print("Directory already exists")

    files = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for file in f:
            if '.out' in file:
                mol_name = file[:-4]
                output_file = file.replace('.out', '.analysis')
                data_dic1, data_dic2 = Parser.parse([], file, output_file)

                if key in data_dic1:
                    #print(data_dic1[key])
                    y_axis.append(data_dic1[key])
                    if 'jobtype' in data_dic1:
                        mol_name += data_dic1['jobtype']
                        x_axis.append(mol_name)
                    else:
                        continue
                    mol_name = file[:-4]


                else:
                    print('This job does not have the specified key')
                    # y_axis.append(0)
                if key in data_dic2:
                    y_axis.append(data_dic2[key])
                    #print(data_dic2[key])
                    if 'jobtype' in data_dic2:
                        mol_name += data_dic2['jobtype']
                        x_axis.append(mol_name)
                    else:
                        continue
                else:
                    #print('This job does not have the specified key')
                    continue

    # for f in files:
    #     print(f)

    print(x_axis)
    print(y_axis)
    return x_axis, y_axis

if __name__ == "__main__":
    Parser = Parser()
    key = 'Max_Mode'
    x_axis, y_axis = BarGraphInfoExtracter(key=key, Parser= Parser)
    createBarGraph(key, x_axis, y_axis)











