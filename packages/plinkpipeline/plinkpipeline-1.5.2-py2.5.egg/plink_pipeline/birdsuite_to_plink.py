#!/usr/bin/env python
from plink_pipeline import create_map, birdseye_to_cnv, canary_merge, canary_to_gvar, fawkes_to_gvar, fawkes_to_diploid, fawkes_merge, make_tped, make_tfam, fam_to_gender
import optparse
import sys, os, getopt, re
from mpgutils import utils

def main(argv = None): 
    if not argv:
        argv = sys.argv
    
    lstRequiredOptions=["metadir", "plateroot", "familyfile"]
    parser = optparse.OptionParser(usage=__doc__)
    #REQUIRED
    parser.add_option("-p", "--plateroot",
                      help="""(Required) Contains folders with larry-bird style files""")
    parser.add_option("-f", "--familyfile",
                      help="""(Required) PLINK formatted .fam file""")
    parser.add_option("-x", "--metadir",
                      help="(Required) Meta directory holding CNV data")
    #OPTIONAL
    parser.add_option("-d", "--outputdir",
                      help ="Define the directory for output files")
    parser.add_option("-m", "--celmap", dest="celmap",
                      help="Cel Map file")
    parser.add_option("-t", "--threshold", default=0.1,
                      help ="define a cutoff for confidence data")
    parser.add_option("-n", "--outputname", default="Output",
                      help="Define the file name root for the output files")
    parser.add_option("-c", "--chip", default='6',
                      help="Chip Type, Use either '5' or '6'")
    parser.add_option("-b", "--build", default='18',
                      help="Human Genome Build, Use either '17' or '18'")
    parser.add_option("-a", "--noallelemap", default=False, action="store_true",
                      help="""Do not convert Probes to Alleles""") 
    parser.add_option("-v", "--verifyfam", default=True, action="store_false",
                      help="""Disable pedigree checking""") 
    parser.add_option("-r", "--norscoding", default=False, action="store_true",
                      help="""Do not convert SNP id to RS id""") 
    parser.add_option("-j", "--nomerge", default=False, action="store_true",
                      help="""Do not merge data again (Useful if you are running different analysis on same data)""")
    parser.add_option("-k", "--nodip", default=False, action="store_true",
                      help="""Do not make Diploid files again""") 
    parser.add_option("-l", "--nomap", default=False, action="store_true",
                      help="""Do not make Map files""")
    parser.add_option("-1", "--firstStep", default=False, action="store_true",
                      help="Run the steps: Birdseye to CNV")
    parser.add_option("-2", "--secondStep", default=False, action="store_true",
                      help="Run the steps: Canary Merge, Canary to Gvar")
    parser.add_option("-3", "--thirdStep", default=False, action="store_true",
                      help="Run the steps: Create Gender Files")
    parser.add_option("-4", "--fourthStep", default=False, action="store_true",
                      help="Run the steps: Fawkes Merge, Fawkes to Gvar")
    parser.add_option("-5", "--fifthStep", default=False, action="store_true",
                      help="Run the steps: Fawkes Merge, Fawkes to Diploid")
    parser.add_option("-6", "--sixthStep", default=False, action="store_true",
                      help="Run the steps: Make Tped, Make Tfam")
    
    dctOptions, lstArgs = parser.parse_args(argv)
    if not utils.validateRequiredOptions(dctOptions, lstRequiredOptions):
        parser.print_help()
        return 1
    
    #VALIDATE PARAMETERS
    lstValidChips = ['5', '6']
    if not (dctOptions.chip in lstValidChips):
        print "You entered a wrong chip type"
        sys.exit(1)
        
    lstValidBuilds = ['17', '18']
    if not (dctOptions.chip in lstValidChips):
        print "You entered a wrong chip type"
        sys.exit(1)
        
    #VALIDATE OUTPUT
    if not dctOptions.outputdir:
        setattr(dctOptions, 'outputdir', sys.path[0])
        
    #CHECK IF USER WANTS GENERIC RUN
    if not (dctOptions.firstStep or dctOptions.secondStep or dctOptions.thirdStep or dctOptions.fourthStep or dctOptions.fifthStep or dctOptions.sixthStep):
        setattr(dctOptions, 'firstStep', True)
        setattr(dctOptions, 'secondStep', True)
        setattr(dctOptions, 'thirdStep', True)
        setattr(dctOptions, 'fourthStep', True)
        setattr(dctOptions, 'fifthStep', True)
        setattr(dctOptions, 'sixthStep', True)
        
    #VALIDATE PATHS
    lstOptionsToCheck = ['familyfile', 'plateroot', 'metadir', 'outputdir']
    if dctOptions.celmap:
        lstOptionsToCheck.append("celmap")
    utils.validatePathArgs(dctOptions, lstOptionsToCheck, True)
    
    print """
    =========================================================
    =             BIRDSUITE -> PLINK PIPELINE               =
    ========================================================="""
    fawkesismerged = False
    
    #VERIFY FAM FILE
    if dctOptions.verifyfam:
        if not utils.checkFamFile(dctOptions.familyfile, 0.5):
            print "WARNING:"
            print "Family file is missing more than 50% phenotypic information"
            print "It is recommended that you provide this information"
            print "**To disable this check use --verifyfam"
            sys.exit(2)
        
    #CREATE MAP
    if not dctOptions.nomap:
        possible_args = ["metadir", "outputdir", "outputname", "chip", "build"]
        current_args = MakeArguments(possible_args, dctOptions)
        print "\n-----CREATE-MAP-----"
        create_map.main(current_args)
            
    #FIRST STEP
    if dctOptions.firstStep:
        print "\n==(1)=="
        
        #BIRDSEYE TO CNV
        possible_args = ["plateroot", "outputdir", "familyfile", "celmap", "outputname"]
        current_args = MakeArguments(possible_args, dctOptions)
        print "\n-----BIRDSEYE->CNV-----"
        birdseye_to_cnv.main(current_args)
    
    #SECOND STEP
    if dctOptions.secondStep: 
        print "\n==(2)=="
        
        if not dctOptions.nomerge:
            #CANARY MERGE
            possible_args = ["plateroot", "outputname"]
            current_args = MakeArguments(possible_args, dctOptions)
            print "\n-----CANARY-MERGE-----"
            canary_merge.main(current_args)
        
        #CANARY TO GVAR
        possible_args = ["plateroot", "outputdir", "familyfile", "threshold", "celmap", "outputname"]
        current_args = MakeArguments(possible_args, dctOptions)
        print "\n-----CANARY->GVAR-----"
        canary_to_gvar.main(current_args)
     
      
    #THIRD STEP
    if dctOptions.thirdStep:
        print "\n==(3)=="
        
        #MAKE GENDER FILES
        possible_args = ["plateroot", "outputdir", "familyfile", "outputname", "celmap"]
        current_args = MakeArguments(possible_args, dctOptions)
        print "\n-----FAM->GENDER-----"
        fam_to_gender.main(current_args)
        
    #FOURTH STEP
    if dctOptions.fourthStep:
        print "\n==(4)=="
        
        #MERGE FAWKES DATA
        if not dctOptions.nomerge:
            fawkesismerged = FawkesMerge(fawkesismerged,dctOptions)
        
        #FAWKES TO GVAR
        possible_args = ["plateroot", "outputdir", "familyfile", "threshold", "celmap", "outputname", "metadir", "noallelemap", "norscoding"]
        current_args = MakeArguments(possible_args, dctOptions)
        print "\n-----FAWKES->GVAR-----"
        fawkes_to_gvar.main(current_args)
        
    #FIFTH STEP
    if dctOptions.fifthStep:
        print "\n==(5)=="
        
        #MERGE FAWKES DATA
        if not dctOptions.nomerge:
            fawkesismerged = FawkesMerge(fawkesismerged,dctOptions)
            
        #FAWKES TO DIPLOID
        possible_args = ["plateroot", "metadir", "chip"]
        current_args = MakeArguments(possible_args, dctOptions)
        print "\n-----FAWKES->DIPLOID-----"
        fawkes_to_diploid.main(current_args)
                
    #SIXTH STEP
    if dctOptions.sixthStep:
        print "\n==(6)=="
        
        #MAKE TPED
        possible_args = ["plateroot", "metadir", "chip", "build", "outputdir", "outputname", "threshold"]
        current_args = MakeArguments(possible_args, dctOptions)
        print "\n-----MAKE-TPED-----"
        make_tped.main(current_args)
        
        #MAKE TFAM
        possible_args = ["plateroot","familyfile", "outputdir", "outputname", "celmap"]
        current_args = MakeArguments(possible_args, dctOptions)
        print "\n-----MAKE-TFAM-----"
        make_tfam.main(current_args)
        
def FawkesMerge(fawkesismerged, dctOptions):
    
    if not fawkesismerged:
        #FAWKES MERGE
        possible_args = ["plateroot", "outputname"]
        current_args = MakeArguments(possible_args, dctOptions)
        print "\n-----FAWKES-MERGE-----"
        fawkes_merge.main(current_args)
        return True
        
def MakeArguments(possible_args, dctOptions):
    current_args = []
    for key in possible_args:
        item = getattr(dctOptions, key)
        if not item == None:
            if item == True:
                current_args.append("--" + key)
            elif item == False:
                continue
            else:
                current_args.append("--" + key)
                current_args.append(item)
    return current_args
    
    
if __name__ == "__main__":
    main()  
    
