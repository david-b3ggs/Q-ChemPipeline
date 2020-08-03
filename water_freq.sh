#PBS -l nodes=1:ppn=8

#PBS -m abe -M david_beggs@baylor.edu

#PBS -N diphenalenyl

 

cd $PBS_O_WORKDIR

numProcs=`cat $PBS_NODEFILE | wc -l`

qchem -nt $numProcs diphenalenyl.in diphenalenyl.out
