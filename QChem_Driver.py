from pyqchem.structure import Structure
from pyqchem.qchem_core import get_output_from_qchem, create_qchem_input, redefine_calculation_data_filename
from pyqchem.parsers.parser_optimization import basic_optimization
from pyqchem.parsers.parser_frequencies import basic_frequencies
import os, sys
from JobClass import Job, switch, case
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
gui_l = [1, 2, 3]
basis_l = ['6-31G*']
method_l = ['b3lyp', 'hf', 'pbe0', 'wb97x-d3', 'wb97x-v']
max_scf_cylces_l = [400, 800, 1000]
max_diis_cycles_l = [400, 600, 800, 1000]
geom_opt_max_cycles_l = [400, 600, 551, 800, 1000]
scf_convergence_l = [8, 9, 10, 11]


# Job you run the most often?

def createMolecule(coordinate_list, symbols_list, charge=0, multiplicity=1):
    molecule = Structure(coordinate_list, symbols_list, charge, multiplicity)
    return molecule


if __name__ == '__main__':
    # Create a Job, whose defaults parameters have been set to parameters most commonly used.
    # Parameters can be set and changed by passing them when the job is created
    Test = Job()
    Test.printJob()

    # Parameters to be entered in the command line, the first one being the xyz file to be read and the second one
    # being the parameter you want to vary.
    ap = argparse.ArgumentParser()
    ap.add_argument("inputXYZfile", help='input file')
    ap.add_argument('parameter', help='The parameter you want to vary')
    # ap.add_argument('param_list', help='The list')

    args = vars(ap.parse_args())

    # Reading the xyz file and extracting the coordinates and symbols for it
    try:
        a = read(args["inputXYZfile"])
    except FileNotFoundError:
        print('Not such file exists')

    coordinate_list = a.get_positions().tolist()

    element_list = a.get_chemical_symbols()

    # molecule = Structure(coordinates=coordinate_list, symbols= element_list, charge=0, multiplicity=1)

    molecule = Structure(coordinates=[[0.0, 0.0, 0.0],
                                      [0.0, 0.0, 0.9]],
                         symbols=['H', 'H'],
                         charge=0,
                         multiplicity=1)

    # print(molecule)

    for x in range(len(geom_opt_max_cycles_l)):

        # create_qchem_input is the function responsible for creating the input file for the calculation
        # This should mostly be left unchanged as the Job object takes care of passing in the correct parameters and if a
        # change is required it should be done using the input_variation function in the job class

        txt_input = create_qchem_input(molecule, jobtype=Test.jobtype, gui=Test.gui, basis=Test.basis,
                                       method=Test.method,
                                       max_scf_cycles=Test.max_scf_cycles, geom_opt_max_cycles=Test.geom_opt_max_cycles,
                                       scf_convergence=Test.scf_convergence)

        txt_input_freq = create_qchem_input(molecule, jobtype='freq', gui=Test.gui, basis=Test.basis,
                                       method=Test.method,
                                       max_scf_cycles=Test.max_scf_cycles, geom_opt_max_cycles=Test.geom_opt_max_cycles,
                                       scf_convergence=Test.scf_convergence)

        # The get_output_from_qchem has the added ability of being able to parsed through data if needed

        try:
            output = get_output_from_qchem(txt_input, processors=8, force_recalculation=True,
                                           store_full_output=True)
            parsed_data = get_output_from_qchem(txt_input_freq,
                                                processors=4,
                                                parser=basic_frequencies)
        except OutputError as e:
            output = 'Error'
            print("Calculation ended with errors. Error lines: ")
            print(e.error_lines)

        output_filename = args["inputXYZfile"].replace('.xyz', '{}.out'.format(x))

        freq_file = output_filename
        freq_file = freq_file.replace('{}.out'.format(x), 'Freq{}.out'.format(x))


        Test.input_variation(args['parameter'], geom_opt_max_cycles_l)
        # Test2.printJob()


        directory = "TestResults"

        path = os.path.join(os.getcwd(), directory)
        print(path)

        try:
            os.mkdir(path)
        except OSError as error:
            print("Directory already exists")

        f = open(path + "/" + output_filename, "w")
        f_freq = open(path + "/" + freq_file, "w")
        #f.write(output)

        for i, mode in enumerate(parsed_data['modes']):
            f_freq.write('mode:                      {}'.format(i + 1))
            f_freq.write('force constant (mdyne/A):  {:10.5f}\n'.format(mode['force_constant']))
            if float(mode['frequency']) >= 0:
                f_freq.write('frequency (cm-1):          {:10.2f}'.format(mode['frequency']))
            else:
                f_freq.write('Frequency is negative please change a parameter')

        # f = open(output_filename, "r")
        # print(f.read())
        f_freq.close()
        f.close()
