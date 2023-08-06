import optparse
import sys
import os
import re
import shutil
from mpgutils import utils

def main(argv = None):
      
    lstRequiredOptions=["plateroot", "familyfile"]
    parser = optparse.OptionParser(usage=__doc__)
    #REQUIRED
    parser.add_option("-f", "--familyfile",
                      help="""(Required) PLINK formatted .fam file""")
    parser.add_option("-p", "--plateroot",
                      help="""(Required) Contains folders with larry-bird style files""")
    #OPTIONAL
    parser.add_option("-d", "--outputdir",
                      help ="Define the directory for output files")
    parser.add_option("-n", "--outputname", default="Output",
                      help="Define the file name root for the output files")
    parser.add_option("-m", "--celmap",help="Cel Map file")
    dctOptions, lstArgs = parser.parse_args(argv)
    if not utils.validateRequiredOptions(dctOptions, lstRequiredOptions):
        parser.print_help()
        return 1
    
    #VALIDATE OUTPUT
    if not dctOptions.outputdir:
        setattr(dctOptions, 'outputdir', sys.path[0])
    
    #VALIDATE PATHS
    lstOptionsToCheck = ['familyfile', 'plateroot', 'outputdir']
    if dctOptions.celmap:
        lstOptionsToCheck.append("celmap")
    utils.validatePathArgs(dctOptions, lstOptionsToCheck, True)
    
    #DICTIONARIES
    dctFamMap = utils.readFamFile(dctOptions.familyfile)
    dctCelFileMap = utils.readCelMapFile(dctOptions.celmap)
        
    #PLATE INFORMATION
    pattern = re.compile("[.]larry_bird_calls", re.IGNORECASE)
    CallsPaths = utils.findFiles(dctOptions.plateroot, pattern)
    MakeGenderFiles(CallsPaths, dctOptions, dctCelFileMap, dctFamMap)
    
    #MERGE GENDER FILES
    gender_output = os.path.join(dctOptions.plateroot, dctOptions.outputname + ".merged.gen")
    pattern = re.compile('[.]gender', re.IGNORECASE)
    GenderPaths = utils.findFiles(dctOptions.plateroot,pattern)
    pattern = re.compile('[.]larry_bird_confs', re.IGNORECASE)
    ConfsPaths = utils.findFiles(dctOptions.plateroot,pattern)
    if len(GenderPaths) != len(ConfsPaths):
        print "\tThe number of Confidence Files and Gender files are not equal"
        print "\tFound " + len(GenderPaths) + " Gender Files, and " + len(ConfsPaths) + " Confidence Files."
        sys.exit(1)
    else:
        if len(GenderPaths) > 1:
            successFlag = MergeGenderFiles(GenderPaths, gender_output)
            if successFlag:
                print "\tGender Merge Finished"
            else:
                print "\tGender Merge Failed, please check your Pedigree file and celmap"
                sys.exit(2)
        else:
            if len(GenderPaths) == 1:
                print "There was only one gender file found, no merge required."
                print "Copying gender file to " + gender_output
                shutil.copy(GenderPaths[0], gender_output)
                
    print "Finished -- FamToGender.Py\n"
    
def MakeGenderFiles(CallsPaths, dctOptions, dctCelFileMap, dctFamMap):
    
    for file_path in CallsPaths:
        file = open(file_path)
        header_line = file.readline()
        celList = header_line.split()
        
        #OUTPUT FILE
        outpath, outputname = os.path.split(file_path)
        lstname = outputname.split(".")
        outputprefix = lstname[0]
        out_file = os.path.join(outpath, outputprefix + ".gender")
        fOut = open(out_file, "w")
        print >> fOut, "gender"
        
        #WRITE GENDER
        for item in celList:
            celid = utils.stripCelExt(item)
            if celid == 'probeset_id':
                continue
            if dctOptions.celmap:
                if dctCelFileMap.has_key(celid):
                    celid = dctCelFileMap[celid]
            if dctFamMap.has_key(celid):
                if dctFamMap[celid][4] == '0' or dctFamMap[celid][4] == '1' or dctFamMap[celid][4] == '2':
                    print >> fOut, dctFamMap[celid][4]
                else:
                    print >> fOut, 0
                    print "\tGender for " + celid + " is unrecognized (" + dctFamMap[celid][4] + "), setting to 0" 
            else:
                print "\tCould not find " + celid + " in pedigree, setting gender to 0"
                print >> fOut, 0
                
        fOut.close()
        
def MergeGenderFiles (lstFiles, outFile):
    
    fOut = open(outFile, 'w')
    headerisdone = False
    
    for file in lstFiles:
        fIn = open(file,'r')
        for line in fIn:
            if str(line).rstrip() == "gender":
                if headerisdone:
                    continue
                else:
                    headerisdone = True
            fOut.write(line)
        fIn.close()
    fOut.close()  
    return True
                
if __name__ == "__main__":
    main() 