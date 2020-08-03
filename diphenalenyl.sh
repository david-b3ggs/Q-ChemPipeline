#PBS -l nodes=1:ppn=8
 #PBS -m abe -M david_beggs@baylor.edu
#PBS -N diphenalenyl
cd 
numProcs=0;
qchem -nt 8 diphenalenyl.in diphenalenyl.out 
