#!/usr/bin/env python
# The Broad Institute
# SOFTWARE COPYRIGHT NOTICE AGREEMENT
# This software and its documentation are copyright 2008 by the
# Broad Institute/Massachusetts Institute of Technology. All rights are
# reserved.

# This software is supplied without any warranty or guaranteed support
# whatsoever. Neither the Broad Institute nor MIT can be responsible for its
# use, misuse, or functionality.
# $Header$
"""usage %prog merge_file input_science_map > output_science_map

Each line in the merge file contains two or more CNP names.
Read the input_science_map, and write to stdout a science map that has
the CNP names from the merge file merged.  The first CNP on each line in the merge
file is used as the output name for the merged CNP."""

from __future__ import division
import optparse
import sys

from mpgutils import utils

def mergeCNPDefinitions(lst1, lst2):
    if lst1[0] != lst2[0]:
        raise Exception("Chromosome mismatch in CNPs to be merged: " + str(lst1) + "; " + str(lst2))
    return [lst1[0], min(lst1[1], lst2[1]), max(lst1[2], lst2[2])]
                        

def cmpCNPs(str1, str2):
    if not str1.startswith("CNP"):
        raise Exception("strange CNP name: " + str1)
    if not str2.startswith("CNP"):
        raise Exception("strange CNP name: " + str2)
    i1 = int(str1[3:])
    i2 = int(str2[3:])
    return cmp(i1, i2)

def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = optparse.OptionParser(__doc__)
    dctOptions, lstArgs = parser.parse_args(argv)

    if len(lstArgs) != 3:
        parser.print_help()
        return 1

    strMergePath = lstArgs[1]
    strScienceMapPath = lstArgs[2]

    # Map from original name to merged name
    dctMergedCNPNameMap = {}
    for lstFields in utils.iterateWhitespaceDelimitedFile(strMergePath):
        strNewName = lstFields[0]
        for strCNP in lstFields:
            dctMergedCNPNameMap[strCNP] = strNewName

    # Map from CNP name to list of [chr, start, end]
    dctCNPAccumulator = {}
    for lstFields in utils.iterateWhitespaceDelimitedFile(strScienceMapPath, iNumFieldsExpected=4, bSkipHeader=True):
        strNewName = dctMergedCNPNameMap.get(lstFields[0], lstFields[0])
        lstGenomicCoordinates = [int(i) for i in lstFields[1:]]
        if strNewName not in dctCNPAccumulator:
            dctCNPAccumulator[strNewName] = lstGenomicCoordinates
        else:
            try:
                dctCNPAccumulator[strNewName] = mergeCNPDefinitions(dctCNPAccumulator[strNewName], lstGenomicCoordinates)
            except:
                print >> sys.stderr, "Error merging", lstFields[0], strNewName
                raise

    lstKeys = dctCNPAccumulator.keys()
    lstKeys.sort(cmpCNPs)
    print "\t".join(["cnp_id", "chr", "start", "end"])
    for strCNP in lstKeys:
        print "\t".join([strCNP] + [str(val) for val in dctCNPAccumulator[strCNP]])
    

if __name__ == "__main__":
    sys.exit(main())
    
