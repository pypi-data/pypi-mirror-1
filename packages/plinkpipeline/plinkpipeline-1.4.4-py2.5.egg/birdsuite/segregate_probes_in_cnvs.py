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
"""usage %prog [options]"""
from __future__ import division
import optparse
import sys

import cnv_definition_collection
from mpgutils import utils

lstRequiredOptions = ["probes_in_cnvs", "cnv_defs", "probes_not_in_cnvs", "probe_locus"]

def main(argv=None):
    if argv is None:
        argv = sys.argv
    parser = optparse.OptionParser(usage=__doc__)
    parser.add_option("-i", "--input",
                      help="""(Required)  List of probes to be divided into two groups.""")
    parser.add_option("-c", "--cnv_defs",
                      help="""(Required)  CNV definitions file.  Must be relative to same genome build as birdseye calls.""")
    parser.add_option("--probe_locus",
                      help="""(Required)  List of SNP and CN probe locations, sorted by chromosome and position.
This is used to determine how many probes are encompassed by a Birdseye or Canary call.
Must be relative to same genome build as birdseye calls.""")
    parser.add_option("--probes_in_cnvs",
                      help="""(Required)  Probes from input that are in a cnv are written to this file.""")
    parser.add_option("--probes_not_in_cnvs",
                      help="""(Required)  Probes from input that are not in a cnv are written to this file.""")

    dctOptions, lstArgs = parser.parse_args(argv)
    if not utils.validateRequiredOptions(dctOptions, lstRequiredOptions):
        parser.print_help()
        return 1

    cnvDefs = cnv_definition_collection.CNVDefinitionCollection(dctOptions.cnv_defs)
    dctProbeLocus = utils.loadProbeLocus(dctOptions.probe_locus)

    fInCNV = open(dctOptions.probes_in_cnvs, "w")
    fNotInCNV = open(dctOptions.probes_not_in_cnvs, "w")

    for lstFields in utils.iterateWhitespaceDelimitedFile(dctOptions.input, iNumFieldsExpected=1):
        strProbe = lstFields[0]
        try:
            (strChr, iPosn) = dctProbeLocus[strProbe]
        except KeyError:
            # If no locus for probe, it can't be in a CNV
            print >> fNotInCNV, strProbe
            continue
        if len(cnvDefs.getCNVsForLocus(strChr, iPosn)) > 0:
            print >> fInCNV, strProbe
        else: print >> fNotInCNV, strProbe

    fInCNV.close()
    fNotInCNV.close()
            
    
if __name__ == "__main__":
    sys.exit(main())
    
