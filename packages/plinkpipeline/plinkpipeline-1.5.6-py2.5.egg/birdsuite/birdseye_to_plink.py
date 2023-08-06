#!/usr/bin/env python
from optparse import OptionParser
import sys, os, getopt, re

dctCelFileMap = {}
dctFamMap = {}
dctFamMissing = {}

def main():    
    #OPTION PARSING!

    usage = "usage: %prog [options] {outputdirectory} {plateroot} {familyfile} ::: -h for help"
    parser = OptionParser(usage)
    parser.add_option("-o", "--outputname", dest="outputname",
                      help="define the file name root for the output files")
    parser.add_option("-m", "--celmap", dest="celmap",
                      help="Cel Map file")
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose")
    (options, args) = parser.parse_args()
    
    #OUTPUT FILE
    if options.outputname == None:
        output_name = "Output"
    else:
        output_name = options.outputname
    
    #CEL MAP FILE
    if options.celmap:
        if (os.path.exists(os.path.expanduser(options.celmap))):
            cel_map_file = os.path.expanduser(options.celmap)
        else:
            print "Could not find CEL Map @ " + options.celmap
            sys.exit(2)

    #SET PATHS
    if (len(args) == 3):
        
        output_root = args[0]
        plate_root = args[1]
        family_file = args[2]
    
        if (os.path.exists(os.path.expanduser(output_root))):
            output_root = os.path.abspath(os.path.expanduser(output_root))
        else:
            print "Could not find Output Root @ " + output_root
            sys.exit(2)
            
        if (os.path.exists(os.path.expanduser(plate_root))):
            plate_root = os.path.abspath(os.path.expanduser(plate_root))
        else:
            print "Could not find Plate Root @ " + plate_root
            sys.exit(2)
        if (os.path.exists(os.path.expanduser(family_file))):
            family_file = os.path.expanduser(family_file)
        else:
            print "Could not find Family File @ " + family_file
            sys.exit(2)
    else:
        print parser.usage
        sys.exit(2)      

    #PLATE INFORMATION
    BirdsEyePaths = []
    for root, dirs, files in os.walk(plate_root, False):
        for name in files:
            if (name[len(name)-14:] == 'birdseye_calls'):
                BirdsEyePaths.append(os.path.join(root, name))
    #END INITIALIZE FILES
        
    #FAMILY FILE    
    print "Loading Family File..."
    ReadFamFile(family_file)
    print "Done."   

    #CEL MAP FILE
    if options.celmap:
        print "Loading Celmap..."
        ReadCelMapFile(cel_map_file)
        print "Done."
    
    #PLATES
    print "Starting Plates..."
        #CNV FILE
    cnvFile = open(os.path.join(output_root, output_name + ".cnv"), "w")
    cnvFile.write("FID\tIID\tCHR\tBP1\tBP2\tTYPE\tSCORE\tSITE\n")
    
    for BirdsEyePath in BirdsEyePaths:
        BirdsEyeCallFile = open(BirdsEyePath)
        ReadPlateFile(BirdsEyeCallFile, cnvFile, options)
        
    print "Done."
        
    #MAKE LOG FILE
    if (len(dctFamMissing) > 0):
        MakeLog(dctFamMissing, output_root, output_name)
    
    print "Exiting."

def MakeLog(dctFamMissing, output_root, output_name):
    
    print "Writing Log File.."
    debugOut = open(os.path.join(output_root, output_name + ".cnv.log"), "w")
    debugOut.write("#MISMATCH  //This details the keys that could not be matched" + "\n")
    for key in dctFamMissing.keys():
        debugOut.write(key + "\n")
    print "Done."
    
def ReadPlateFile(BirdsEyeCallFile, cnvFile, options):
    global dctFamMissing
    header_complete = False
    
    for strLine in BirdsEyeCallFile:
        Fields=strLine.split()
        
        if(header_complete == False):
            header_complete=True
            continue
        
        ID = StripCelExt(Fields[0])
        if options.celmap:
            if dctCelFileMap.has_key(ID):
                ID = dctCelFileMap[ID]
                
        if dctFamMap.has_key(ID):
            FID = dctFamMap[ID]
        else:
            if not dctFamMissing.has_key(ID):
                dctFamMissing[ID] = True
            continue
        
        #DATA COLLECTION
        Type = Fields[2]
        Chrom = Fields[3]
        SPos = Fields[4]
        EPos = Fields[5]
        Score = Fields[9]
        if Score == '-Inf':
            Score = 0
            continue
        Site = Fields[8]
        if Site == '-Inf':
            Site = 0
            continue        
        
        cnvFile.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (FID,ID,Chrom,SPos,EPos,Type,Score,Site))  
        
          
def ReadFamFile (family_file):
    FamilyFile = open(family_file)
    global dctFamMap
    
    for strLine in FamilyFile:
        Fam_Value = []
        
        if(strLine[0]== '#'):
            continue
        
        Fields = strLine.split()
        
        IID=Fields[1]
        FID=Fields[0]
        dctFamMap[IID] = FID
        
def ReadCelMapFile (cel_map_file):
    CelMapFile = open(cel_map_file)
    global dctCelFileMap
        
    for strLine in CelMapFile:
        if(strLine[0]== '#'):
            continue
        
        Fields=strLine.split()   
        CelID=Fields[0]
        
        #Make sure .CEL isn't appended to the name
        CelID = StripCelExt(CelID)
            
        IID=Fields[1]
        dctCelFileMap[CelID] = IID
        
def StripCelExt(item):
    p = re.compile( '[.]cel', re.IGNORECASE )
    m = p.search(item)
    if m:
        item = item[:-4]
    return item

if __name__ == "__main__":
    main()
    
