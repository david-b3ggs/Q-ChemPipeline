from pyqchem.structure import Structure
from pyqchem.qchem_core import get_output_from_qchem, create_qchem_input, redefine_calculation_data_filename
import os, sys
import JobClass
import importlib
from pyqchem.errors import OutputError, ParserError
import ast
from ase.io import read, write
import os.path
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
scf_convergence_l = [8, 9, 10 ,11]


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

    def readXYZ(self):
        ap = argparse.ArgumentParser()
        ap.add_argument("inputXYZfile", help='input file')
        ap.add_argument('parameter', help='The parameter you want to vary')
        args = vars(ap.parse_args())

        try:
            a = read(args["inputXYZfile"])
        except FileNotFoundError:
            print('Not such file exists')

        coordinate_list = a.get_positions().tolist()


        element_list = a.get_chemical_symbols()

        for x in range(len(element_list)):
            coordinate_list[x].append(element_list[x])
        return coordinate_list

    def printJob(self):

        # print('jobtype is {}'.format(self.jobtype))
        # print(f'gui is {self.gui}')
        # print(f'basis is {self.basis}')
        # print(f'method is  {self.method}')
        # print(f'max_scf_cycles is {self.max_scf_cycles}')
        # print(f'max_diis_cycles is {self.max_diis_cycles}')
        # print(f'geom_opt_max_cycles is {self.geom_opt_max_cycles}')
        # print(f'scf_convergence is {self.scf_convergence}')
        print('jobtype is {}'.format(self.jobtype))
        print('gui is {}'.format(self.gui))
        print('basis is {}'.format(self.basis))
        print('method is  {}'.format(self.method))
        print('max_scf_cycles is {}'.format(self.max_scf_cycles))
        print('max_diis_cycles is {}'.format(self.max_diis_cycles))
        print('geom_opt_max_cycles is {}'.format(self.geom_opt_max_cycles))
        print('scf_convergence is {}'.format(self.scf_convergence))




    def input_variation(self, param_name, param_value, *args):
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
            if case('geo_opt_max_cycles'):
                self.geom_opt_max_cycles = param_value[Job.l_iterator]
                break
            if case('scf_convergence'):
                self.scf_convergence = param_value[Job.l_iterator]
                break
            print("Please Enter a valid parameter")
            exit(3)
        Job.l_iterator = Job.l_iterator + 1

if __name__ == '__main__':
    Test = Job()
   # Test.printJob()



    ap = argparse.ArgumentParser()
    ap.add_argument("inputXYZfile", help='input file')
    ap.add_argument('parameter', help='The parameter you want to vary')
    #ap.add_argument('param_list', help='The list')

    args = vars(ap.parse_args())

    try:
        a = read(args["inputXYZfile"])
    except FileNotFoundError:
        print('Not such file exists')

    coordinate_list = a.get_positions().tolist()

    element_list = a.get_chemical_symbols()

    #num_of_jobs = input('Please specify the number ojf jobs you want to run ')



    #param = input('Please Enter the parameter you wished to variation')


    molecule = Structure(coordinates=coordinate_list, symbols= element_list, charge=0, multiplicity=1)

    print(molecule)

    txt_input = create_qchem_input(molecule, jobtype=Test.jobtype, gui=Test.gui,basis=Test.basis,method=Test.method,
                                   max_scf_cycles=Test.max_scf_cycles, geom_opt_max_cycles=Test.geom_opt_max_cycles,
                                   scf_convergence=Test.scf_convergence)

    try:
        output = get_output_from_qchem(txt_input, processors=8, force_recalculation=True,
                                       store_full_output=True)
    except OutputError as e:
        output = 'Error'
        print("Calculation ended with errors. Error lines: ")
        print(e.error_lines)
    
    print(output)

    # for x in range(10):
    #     output_filename = args["inputXYZfile"].replace('.xyz', '{}.out'.format(x))
    #     Test2 = Job()
    #     Test2.input_variation(args['parameter'],scf_convergence_l)
    #     Test2.printJob()

    #     l = list(args['parameter']+'_l')
    #     print(l)
    #     #l = ast.literal_eval(l)

    #     #print(l)
    #     #l = method_l
    #     print(method_l[0])
    #     print(output_filename)














