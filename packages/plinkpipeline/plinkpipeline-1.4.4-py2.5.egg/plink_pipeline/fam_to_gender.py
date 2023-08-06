import optparse
import sys, os, getopt, re
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
                
if __name__ == "__main__":
    main() 