from pyqchem.structure import Structure
from pyqchem.qchem_core import get_output_from_qchem, create_qchem_input, redefine_calculation_data_filename
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
gui_l = [1,2,3]
basis_l = ['6-31G*']
method_l = ['b3lyp', 'hf', 'pbe0', 'wb97x-d3', 'wb97x-v']
max_scf_cylces_l = [400, 800, 1000]
max_diis_cycles_l = [400, 600, 800, 1000]
geom_opt_max_cycles_l = [400, 600 ,551, 800, 1000]
scf_convergence_l = [8, 9, 10 ,11]


#Job you run the most often?


if __name__ == '__main__':
    Test = Job()
    Test.printJob()



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


    molecule = Structure(coordinates=coordinate_list, symbols= element_list, charge=0, multiplicity=2)

    #print(molecule)

    txt_input = create_qchem_input(molecule, jobtype=Test.jobtype, gui=Test.gui,basis=Test.basis,method=Test.method,
                                   max_scf_cycles=Test.max_scf_cycles, geom_opt_max_cycles=Test.geom_opt_max_cycles,
                                   scf_convergence=Test.scf_convergence)

    # try:
    #     output = get_output_from_qchem(txt_input, processors=8, force_recalculation=True,
    #                                    store_full_output=True)
    # except OutputError as e:
    #     output = 'Error'
    #     print("Calculation ended with errors. Error lines: ")
    #     print(e.error_lines)
    #
    # print(output)

    for x in range(10):
        output_filename = args["inputXYZfile"].replace('.xyz', '{}.out'.format(x))
        Test2 = Job()
        Test2.input_variation(args['parameter'],geom_opt_max_cycles_l)
        Test2.printJob()

        print(output_filename)
