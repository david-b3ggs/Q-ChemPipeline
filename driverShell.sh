#PBS -l nodes=1:ppn=8 

#PBS -M esteban_orozco@baylor.edu
#PBS -m abe

#PBS -N Param_VarationTest

 

cd $PBS_O_WORKDIR

module load openmpi-intel/1.10.3 

module load python/3.7.2

python QChem_Driver.py biphenalenyl.xyz geom_opt_max_cycles
