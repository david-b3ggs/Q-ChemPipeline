from ase.io import read, write
import sys
import os.path
import matplotlib.pyplot as plt
from os import path
import argparse
import numpy as np


# defining list that will be used for input variation
jobtype_l = ['opt', 'freq']
gui_l = [1,2,3]
basis_l = ['6-31G*']
method_l = ['b3lyp', 'hf', 'pbe0', 'wb97x-d3', 'wb97x-v']
max_scf_cylces_l = [400, 800, 1000]
max_diis_cycles_l = [400, 600, 800, 1000]
geo_opt_max_cycles_l = [400, 600 ,551, 800, 1000]
scf_convergence_l = [8, 9, 10, 11]


#Job you run the most often?

class switch(object):
    value = None
    def __new__(class_, value):
        class_.value = value
        return True

def case(*args):
    return any((arg == switch.value for arg in args))


class Job:
    l_iterator = 0

    def __init__(self, jobtype = 'opt', gui = '2', basis = '6-31G*', method = 'b3lyp', max_scf_cycles = '400',
                 max_diis_cycles = '400', geom_opt_max_cycles = '400', scf_convergence = '8'):
        self.jobtype = jobtype
        self.gui = gui
        self.basis = basis
        self.method = method
        self.max_scf_cycles = max_scf_cycles
        self.max_diis_cycles = max_diis_cycles
        self.geom_opt_max_cycles = geom_opt_max_cycles
        self.scf_convergence = scf_convergence

    # Function that is used to extract data from an XYZ files, both coordinates and elements.
    # Returns a list of list containing both, where the elements are appended to the end

    def readXYZ(self, file):

        file.readline()
        file.readline()

        coordinate_list = file.readlines()[2:]
        return coordinate_list

    def printJob(self):
        print('jobtype is {self.jobtype}')
        print('gui is {self.gui}')
        print('basis is {self.basis}')
        print('method is  {self.method}')
        print('max_scf_cycles is {self.max_scf_cycles}')
        print('max_diis_cycles is {self.max_diis_cycles}')
        print('geom_opt_max_cycles is {self.geom_opt_max_cycles}')
        print('scf_convergence is {self.scf_convergence}')

    # Need to ask about multiple jobs in next meeting. Like when the occur outside of opt => freq
    def createStartInputFile(self, mol_name, coordinates):
        file = open("./" + mol_name + "/" + mol_name + ".in", "w+")
        self.make_executable("./" + mol_name + "/" + mol_name + ".in")
    # print molecule, then rem, then comments
        file.write("$molecule\n 0 1\n")
        for x in coordinates:
            file.write(x)
        file.write("$end \n")

        file.write("$rem\n")
        file.write("jobtype " + self.jobtype + "\n")
        file.write("gui " + self.gui + '\n')
        file.write("basis " + self.basis + '\n')
        file.write("method " + self.method + '\n')
        file.write("max_scf_cycles " + self.max_scf_cycles + '\n')
        file.write("max_diis_cycles " + self.max_diis_cycles + '\n')
        file.write("geom_opt_max_cycles " + self.geom_opt_max_cycles + '\n')
        file.write("$end\n")

        file.write("@@@\n")
        file.write("$molecule\nread\n$end\n")

        file.write("$rem\n")
        file.write("jobtype freq" + "\n")
        file.write("gui " + self.gui + '\n')
        file.write("basis " + self.basis + '\n')
        file.write("max_scf_cycles " + self.max_scf_cycles + '\n')
        file.write("exchange b3lyp\n")
        file.write("$end\n")

        file.close()
        return file.name

    # Function that creates the external_charges section for an SP file.
    # Element is the specific element you are looking for
    # First_axis parameter determines which axis will be used to create the distance
    # Second_axis determines which axis to apply the distance
    # If the visualizier needs to be used, change show_plot to True.

    def external_charges(self, filename, element, first_axis, second_axis, show_plot=False):
        try:
            a = read(filename)
        except FileNotFoundError:
            print('Not such file exists')
            exit(3)

        index = []
        ax = plt.axes(projection="3d")

        symbol_list = a.get_chemical_symbols()

        for x in range(len(symbol_list)):
            if (symbol_list[x] == element):
                index.append(x)

        coordinate_list = a.get_positions().tolist()
        if first_axis == 'x-axis'.lower():
            index_finder = 0
        elif first_axis == 'y-axis'.lower():
            index_finder = 1
        elif first_axis == 'z-axis'.lower():
            index_finder = 2
        else:
            print('Not a valid parameter')
            exit(5)

        outfile = '$external_charges\n'
        new_charge = abs(coordinate_list[index[0]][index_finder]) + abs(coordinate_list[index[1]][index_finder])

        for x in range(len(index)):
            ax.scatter3D(coordinate_list[index[x]][0], coordinate_list[index[x]][1], coordinate_list[index[x]][2])
            if second_axis == 'x-axis'.lower():
                x_charge = round(coordinate_list[index[x]][0] + new_charge, 4)
                y_charge = round(coordinate_list[index[x]][1], 4)
                z_charge = round(coordinate_list[index[x]][2], 4)
            elif second_axis == 'y-axis'.lower():
                x_charge = round(coordinate_list[index[x]][0], 4)
                y_charge = round(coordinate_list[index[x]][1] + new_charge, 4)
                z_charge = round(coordinate_list[index[x]][2], 4)
            elif second_axis == 'z-axis'.lower():
                x_charge = round(coordinate_list[index[x]][0], 4)
                y_charge = round(coordinate_list[index[x]][1], 4)
                z_charge = round(coordinate_list[index[x]][2] + new_charge, 4)

            ax.scatter3D(x_charge, y_charge, z_charge, c='yellow')
            outfile += '{0: <11.4f}'.format(x_charge)
            outfile += '{0: <11.4f}'.format(y_charge)
            outfile += '{0: <11.4f}'.format(z_charge)
            outfile += '\n'

        outfile += '$end\n'
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('z')
        if show_plot == True:
            plt.show()

        return outfile

    def createSPFile(self, mol_name, coordinates, filename):
        file = open("./" + mol_name + "/" + mol_name + ".in", "w+")
        self.make_executable("./" + mol_name + "/" + mol_name + ".in")
        # print molecule, then rem, then comments
        file.write("$molecule\n 0 1\n")
        for x in coordinates:
            file.write(x)
        file.write("$end \n")

        file.write(self.external_charges(filename, element='Fe', first_axis= 'x-axis', second_axis= 'y-axis'))

        file.write("$rem\n")
        file.write("jobtype " + self.jobtype + "\n")
        file.write("gui " + self.gui + '\n')
        file.write("basis " + self.basis + '\n')
        file.write("method " + self.method + '\n')
        file.write("max_scf_cycles " + self.max_scf_cycles + '\n')
        file.write("max_diis_cycles " + self.max_diis_cycles + '\n')
        file.write("geom_opt_max_cycles " + self.geom_opt_max_cycles + '\n')
        file.write("$end\n")

        file.close()
        return file.name


    # def createCDFTCIFile(self, molName, coordinates):

    def make_executable(self, path):
        mode = os.stat(path).st_mode
        mode |= (mode & 0o444) >> 2    # copy R bits to X
        os.chmod(path, mode)


    def input_variation(self, param_name, param_value):
        #param_name = param_name.lower()
        if Job.l_iterator >= len(param_value):
            Job.l_iterator = 0

        while switch(param_name):
            if case('jobtype'):
                self.jobtype = param_value[Job.l_iterator]
                break
            if case('gui'):
                self.gui = param_value[Job.l_iterator]
                break
            if case('basis'):
                self.basis = param_value[Job.l_iterator]
                break
            if case('method'):
                print(param_value[Job.l_iterator])
                self.method = param_value[Job.l_iterator]
                break
            if case('max_scf_cycles'):
                self.max_scf_cycles = param_value[Job.l_iterator]
                break
            if case('max_diis_cycles'):
                self.max_diis_cycles = param_value[Job.l_iterator]
                break
            if case('geom_opt_max_cycles'):
                self.geom_opt_max_cycles = param_value[Job.l_iterator]
                break
            if case('scf_convergence'):
                self.scf_convergence = param_value[Job.l_iterator]
                break
            print("Please Enter a valid parameter")
        Job.l_iterator = Job.l_iterator + 1




# def input_variation(param_name):
#     param_name = param_name.lower()
#     switcher = {
#         'jobtype': 'Whatever',
#         'gui': 'Change gui',
#         'basis': 'Change basis',
#         'method': 'Change method',
#         'max_scf_cycles': 'Change scf cycles',
#         'max_diis_cycles': 'Change diis cycles',
#         'geo_opt_max_cycles': 'Change geom_opt cycles',
#         'scf_convergence': 'Change scf convergence'
#     }
#     Test = Job(param_name = param_name)
#     switcher.get(param_name, 'Invalid parameter')
#     return Test


if __name__ == '__main__':
    sys.path.append(".")
    Test = Job()

    for x in range(10):
        print('JOB {x}')
        Test.input_variation(param_name='method', param_value=method_l)
        Test.printJob()
