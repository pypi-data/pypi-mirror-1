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
"""usage %prog merge_file input_smart_probes > output_smart_probes

Each line in the merge file contains two or more CNP names.
Read the input_smart_probes, and write to stdout a smart probes file that has
the CNP names from the merge file merged.  The first CNP on each line in the merge
file is used as the output name for the merged CNP."""

from __future__ import division
import optparse
import sys

from mpgutils import utils

def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = optparse.OptionParser(__doc__)
    dctOptions, lstArgs = parser.parse_args(argv)

    if len(lstArgs) != 3:
        parser.print_help()
        return 1

    strMergePath = lstArgs[1]
    strSmartProbesPath = lstArgs[2]

    # Map from original name to merged name
    dctMergedCNPNameMap = {}
    for lstFields in utils.iterateWhitespaceDelimitedFile(strMergePath):
        strNewName = lstFields[0]
        for strCNP in lstFields:
            dctMergedCNPNameMap[strCNP] = strNewName


    stCNPProbePairsSeen = set()

    print "\t".join(["cnp_id", "probeset_id"])
    for lstFields in utils.iterateWhitespaceDelimitedFile(strSmartProbesPath, iNumFieldsExpected=2, bSkipHeader=True):
        strNewName = dctMergedCNPNameMap.get(lstFields[0], lstFields[0])

        tupOut = (strNewName, lstFields[1])
        # If probe was in both CNPs being merged, don't duplicate it
        if tupOut in stCNPProbePairsSeen:
            continue
        stCNPProbePairsSeen.add(tupOut)
        print "\t".join(tupOut)

if __name__ == "__main__":
    sys.exit(main())
    
