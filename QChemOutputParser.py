# Author: David Beggs
# This file will produce specified output from Qchem *.out files to extrapolate meaningful results

import sys
import re
import subprocess
import os

class Parser:

    ##############################################################################################
    # Read until function moves the file pointer and returns appropriate line given search string
    ##############################################################################################

    def __readUntil(self, f, stri):
        line = f.readline()
        currentPosition = f.tell()
        found = 0

        if stri == "$rem":
            while stri not in line and line != "":
                line = f.readline()
        else:
            while stri not in line and line != "" and "$rem" not in line:
                line = f.readline()

        if stri in line:
            found = 1

        if not found:
            line = ""
            f.seek(currentPosition, 0)

        return line

    ##############################################################################################
    # hasNumbers returns True or False for the presence of numbers in a string
    ##############################################################################################

    def __hasNumbers(self, inputString):
        return any(char.isdigit() for char in inputString)

    ##############################################################################################
    # Find last instance of given string in argument file
    ##############################################################################################

    def __findLast(self, infile, stri):
        infile.readline()
        count = 0
        line = self.__readUntil(infile, stri)

        while line != "":
            count += 1
            line = self.__readUntil(infile, stri)

        return line

    ##############################################################################################
    # extractAtoms() function is used to extract Becke populations from cdft files
    ##############################################################################################

    def __extractAtoms(self, infile, outfile, atomGroups):
        hasSpin = 0
        isOpt = 0
        currentLine = infile.readline()
        if "Spin" in currentLine:
            hasSpin = 1

        start = infile.tell()
        outfile.write(currentLine.lstrip() + "\n")

        atomCount = 1
        agCount = len(atomGroups)
        currentLine = infile.readline()

        if "---" in currentLine:
            currentLine = infile.readline()
            isOpt = 1

        while "---" not in currentLine:
            atomCount += 1

            currentLine = currentLine.lstrip()[2:]
            currentLine = currentLine.lstrip()
            outfile.write(currentLine)
            currentLine = infile.readline()

        infile.seek(start, 0)
        while agCount > 0:
            atomGroupFirst = atomGroups[agCount - 1][0]
            atomGroupLast = atomGroups[agCount - 1][1]

            if atomGroupLast > atomCount:
                atomGroupLast = atomCount
            if atomGroupFirst > atomCount:
                atomGroupFirst = 0

            atomGroups[agCount - 1].append(0)
            if hasSpin == 1:
                atomGroups[agCount - 1].append(0)

            chargeArray = []
            spinArray = []
            currentLine = infile.readline().lstrip()
            checkOpt = isOpt

            while (not re.match("([-]{2,})", currentLine) or isOpt == 1) and currentLine.split(' ')[0] != str(
                    atomGroupFirst):
                isOpt = 0
                currentLine = infile.readline().lstrip()

            for x in range(atomGroupFirst, atomGroupLast + 1):
                bomb = currentLine.split()

                if re.match("[0-9]", bomb[0]):
                    bomb.pop(0)

                if hasSpin == 1:
                    chargeArray.append(float(bomb[1]))
                    spinArray.append(float(bomb[len(bomb) - 1]))

                else:
                    chargeArray.append(float(bomb[len(bomb) - 1]))

                currentLine = infile.readline().lstrip()

            atomGroups[agCount - 1][2] = sum(chargeArray)
            if hasSpin == 1:
                atomGroups[agCount - 1][3] = sum(spinArray)
            agCount -= 1
            if checkOpt == 1:
                isOpt = 1
            infile.seek(start, 0)

        for i in range(0, len(atomGroups)):
            outfile.write("Atom Group Range: " + str(atomGroups[i][0]) + ", " + str(atomGroups[i][1]) + "\n")
            outfile.write("Atom Group Charge: " + str(atomGroups[i][2]) + '\n')
            if hasSpin == 1:
                outfile.write("Atom Group Spin: " + str(atomGroups[i][3]) + " \n")
            outfile.write("\n")
            atomGroups[i].pop(2)

    ##############################################################################################
    # This program is used in a larger driver to parse qchem output files for particular data
    # and generate iterative qchem input parameters
    ##############################################################################################
    def parse(self, atomGroups, inFileName = "atom", outFileName = "atom analysis"):

        # Create AG pairs
        atomGroups = []
        agCount = 0

        #AG's are 2d arrays

        # Open files
        hasPerms = True
        try:
            outputFile = open("./" + inFileName + "/" + outFileName , "w+")
        except IOError:
            print("Could not open Output File in parser")
            sys.exit(-1)

        try:
            chemFile = open("./" + inFileName + "/" + inFileName, "r")
        except IOError:
            hasPerms=False
            print("Could not open chem File in parser, Trying to elevate permissions...")

        if hasPerms is False:
            print("Attempting to give permissions")
            os.chmod("./"+inFileName+"/"+inFileName, 0o777)
            try:
               chemFile = open("./" + inFileName + "/" + inFileName, "r")
            except IOError:
               print("Could not give privelages")
               sys.exit(-1)

        self.__readUntil(chemFile, "$rem")
        self.__readUntil(chemFile, "$rem")
        outputFile.write("FIRST JOB\n")
        outputFile.write("TYPE: ")

        isCDFT = 0
        isCDFTCI = 0
        isOpt = 0
        isSP = 0
        isFreq = 0
        params = chemFile.readline()
        while "$end" not in params:
            if "cdftci" in params and "true" in params:
                isCDFTCI = 1
                outputFile.write("CDFTCI ")
            elif "cdft " in params and "true" in params:
                isCDFT = 1
                outputFile.write("CDFT ")
            elif "opt" in params:
                isOpt = 1
                outputFile.write("OPT ")
            elif "sp" in params:
                isSP = 1
                outputFile.write("SP ")
            elif "freq" in params:
                isFreq = 1
                outputFile.write("FREQ ")
            params = chemFile.readline()

        start = chemFile.tell()

        self.__parseRunner(atomGroups, chemFile, isCDFT, isCDFTCI, isFreq, isOpt, isSP, outputFile, start)

        if self.__readUntil(chemFile, "$rem") != "":
            params = self.__readUntil(chemFile, "$rem")
            outputFile.write("\n\nSECOND JOB \n")
            outputFile.write("TYPE: ")

            isCDFT = 0
            isCDFTCI = 0
            isOpt = 0
            isSP = 0
            isFreq = 0
            while "$end" not in params:
                if "cdftci" in params and "true" in params:
                    isCDFTCI = 1
                    outputFile.write("CDFTCI ")
                elif "cdft " in params and "true" in params:
                    isCDFT = 1
                    outputFile.write("CDFT ")
                elif "opt" in params:
                    isOpt = 1
                    outputFile.write("OPT ")
                elif "sp" in params:
                    isSP = 1
                    outputFile.write("SP ")
                elif "freq" in params:
                    isFreq = 1
                    outputFile.write("FREQ ")
                params = chemFile.readline()
            start = chemFile.tell()
            self.__parseRunner(atomGroups, chemFile, isCDFT, isCDFTCI, isFreq, isOpt, isSP, outputFile, start)

        chemFile.close()
        outputFile.close()

    def __parseRunner(self, atomGroups, chemFile, isCDFT, isCDFTCI, isFreq, isOpt, isSP, outputFile, start):

        if self.__readUntil(chemFile, "OPTIMIZATION CONVERGED") == "":
            angst = self.__readUntil(chemFile, "Nuclear Orientation (Angstroms)")
            while angst != "":
                angst = self.__readUntil(chemFile, "Nuclear Orientation (Angstroms)")

            outputFile.write("\n\nInput Coordinates\n")
            outputFile.write("Atom           X                Y                Z\n")
            chemFile.readline()
            angstrom = chemFile.readline().lstrip()
            currentNum = 1

            while "---" not in angstrom and int(angstrom.split()[0]) == currentNum:
                angList = angstrom.split()
                angstrom = '\t'.join(angList[1:])
                outputFile.write(angstrom + "\n")

                angstrom = chemFile.readline().lstrip()
                currentNum += 1
        else:
            chemFile.readline()
            chemFile.readline()
            chemFile.readline()
            outputFile.write("\n\nOPTIMIZED COORDINATES\n")
            angstrom = chemFile.readline()
            outputFile.write(angstrom.lstrip())
            angstrom = chemFile.readline()

            while self.__hasNumbers(angstrom):
                outputFile.write(angstrom.lstrip()[2:].lstrip())
                angstrom = chemFile.readline()
        # If the file is a cdft type
        if isCDFT == 1 or isCDFTCI == 1:
            chemFile.seek(start)
            block = self.__readUntil(chemFile, "$cdft")
            while "$end" not in block:
                block = chemFile.readline()
                outputFile.write(block)

            self.__readUntil(chemFile, "Final Multiplier")
            self.__readUntil(chemFile, "Final Multiplier")
            beckeEnergy = chemFile.readline()
            outputFile.write("Becke Prior Energy Line: " + beckeEnergy.lstrip())

            outputFile.write('\n')
            if isCDFT == 1:
                beckeLine = self.__readUntil(chemFile, "CDFT Becke Populations")
                while beckeLine != "":
                    self.__readUntil(chemFile, "Final Multiplier")
                    self.__readUntil(chemFile, "Final Multiplier")
                    beckeEnergy = chemFile.readline()
                    beckeLine = self.__readUntil(chemFile, "CDFT Becke Populations")

                outputFile.write("Becke Prior Energy Line: " + beckeEnergy.lstrip())
                self.__extractAtoms(chemFile, outputFile, atomGroups)

            elif isCDFTCI == 1:
                beckeLine = self.__readUntil(chemFile, "CDFT Becke Populations")
                stateNumber = 1
                while beckeLine != "":
                    outputFile.write("State #" + str(stateNumber) + '\n')
                    self.__extractAtoms(chemFile, outputFile, atomGroups)
                    self.__readUntil(chemFile, "Final Multiplier")
                    self.__readUntil(chemFile, "Final Multiplier")
                    beckeEnergy = chemFile.readline()

                    if "Convergence criterion" in beckeEnergy:
                        outputFile.write("Becke Prior Energy Line: " + beckeEnergy.lstrip())

                    beckeLine = self.__readUntil(chemFile, "CDFT Becke Populations")
                    stateNumber += 1

            if isCDFTCI == 1 and self.__readUntil(chemFile, "Hamiltonian matrix in orthogonalized basis") != "":
                # read until matrix in orthogonalized, then extract matrix, and diagonals
                self.__readUntil(chemFile, "Hamiltonian matrix in orthogonalized basis")
                outputFile.write("Hamiltonian Matrix in orthognialized basis\n")
                matrixString = chemFile.readline()
                matrixLine = matrixString.lstrip()[1:].split()

                length = len(matrixLine)
                if length == 2:
                    for elem in matrixLine:
                        if len(elem) > 16:
                            length = 3
                            break

                for x in range(0, length):
                    outputFile.write(matrixString.lstrip()[1:])
                    matrixString = chemFile.readline()

        if isOpt == 1 or isSP == 1 or isFreq == 1:
            chemFile.seek(start)

            if isOpt == 1:
                finalEnergy = self.__readUntil(chemFile, "Final energy is").lstrip().rstrip()
                outputFile.write("Final Energy  (Hartree, eV):\t")
                energy = finalEnergy.split(' ')
                outputFile.write(
                    energy[len(energy) - 1] + " Ha, " + str(float(energy[len(energy) - 1]) * 27.2114) + " eV\n")

                outputFile.write('\n')

            self.__readUntil(chemFile, "Ground-State Mulliken Net Atomic Charges")
            chemFile.readline()

            self.__extractAtoms(chemFile, outputFile, atomGroups)

            if self.__readUntil(chemFile, "Hessian of the SCF energy") != "":
                self.__readUntil(chemFile, "Hessian of the SCF Energy")

                chemFile.readline()
                hessianLine = chemFile.readline().lstrip()
                hessianMatrix = []
                x = 0
                seen = 0

                while not re.search("([a-zA-Z])", hessianLine) and not re.search("(\*)", hessianLine):

                    if hessianLine.find('.') == -1:
                        seen = 1
                        hessianLine = chemFile.readline().lstrip()
                        x = 0
                    else:
                        row = []
                        rowInts = hessianLine[1:].split()
                        x = int(hessianLine[0]) - 1
                        for num in rowInts:
                            row.append(float(num))

                        if seen == 0:
                            hessianMatrix.append(row)
                        else:
                            hessianMatrix[x] = hessianMatrix[x] + row

                        hessianLine = chemFile.readline().lstrip()

                outputFile.write("Hessian Matrix of the SCF Energy\n")
                outputFile.write("Size: " + str(len(hessianMatrix)) + ", " + str(len(hessianMatrix[0])))
                for array in hessianMatrix:
                    for number in array:
                        outputFile.write('{:13}'.format(str(number)) + " ")
                    outputFile.write("\n")

            currentLine = self.__readUntil(chemFile, "Mode: ")

            if currentLine != "":
                frequencies = []
                modeMax = 0

                while currentLine != "":
                    words = currentLine.split()
                    modeMax = float(words[len(words) - 1])
                    currentLine = chemFile.readline()
                    words = currentLine.split()
                    words.pop(0)

                    for freq in words:
                        frequencies.append(float(freq))

                    currentLine = self.__readUntil(chemFile, "Mode: ")

                outputFile.write("\nMaxMode: " + str(modeMax) + '\n')
                outputFile.write("List of Frequencies: ")
                for f in frequencies:
                    outputFile.write(str(f) + " ")

            if self.__readUntil(chemFile, "STANDARD THERMODYNAMIC QUANTITIES") != "":
                outputFile.write(chemFile.readline())
                outputFile.write(chemFile.readline())
        chemFile.seek(start)
        aMinus = ""
        vMinus = ""
        if self.__readUntil(chemFile, "Alpha MOs") != "":
            self.__findLast(chemFile, "Alpha MOs")
            homoLine = chemFile.readline()
            lineSplitter = homoLine.split()

            lastIndex = homoLine.rfind(' ')
            if len(lineSplitter) > 1:
                aMinus = float(lineSplitter[len(lineSplitter) - 2])

            homo = float(homoLine[lastIndex + 1:])
            homoLine = chemFile.readline()

            while re.search("(-)*([0-9]+)\.([0-9]+)", homoLine):
                lastIndex = homoLine.rfind(' ')
                lineSplitter = homoLine.split()
                if len(lineSplitter) > 1:
                    aMinus = float(lineSplitter[len(lineSplitter) - 2])
                else:
                    aMinus = homo
                homo = float(homoLine[lastIndex + 1:])
                homoLine = chemFile.readline()

            lomoLine = chemFile.readline()

            if re.search("[a-zA-Z]", lomoLine):
                lomoLine = chemFile.readline()

            lomo = float(lomoLine.split()[0])
            vMinus = float(lomoLine.split()[1])

            outputFile.write("HOMO (Hartree, eV): " + str(homo) + " Ha, " + str(homo * 27.2114) + "eV\n")
            outputFile.write("HOMO - 1 (Hartree, eV): " + str(aMinus) + " Ha, " + str(aMinus * 27.2114) + "eV\n")
            outputFile.write("LOMO (Hartree, eV): " + str(lomo) + " Ha, " + str(lomo * 27.2114) + "eV\n")
            outputFile.write("LOMO + 1 (Hartree, eV): " + str(vMinus) + " Ha, " + str(vMinus * 27.2114) + "eV\n")
            energyGap = homo - lomo
            outputFile.write(
                "HOMO-LUMO Energy Gap (Hartree, eV): " + str(energyGap) + " Ha, " + str(energyGap * 27.2114)
                + "eV\n\n")

            if isSP == 1:
                outputFile.write("Koopmans hole transfer coupling (Hartree, eV): " + str((homo - aMinus) / 2) + " Ha, ")
                outputFile.write(str((homo - aMinus) / 2 * 27.2114) + " eV\n")
                outputFile.write(
                    "Koopmans electron transfer coupling (Hartree, eV): " + str((vMinus - lomo) / 2) + " Ha, ")
                outputFile.write(str((vMinus - lomo) / 2 * 27.2114) + " eV\n")
