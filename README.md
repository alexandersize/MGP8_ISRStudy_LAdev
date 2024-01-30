# MGP8_ISRStudy



* example MadGraph samples
	* https://cmsweb.cern.ch/das/request?instance=prod/global&input=file+dataset%3D%2FSMS-T1btbt-LLC1_ctau10to200-mGluino-1000to2800-mLSP0to2800_TuneCP2_13TeV-madgraphMLM-pythia8%2FRunIIFall17FSPremix-GridpackScan_94X_mc2017_realistic_v15-v1%2FAODSIM

From Sara F:

> here some MG gluino samples
> https://cmsweb.cern.ch/das/request?view=list&limit=50&instance=prod%2Fglobal&input=%2FSMS-T5qqqqWH_TuneCP5_13TeV-madgraphMLM-pythia8%2FRunIISummer20UL*MiniAODv2*%2FMINIAODSIM
> and here some stops samples
> https://cmsweb.cern.ch/das/request?view=list&limit=50&instance=prod%2Fglobal&input=%2FSMS-T6ttZH_TuneCP5_13TeV-madgraphMLM-pythia8%2FRunIIS*MiniAODv*%2FMINIAODSIM


* Our Pythia samples
	* https://cmsweb.cern.ch/das/request?view=list&limit=50&instance=prod%2Fglobal&input=dataset%3D%2FHSCP*%2FRunIISummer20UL18RECO-106X*%2FAODSIM

For some notes on how to access files like this. You can open them in root:

```python
import ROOT
f = ROOT.TFile.Open("root://cmsxrootd.fnal.gov///store/mc/RunIISummer20UL18RECO/HSCPgluino_M-1000_TuneCP5_13TeV-pythia8/AODSIM/106X_upgrade2018_realistic_v11_L1v1-v2/80000/176F47D3-A514-454B-82D4-019163A330F9.root")
```

or you can copy them to whereever you want with:

```bash
xrdcp root://cmsxrootd.fnal.gov///store/mc/RunIISummer20UL18RECO/HSCPgluino_M-1000_TuneCP5_13TeV-pythia8/AODSIM/106X_upgrade2018_realistic_v11_L1v1-v2/80000/176F47D3-A514-454B-82\
D4-019163A330F9.root .
```

**I've already downloaded an example file to get you started here `/afs/cern.ch/user/l/leejr/work/public/ISRStudy//sampleFiles/176F47D3-A514-454B-82D4-019163A330F9.root`**

In order to see the contents of these files in an effective way you need to be in a CMSSW environment. Instructions for setting up CMSSW from Tamas:

```bash
cmsrel CMSSW_10_6_30
cd CMSSW_10_6_30/src/
cmsenv

scram b -j
```

Then you'll be able to run the `truth.py` example skeleton file from this repo.

The syntax for `truth.py` looks like this

python truth.py inputFiles_load=batch_of_files.list outputFile=dir/name_PYTHIA.root outputFilename=name_PYTHIA isAOD=True targetMass=100

You can instead opt to hand `truth.py` a single ROOT file by using 'inputFiles' rather than 'inputFiles_load'

isAOD takes a boolean and will change the status between 22 and 23 based on if the samples are AOD or MINIAOD

targetMass takes an int and refers to the mass of an individual particle in an event


**Instructions for generating .list files to pass to truth.py**

Once path to the dataset has been found from DAS, this command will generate the .list with the entries in the appropriate format.

```dasgoclient -query="file dataset=<dataset path>" | sed  's%^%root://cmsxrootd.fnal.gov//%' > ./input-files/<filename>.list```

The .list can then be passed to truth.py with the ```inputFiles_load``` command as outlined above.


**Helpful tips when running truth.py**

It may be useful to record the output of truth.py while also observing the output in the terminal. Rather than redirecting the output stream with ```>```, consider using ```tee```. Example:

```python truth.py inputFiles_load='./input-files/<input-list>.list' outputFilename='./output-files/<output_filename>.root' targetMass=200 isAOD=False printEvery=10000 2>&1 | tee ./text-logs/<log filename>.txt```

Note that this will overwrite the log.txt if run again. This is generally desireable, but you can append to an exisiting file by adding the ```-a``` flag to ```tee```. ```2>&1``` Ensures that the error outputstream is passed to ```tee``` so that any error output is recorded in the log. 

When passing Madgraph samples to truth.py, the target status must be given as a flag. Example: 

```python truth.py inputFiles_load='./input-files/<input-list>.list' outputFilename='./output-files/<output-filename>.root' targetMass=1000 isAOD=False printEvery=1000 targetStatus=62 2>&1 | tee ./text-logs/<log-filename>.txt```

**Status Code**

When inputting madgraph files use targetStatus=62
