from JobClass import Job
import sys

class Runner:
    #Need to add opt object

    """""  
    Run opt extracts coordinates from the XYZ file and generates parameters for 
    optimization job to be run.
    """""
    def start(self, xyzFile):
        job = Job()
        try:
            xFile = open(xyzFile, "r+")
        except IOError:
            print("Could not open File to extract xyz coordinates")

        job.

    def runOpt(self, Job):

    def parseJob(self):

    def runJob(self, Job):

    def runAllJobs(self):
