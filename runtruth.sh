#!/bin/bash
#Bash script to run truth.py
#cd /afs/cern.ch/user/c/cthompso/private/CMSSW_10_6_30/src
#cmsenv
#scram b -j
#voms-proxy-init -voms cms
#Inf291501
pymass=('1800' '2000' '2200' '2400' '2600')
#mgmass=('1000' '1400' '1600' '1800' '2000' '2200' '2400' '2600')

for str in ${pymass[@]};
do
	echo Running truth.py on pythia for targetMass = $str GeV
	python truth.py inputFiles_load=input-files/PYgluino2018_M-$str.list outputFilename=output-files/pythia-M-$str.root targetMass=$((str)) isAOD=True printEvery=1000
done

#for str in ${mgmass[@]};
#do
#	echo Running truth.py on madgraph for targetMass = $str GeV
#	python truth.py inputFiles_load=input-files/MGgluino2018.li#st outputFilename=output-files/gluglu_MG_GeV$str.root targetMass=$((str)) isAOD=False printEvery=100000 targetStatus=62 2>&1 | tee ./text-logs/MG$str.txt
#done