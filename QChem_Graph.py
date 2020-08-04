from QChemOutputParser import Parser
import sys
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt
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

def createBarGraph(key, x_axis, y_axis):
    y_pos = np.arange(len(x_axis))
    plt.bar(x_axis, y_axis, align='center', alpha=0.5)
    #plt.xticks(x_axis, y_axis)
    plt.ylabel(key)
    plt.title(f'{key} Bar Graph')
    plt.show()


if __name__ == "__main__":
    Parser = Parser()
    key = 'LOMO_Hartree'
    try:
        f = open('fileNames.txt', "r")
        fileNames = f.readlines()
    except OSError:
        print("Could not find file")
        sys.exit()

    x_axis = []
    y_axis = []

    for line in fileNames:
        #print(line.strip())
        input_file = line.strip()
        if input_file.endswith('.out'):
            mol_name = input_file[:-4]
        output_file = input_file.replace('.out', '.analysis')
        data_dic1, data_dic2 = Parser.parse([], input_file, output_file)



        if key in data_dic1:
            print(data_dic1[key])
            y_axis.append(data_dic1[key])
            if 'jobtype' in data_dic1:
                mol_name += data_dic1['jobtype']
                x_axis.append(mol_name)
            else:
                continue
            mol_name = input_file[:-4]


        else:
            print('This job does not have the specified key')
            # y_axis.append(0)
        if key in data_dic2:
            y_axis.append(data_dic2[key])
            print(data_dic2[key])
            if 'jobtype' in data_dic2:
                mol_name += data_dic2['jobtype']
                x_axis.append(mol_name)
            else:
                continue
        else:
            print('This job does not have the specified key')
            # y_axis.append(0)

    print(x_axis)
    print(y_axis)

    #createBarGraph(key, x_axis, y_axis)







