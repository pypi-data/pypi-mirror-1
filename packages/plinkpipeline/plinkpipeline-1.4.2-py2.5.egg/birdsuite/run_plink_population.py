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

Run plink on a list of directories that define a population.
The directory name informs this script as to what the appropriate artifacts
are named to generate the proper input files for plink.

This program will 
1) make_ped_and_map_file.py
(requiring a map3 file, platemap files, pedigree files, a threshold, calls files, and confidence files)
2) merge_pedfiles.py
(requires ped files from step #1)
3) plink_compile.py
(requires merged ped files and a map file from step #2)
4) plink_summarize.py 
(requires .bed, .bim, .fam from step #3)

The important thing to remember is that the input directory names and the platemap and pedigree files are linked together by name.
The directory encodes 3 fields with a "_" seperation.  
1) Algorithm (birdseed | brlmmp)
2) plate name (5 character word like HURTS)
3) a quality metric (like q1c80p1)
This program only cares about field 2, so as long as a 5 letter word exists in the directory name, that will be used as the plate name.
The platemap will have the plate name with a filetype of platemap.  EG: hurts.platemap
The pedigree will have the plate name with a filetype of pedigree.  EG: hurts.pedigree
"""

import sys
sys.path.append ("/fg/wgas/wgas_scripts")
#sys.path.append("/home/radon00/nemesh/wgas_scripts")

import optparse
import re
import glob
import os.path
import make_ped_and_map_file
import merge_pedfiles
import plink_compile
import plink_summarize
from string import Template

def getsuffixFile (directory, suffix):
    directory=directory.rstrip("/")    
    searchStr=directory+"/*"+suffix
    results=glob.glob(searchStr)
    if (len(results)>1):
        print >> sys.stderr, 'suffix [', suffix, '] not specific, multiple results found for directory [', directory, ']' 
        sys.exit(1)
    if (len(results)==0):
        print >> sys.stderr, 'suffix [', suffix, '] not found for directory [', directory, ']'
    return results[0]

def getPrePlinkArtifact (directory, plateName, filetype):
    directory=directory.rstrip("/")
    return directory + "/" + plateName + filetype

def getPlateName (directory):
    directory=directory.rstrip("/")  
    base=os.path.basename(directory)
    s = base.split("_")
    for str in s:
        if (len(str)==5):
            return str
    if (plate is None):
        print >> sys.stderr, 'For directory [', d, '] a platename could not be determined!'
        sys.exit(1) 
            
def make_files (map3file, callssuffix, confssuffix, plateMapPath, pedigreePath, threshold, directories, outputdir, reIndex):
    if not os.path.exists(outputdir):
        os.mkdir(outputdir)
        
    for d in directories:
        callsFile = getsuffixFile(d, callssuffix)
        confsFile = getsuffixFile(d, confssuffix)
        plateName=getPlateName(d)
        plateMap= getPrePlinkArtifact(plateMapPath, plateName, ".platemap")
        pedigree= getPrePlinkArtifact(pedigreePath, plateName, ".pedigree")
        if not outputdir.endswith("/"):
            outputdir+="/"
        
        args = [
            "make_ped_and_map_file"]
        if map3file is not None:
            args.extend (["--map3", map3file])
         
        args.extend (
            [
             "--platemap", plateMap,
            "--pedigree", pedigree,
            "--calls", callsFile,
            "--confidences", confsFile,
            "--threshold", threshold,
            "--output-map", (outputdir + plateName + ".map"),
            "--output-ped", (outputdir + plateName + ".ped"),
            ])
        print(args)
        make_ped_and_map_file.main(args)


def merge_peds (directories, outputdir):
    """Gathers up all the .ped files in the outputdir, and hands them off to the merge script.
    Produces a merged.ped file in the output directory."""
    if not outputdir.endswith("/"):
        outputdir+="/"
    files = []
    for d in directories:
        f= outputdir+getPlateName(d)+".ped"
        files.append(f)
        
    args = ["merge_pedfiles",
    "--out-file", outputdir + "merged.ped"]
    for f in files:
        args.append(f)

    print (args)
    merge_pedfiles.main(args)

def compile_plink (directories, outputdir, excludeMESNP, excludeMEFamily, rootName="plink"):
    if not outputdir.endswith("/"):
        outputdir+="/"
    examplePlate=getPlateName(directories[0])
    mapfile = outputdir + examplePlate + ".map"
    pedfile = outputdir + "merged.ped"
    plinkout=outputdir + rootName
    args = ["plink_compile", 
            "--ped", pedfile,
            "--map", mapfile,
            "--out", plinkout,
            "--exclude-mendel-error-snp", excludeMESNP,
            "--exclude-mendel-error-family", excludeMEFamily]
    print (args)
    plink_compile.main(args)
    
    
def summarize (outputdir):
    if not outputdir.endswith("/"):
        outputdir+="/"
    bed=outputdir + "plink.bed"
    bim=outputdir + "plink.bim"
    fam=outputdir + "plink.fam"
    
    args=["plink_summarize",
          "--bed", bed,
          "--bim", bim,
          "--fam", fam]
    print (args)
    olddir=os.getcwd()
    os.chdir(outputdir)
    plink_summarize.main(args)
    os.chdir(olddir)
    
def main(argv=None):
    if argv is None:
        argv = sys.argv
        
    if argv is None:
        argv=sys.argv

    parser = optparse.OptionParser(usage=__doc__)

    parser.add_option("--map3", dest="map3Path", default="/humgen/cnp04/sandbox/data/TEST_DATA_SET/pre_plink_artifacts/500b.map3",
                      help="""tab-delimited map3 file with 3 columns: chromosome, SNP, position.
Default:/humgen/cnp04/sandbox/data/TEST_DATA_SET/pre_plink_artifacts/500b.map3""")
    
    parser.add_option("--platemap", dest="plateMapPath", default=None,
                      help="""tab-delimited file with 3 columns: container, well, participant ID, used to determine a participant ID for plates.
Each of these files should look like the plate name with a filetype of .platemap.  EG: hurts.platemap""")
        
    parser.add_option("--pedigree", dest="pedigreePath", default=None,
                      help="""tab-delimited file with 5 columns: Family ID, Individual ID, Father ID, Mother ID, Gender (1=M, 2=F)
Each of these files should look like the platename with a filetype of .pedigree.  EG: hurts.pedigree""")
        
    parser.add_option("--calls", dest="callsSuffix", default=None,
                      help="""The suffix of the tab-delimited files with 1 line for each SNP, 1 column for each genotype call, 
plus 1st column is SNP name.  Header line has CEL file name 
for each column of genotypes.  Genotypes are: 0=AA, 1=AB, 2=BB.
For each directory given, a calls file will be searched for that looks like *<suffix>
EG: birdseed_aspen_q1c86p1_calls_snp_list_sample_snp_filtered.txt 
would have the suffix 'calls_snp_list_sample_snp_filtered.txt'""")
    
    parser.add_option("--confidences", dest="confsSuffix", default=None,
                      help="""The suffix of the tab-delimited file identical to calls file, 
except that each value in the matrix is a confidence of the
corresponding genotype call in the calls file.
For each directory given, a confidence file will be searched for that looks like *<suffix>
EG: birdseed_aspen_q1c86p1_confs_snp_list_sample_snp_filtered.txt would have the suffix confs_snp_list_sample_snp_filtered.txt""")
    
    parser.add_option("--threshold", dest="threshold", type="float", default="0.1",
                      help="If a genotype has confidence > this value, it is considered a no-call.  Defaults to 0.1")

    parser.add_option("--output-dir", dest="outputdir", default=None,
                      help="""A directory where the output of these operations will be written""")
    
    parser.add_option("--which-re", dest="reIndex", type="int",
                      help="Index of regular expression to use in conjunction with platemap.  Default: 0",
                      default=0)
    
    parser.add_option('--exclude-mendel-error-snp', dest="excludeMESNP", default=1,
                      help="""Let plink filter Mendel errors on a SNP by SNP basis.  This excludes all SNPs with an error rate higher than the number given.
                      This may be combined with the family based Mendel error exclusion parameter.  In that case, both filters will be run concurrently.
                      This option is set to 1 by default.""")
    
    parser.add_option('--exclude-mendel-error-family', dest='excludeMEF', default=1, 
                      help="""Let plink filter Mendel errors on a family by family basis.  
This excludes all families with an error rate higher than the number given. This may be combined with the 
SNP based Mendel error exclusion parameter.  In that case, both filters will be run concurrently.
This option is set to 1 by default.""")
    
    parser.add_option('--skip-summary', dest='skipSummary', default=False,
                      help="""If you do not wish to generate summary data, set this to true""")
    
    parser.add_option('--outputFileNameRoot', dest='rootName', default='plink', 
                      help="""What is the root name for the files comming out of plink?  
This is equivilent to the --out option in plink.""")
    options, lstArgs = parser.parse_args(argv)

    argCount = len(lstArgs)-1
    
    if argCount == 0:
        print ("Must supply a list of directories that contain calls and confidence files to run plink on!")
        parser.print_help()
        sys.exit()

    lstRequiredOptions=["plateMapPath", "pedigreePath", "callsSuffix", "confsSuffix", "outputdir"]
 
    for strOpt in lstRequiredOptions:
        if getattr(options, strOpt) is None:
            print >> sys.stderr, 'ERROR:', strOpt, 'argument is required.'
            parser.print_help()
    directories=lstArgs[1:len(lstArgs)]
    
    make_files(options.map3Path, options.callsSuffix, options.confsSuffix, options.plateMapPath, options.pedigreePath, options.threshold, directories, options.outputdir, options.reIndex)
    merge_peds(directories, options.outputdir)
    compile_plink(directories, options.outputdir, options.excludeMESNP, options.excludeMEF, options.rootName)
    if options.skipSummary is False:
        summarize (options.outputdir)
    print("Finishing run plink population")

if __name__ == '__main__':
    sys.exit(main())
