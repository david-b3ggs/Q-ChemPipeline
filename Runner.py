from JobClass import Job
from QChemOutputParser import Parser
import sys
import os
import time
import subprocess

class Runner:
    job = Job()
    optFreqOutput = ""
    molName = ""

    # Returns True if no imaginary frequencies, false otherwise

    def __checkFreq(self, file):
        ret = False
        line = file.readline()
        while "This Molecule has" not in line:
            line = file.readline()
        if int(line.lsplit().split()[3]) == 0:
            ret = True

        return ret


    def __extractOptomizedCoordinates(self, file):
        list = file.readlines()
        coordinates = []
        line = list[5]
        while "Final Energy" not in line:
            coordinates.append(line)

        return coordinates

    """""  
    Run opt extracts coordinates from the XYZ file and generates parameters for 
    optimization job to be run.
    """""
    def start(self, xyzFile, name):
        # Running default spec for standard optimization job
        self.molName = name
        path = "./" + name

        try:
           os.mkdir(path)
        except OSError:
           print ("Creation of the directory %s failed" % path)
        else:
           print ("Successfully created the directory %s " % path)

        try:
            xFile = open(xyzFile, "r+")
        except IOError:
            print("Could not open File to extract xyz coordinates")
            sys.exit(-1)

        coords = self.job.readXYZ(xFile)
        print("Generating Input File")
        inFile = self.job.createStartInputFile(self.molName, coords)
        time.sleep(3)
        self.optFreqOutput = self.runOptFreq()
        looker = Parser()
        looker.parse([], "./" + self.molName + ".out", "./" + self.molName + "_analysis")

        while not self.__checkFreq(self.molName + "_analysis"):
            newPoints = self.__extractOptomizedCoordinates(self.molName + "_analysis")
            inFile = self.job.createStartInputFile(self.molName, newPoints)
            self.optFreqOutput = self.runOptFreq()


    # Returns a filename of optOutput
    def runOptFreq(self):
        print("Creating script file...")
        scriptString = "\"#PBS -l nodes=1:ppn=8\n#PBS -m abe -M david_beggs@baylor.edu\nPBS -N " + self.molName +  \
                        "\ncd " + self.molName + "\nnumProcs=`cat $PBS_NODEFILE | wc -l`;\n" \
                        "qchem -nt 8 " + self.molName + ".in " + self.molName + ".out \" > ./" + self.molName + "/" + self.molName + ".sh ;\n"
        print(scriptString)
        processCreateSh = subprocess.Popen(("echo " + scriptString).split(), stdout=subprocess.PIPE)
        processCreateSh.wait()
        print("Running qsub...")
        scriptRun = "qsub ./" + self.molName + "/" + self.molName +  ".sh"
        processRunSh = subprocess.Popen(scriptRun.split(), stdout=subprocess.PIPE)
        processRunSh.wait()


        foundFile = 0
        while foundFile == 0:
            time.sleep(5)
            print(os.path.isfile("./" + self.molName + "/" + self.molName +  ".out"))
            if os.path.isfile("./" + self.molName + "/" + self.molName +  ".out"):
                foundFile = 1
                print("Located Output File")

        print("Job finished")

"""
    def runCDFTCI(self):
    

    def runAllJobs(self):
"""
