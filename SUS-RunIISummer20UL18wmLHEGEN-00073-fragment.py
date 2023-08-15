import FWCore.ParameterSet.Config as cms

from Configuration.Generator.Pythia8CommonSettings_cfi import *
from Configuration.Generator.MCTunes2017.PythiaCP5Settings_cfi import *  

externalLHEProducer = cms.EDProducer("ExternalLHEProducer",
    args = cms.vstring("/cvmfs/cms.cern.ch/phys_generator/gridpacks/UL/13TeV/madgraph/V5_2.6.5/sus_sms/SMS-GlGl/SMS-GlGl_mGl-1500_slc7_amd64_gcc700_CMSSW_10_6_19_tarball.tar.xz"),
    nEvents = cms.untracked.uint32(5000),
    numberOfParameters = cms.uint32(1),
    outputFile = cms.string('cmsgrid_final.lhe'),
    scriptName = cms.FileInPath('GeneratorInterface/LHEInterface/data/run_generic_tarball_cvmfs.sh')
)

import math

baseSLHATable="""
BLOCK MASS
   2000001     1.00000000E+05
   2000002     1.00000000E+05
   2000003     1.00000000E+05
   2000004     1.00000000E+05
   2000005     1.00000000E+05
   2000006     1.00000000E+05
   2000011     1.00000000E+05
   2000013     1.00000000E+05
   2000015     1.00000000E+05
   1000001     1.00000000E+05
   1000002     1.00000000E+05
   1000003     1.00000000E+05
   1000004     1.00000000E+05
   1000005     1.00000000E+05
   1000006     1.00000000E+05
   1000011     1.00000000E+05
   1000012     1.00000000E+05
   1000013     1.00000000E+05
   1000014     1.00000000E+05
   1000015     1.00000000E+05
   1000016     1.00000000E+05
   1000021     1500
   1000022     1.00000000E+00
   1000023     750
   1000024     750
   1000025     1.00000000E+05
   1000035     1.00000000E+05
   1000037     1.00000000E+05
#
DECAY   2000001     0.00000000E+00
DECAY   2000002     0.00000000E+00
DECAY   2000003     0.00000000E+00
DECAY   2000004     0.00000000E+00
DECAY   2000005     0.00000000E+00
DECAY   2000006     0.00000000E+00
DECAY   2000011     0.00000000E+00
DECAY   2000013     0.00000000E+00
DECAY   2000015     0.00000000E+00
DECAY   1000001     0.00000000E+00
DECAY   1000002     0.00000000E+00
DECAY   1000003     0.00000000E+00
DECAY   1000004     0.00000000E+00
DECAY   1000005     0.00000000E+00
DECAY   1000006     0.00000000E+00
DECAY   1000011     0.00000000E+00
DECAY   1000012     0.00000000E+00
DECAY   1000013     0.00000000E+00
DECAY   1000014     0.00000000E+00
DECAY   1000015     0.00000000E+00
DECAY   1000016     0.00000000E+00

DECAY   1000021     1.00000000E+00
     0.00000000E+00    3         -6          6    1000022
     1.00000000E-01    3         -1          1    1000023
     1.00000000E-01    3         -2          2    1000023
     1.00000000E-01    3         -3          3    1000023
     1.00000000E-01    3         -4          4    1000023
     1.00000000E-01    3         -5          5    1000023
     1.25000000E-01    3         -2          1    1000024
     1.25000000E-01    3          2         -1    -1000024
     1.25000000E-01    3         -4          3    1000024
     1.25000000E-01    3          4         -3    -1000024

DECAY   1000023     1.00000000E-01
     1.00000000E+00    2         22    1000022
DECAY   1000024     1.00000000E-01
     0.0000000    3     1000022        -1      2
     1.0000000    2     1000022        24

DECAY   1000022     0.00000000E+00
"""


generator = cms.EDFilter("Pythia8HadronizerFilter",
  maxEventsToPrint = cms.untracked.int32(1),
  pythiaPylistVerbosity = cms.untracked.int32(1),
  filterEfficiency = cms.untracked.double(1.0),
  pythiaHepMCVerbosity = cms.untracked.bool(False),
  comEnergy = cms.double(13000.),
  PythiaParameters = cms.PSet(
    pythia8CommonSettingsBlock,
    pythia8CP5SettingsBlock,
    JetMatchingParameters = cms.vstring(
      'JetMatching:setMad = off',
      'JetMatching:scheme = 1',
      'JetMatching:merge = on',
      'JetMatching:jetAlgorithm = 2',
      'JetMatching:etaJetMax = 5.',
      'JetMatching:coneRadius = 1.',
      'JetMatching:slowJetPower = 1',
      'JetMatching:qCut = 147', #this is the actual merging scale
      'JetMatching:nQmatch = 5', #4 corresponds to 4-flavour scheme (no matching of b-quarks), 5 for 5-flavour scheme
      'JetMatching:nJetMax = 2', #number of partons in born matrix element for highest multiplicity
      'JetMatching:doShowerKt = off', #off for MLM matching, turn on for shower-kT matching
      '6:m0 = 172.5',
      '24:mMin = 7',
      'Check:abortIfVeto = on',
    ),
    processParameters = cms.vstring(
      'SUSY:all = off',
      'SUSY:gg2gluinogluino = on',
      'SUSY:qqbar2gluinogluino = on',
      'RHadrons:allow  = on',
      'RHadrons:allowDecay = off',
      'RHadrons:setMasses = on',
      'RHadrons:probGluinoball = 0.1',
	),     
    parameterSets = cms.vstring('pythia8CommonSettings',
      'pythia8CP5Settings',
      'JetMatchingParameters',
      'processParameters'
    )
  ),
  SLHATableForPythia8 = cms.string(baseSLHATable),
)
