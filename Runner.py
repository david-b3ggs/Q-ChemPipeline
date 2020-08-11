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
        scriptFile = open("./" + self.molName + "/" + self.molName + ".sh",
        "w+")
        scriptString = "#PBS -l nodes=1:ppn=8\n#PBS -m abe -M david_beggs@baylor.edu\n#PBS -N " + self.molName +  \
                        "\ncd /home/beggsd/Q-ChemPipeline/" + self.molName + "\nnumProcs=`cat $PBS_NODEFILE | wc -l`;\n" \
                        "qchem -nt 8 " + self.molName + ".in " + self.molName + ".out"
        print(scriptString)
        scriptFile.write(scriptString)
        scriptFile.close()
        print("Running qsub...")
        scriptRun = "qsub /home/beggsd/Q-ChemPipeline/" + self.molName + "/" + self.molName + ".sh"
        processRunSh = subprocess.check_output(scriptRun.split())
        print(processRunSh[:len(processRunSh) - 1])
        batchCode = str(processRunSh[:len(processRunSh) - 1])[2:len(processRunSh) - 1] + "ch"
        print("batch code: " + batchCode)


        foundFile = 0
        time.sleep(30)
        while foundFile == 0:
            findCommand = "qstat | grep " + str(batchCode)
            qStatAnalyze = subprocess.Popen(findCommand, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
            analyze = str(qStatAnalyze.stdout.read())[2:]
            if batchCode not in analyze:
                foundFile = 1
                print("Job Completed")
            else:
                print("Job still running")
                time.sleep(60)

        print("Job finished")

"""
    def runCDFTCI(self):
    

    def runAllJobs(self):
"""
