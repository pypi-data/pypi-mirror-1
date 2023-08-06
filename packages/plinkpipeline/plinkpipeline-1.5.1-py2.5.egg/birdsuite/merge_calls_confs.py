#!/usr/bin/env python
# The Broad Institute
# SOFTWARE COPYRIGHT NOTICE AGREEMENT
# This software and its documentation are copyright 2007 by the
# Broad Institute/Massachusetts Institute of Technology. All rights are
# reserved.

# This software is supplied without any warranty or guaranteed support
# whatsoever. Neither the Broad Institute nor MIT can be responsible for its
# use, misuse, or functionality.
# $Header$
"""usage %prog [options]
Make a guide file from a cel_map file mapping a cel file to a sample name,
and a  list of celFiles in a calls file.
"""

from __future__ import division
import optparse
import sys
import string
from mpgutils import utils

lstRequiredOptions=["pedigree", "output", "celMap"]

def mergeFiles (lstFiles, outFile):
    lstFileHandles=[open(f, 'r') for f in lstFiles]
    startHandle=lstFileHandles[1]
    out = open (outFile, "w")
    
    successFlag=True
    while startHandle:
        
        lines=[f.readline() for f in lstFileHandles]
        data=lines[0].split()
        
        if len(data)==0: break;  #hit the end of the data.
        
        id=data[0]            
        otherLines=lines[1:]
        otherLines=[l.split() for l in otherLines]
        
        otherIDs=[l[0] for l in otherLines]
        for o in otherIDs:
            if o!=id: 
                print ("Line of first file and subsequent file don't match:" + "original[" + id + "] new [" + o +"]")
                successFlag=False
            
        otherLines=[l[1:] for l in otherLines]
        
        for l in otherLines: data.extend(l)
        data.append("\n")
        finalLine = "\t".join(data)
        out.write(finalLine)
        
    out.close()    
    return (successFlag)

def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = optparse.OptionParser(usage=__doc__)
    
    parser.add_option("-o", "--output", default=None,
                      help="""(Required) Output a single calls or confs file that 
                      is the result of merging multiple calls/confs files""")

    dctOptions, lstArgs = parser.parse_args(argv)
    lstRequiredOptions=["output"]
    
    if not utils.validateRequiredOptions(dctOptions, lstRequiredOptions):
        parser.print_help()
        return 1
    
    lstFiles = lstArgs[1:len(lstArgs)]
    successFlag=mergeFiles(lstFiles, dctOptions.output)
    if successFlag: print ("Finished Merge Successfully")
    
if __name__ == "__main__":
    sys.exit(main())
    
