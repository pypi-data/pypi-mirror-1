#!/usr/bin/env python
# The Broad Institute
# SOFTWARE COPYRIGHT NOTICE AGREEMENT
# This software and its documentation are copyright 2006 by the
# Broad Institute/Massachusetts Institute of Technology. All rights are
# reserved.

# This software is supplied without any warranty or guaranteed support
# whatsoever. Neither the Broad Institute nor MIT can be responsible for its
# use, misuse, or functionality.
# $Header$

"""usage: %prog [options] list of fully qualified directories
run plink_summarize across a number of populations.  This splits a plink bed/bim/fam combo with many populations into a set of bed/bim/fam
files for each population, then runs plink_summarize against it.
"""

import sys
sys.path.append ("/fg/wgas/wgas_scripts")
sys.path.append("/home/radon00/nemesh/wgas_scripts")

import optparse
import os.path
from mpgutils import utils
import plink_summarize

strDEFAULT_PLINK_PATH='plink'

def readPopulationMap (inFile):
    fIn = open(inFile, 'rU')
    
    dctPopMap={}
    for strLine in fIn:
         s= strLine.split()
         pop=s[0]
         sample=s[1]
         if (pop!="population"):
             if (pop in dctPopMap):
                 lstTmp=dctPopMap[pop]
                 lstTmp.append(sample)
                 dctPopMap[pop]=lstTmp
             else:
                 lstTmp=[sample]
                 dctPopMap[pop]=lstTmp
    fIn.close()
    
    return (dctPopMap)

def readSampleFamMap (pedigreeFile):
    """Reads in a pedigree file, and creates a dictionary with the key as the sample, and the value as the family ID"""
    fIn = open(pedigreeFile, 'r')
    
    dctSampleFam={}
    for strLine in fIn:
         s= strLine.split()
         famID=s[0]
         sampleID=s[1]
         if (famID!="FAM_ID"):
             dctSampleFam[sampleID]=famID
    
    fIn.close()
    return (dctSampleFam)
    
def compilePlinkPopulations (dctPopMap, dctSampleFam, workingDirectory, rootBedBimFamName, plinkPath):
    """Compiles a new bed/bim/fam combo with only the individuals for a single population included.  Calls the root of the combo
    by the population name.  Example plink call: plink --bfile plink --keep YRI.pop --out YRI --make-bed"""
    
    pops=dctPopMap.keys()
    for p in pops:
        popFile=writePopulationFile(dctPopMap, p, dctSampleFam, workingDirectory)
        
        
        lstArgs=[plinkPath,
                 "--bfile", workingDirectory+rootBedBimFamName,
                 "--keep", popFile,
                 "--out", workingDirectory+p,
                 "--make-bed"]
        
        utils.check_call(lstArgs, True)

def callPlinkSummarize (dctPopMap, workingDirectory, plinkPath):
    """Call plink summarize on each of the compiled bed/bim/fam file sets that are created per population"""
    originalDir=os.getcwd()
    pops=dctPopMap.keys()
    os.chdir(workingDirectory)
    for p in pops:
        lstArgs=["plink_summarize",
                 "--bed", p + ".bed",
                 "--bim", p+ ".bim",
                 "--fam", p+ ".fam",
		 		 "--plink-out", p,
		 		 "--log", p+".plink_log", 
                 "--output", p+"_qc_report.html"]
        plink_summarize.main(lstArgs)
        
    os.chdir(originalDir)
    
def writePopulationFile (dctPopMap, populationName, dctSampleFam, workingDirectory):
    """Writes out a set of family and individual names for use in plink compile.  Returns the file location"""
    outFile=workingDirectory + populationName + ".pop"
    fOut=open (outFile, "w")
    samples=dctPopMap[populationName]
    for s in samples:
        if dctSampleFam.has_key(s):
            f=dctSampleFam[s]
            line="\t".join([f,s])
            fOut.write(line+"\n")
    fOut.close()
    return (outFile)
    
    
def main(argv=None):
    if argv is None:
        argv = sys.argv
        
    if argv is None:
        argv=sys.argv

    parser = optparse.OptionParser(usage=__doc__)

    parser.add_option("--populationFile", 
                      help="""tab-delimited file with 2 columns: popultion and sample""")
    
    parser.add_option("--pedigreeFile",
                      help="""The pedigree file for the populations""")
    
    parser.add_option ("--workingDirectory", 
                       help="""The directory where the input bed/bim/fam and output files will go.""")
                       
    parser.add_option("--rootBedBimFamName", default="plink",
                      help="""The name of the bed/bim/fam files, eg: "plink" for plink.bed""")
    
    parser.add_option('--plink-path', dest='strPlinkPath',
                      default=strDEFAULT_PLINK_PATH,
                      help="""plink program.  Default: find plink on path.  
                      Hint: put "use plink" in your startup script.""")

    dctOptions, lstArgs = parser.parse_args(argv)

    argCount = len(lstArgs)-1
    
    lstRequiredOptions=["populationFile", "pedigreeFile", "workingDirectory", "rootBedBimFamName"]
    
    if not utils.validateRequiredOptions(dctOptions, lstRequiredOptions):
        parser.print_help()
        return 1
    
    dctPopMap=readPopulationMap(dctOptions.populationFile)
    dctSampleFam=readSampleFamMap(dctOptions.pedigreeFile)
    
    """Ensure that the working directory always has a trailing slash"""
    strWorkingDirectory=dctOptions.workingDirectory
    if not strWorkingDirectory.endswith("/"):
        strWorkingDirectory+="/"
   
    compilePlinkPopulations (dctPopMap, dctSampleFam, strWorkingDirectory, dctOptions.rootBedBimFamName, dctOptions.strPlinkPath)
    callPlinkSummarize(dctPopMap, strWorkingDirectory, dctOptions.strPlinkPath)
    print("Finishing run plink population")

if __name__ == '__main__':
    sys.exit(main())
