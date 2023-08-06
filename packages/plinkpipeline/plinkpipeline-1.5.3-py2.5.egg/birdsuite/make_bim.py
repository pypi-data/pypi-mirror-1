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

Make a PLINK BIM (binary map) file from an Affymetrix annotation file.

If a SNP is not found in the annotation file, or does not have locus information
in the annotation file, zeroes are written for the locus in the bim file.

If a SNP is not found in the annotation file, or does not have allele information
in the annotation file, zeros are written for the alleles in the bim file.
"""

from __future__ import division
import optparse
import sys

from mpgutils import utils

lstRequiredOptions=["output", "calls", "annotations"]

# Columns of interest in annotation file
lstCOLUMN_HEADERS = [
    'Probe Set ID',
    'dbSNP RS ID',
    'Chromosome',
    'Physical Position',
    'Strand',
    'Allele A',
    'Allele B'
    ]

# Positions in list of various attributes, after removing SNP name
iRS_NUMBER_INDEX = 0
iCHROMOSOME_INDEX = 1
iPOSITION_INDEX = 2
iSTRAND_INDEX = 3
iALLELE_A_INDEX = 4
iALLELE_B_INDEX = 5

strUNDEFINED = '---'

def convertChromosomeStr(strChr):
    '''This is different from the usual converstion.  PAR is considered a separate chromosome'''
    # Handle PAR like chrX
    if strChr == 'X':
        return '23'
    if strChr == 'Y':
        return '24'
    if strChr == 'PAR' or strChr == 'XY':
        return '25'
    if strChr == 'MT':
        return '26'
    return strChr



def writeBim(fOut, lstAnnotations, strSNP, bAffy_names, bAffy_strand, bVerbose):
    for strVal in lstAnnotations:
        assert(len(strVal) > 0)

    strOutputSNP = strSNP
    if not bAffy_names:
        if lstAnnotations[iRS_NUMBER_INDEX] == strUNDEFINED:
            if bVerbose:
                print >> sys.stderr, "WARNING: No RS number for", strSNP
        else:
            strOutputSNP = lstAnnotations[iRS_NUMBER_INDEX]
            if strSNP.startswith("AFFX-SNP"):
                strOutputSNP = strSNP + "__" + strOutputSNP

    strAAllele = lstAnnotations[iALLELE_A_INDEX]
    strBAllele = lstAnnotations[iALLELE_B_INDEX]
    if not bAffy_strand and lstAnnotations[iSTRAND_INDEX] == '-':
        strAAllele = utils.complementBase(strAAllele)
        strBAllele = utils.complementBase(strBAllele)

    strChr = convertChromosomeStr(lstAnnotations[iCHROMOSOME_INDEX])
    strPosn = lstAnnotations[iPOSITION_INDEX]
    if strChr == strUNDEFINED or strPosn == strUNDEFINED:
        if bVerbose:
            print >> sys.stderr, "WARNING: No locus for", strSNP
        strChr = "0"
        strPosn = "0"
    
    print >> fOut, "\t".join([strChr, strOutputSNP, "0", strPosn, strAAllele, strBAllele])

def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = optparse.OptionParser(usage=__doc__)
    parser.add_option("-a", "--annotations",
                      help="""(Required) Affymetrix annotation file.""")
    parser.add_option("-c", "--calls",
                      help="""(Required) Input calls file in traditional apt-probeset-genotype format or Larry Bird format.
This file is used only to get the order of SNPs.""")
    parser.add_option("-o", "--output",
                      help="""(Required) Output calls file in tped (transposed ped) format""")
    parser.add_option("--affy_names", default=False, action="store_true",
                      help="Output Affymetrix SNP names instead of using RS numbers when available.  Default: use RS number when available.")
    parser.add_option("--affy_strand", default=False, action="store_true",
                      help="Write alleles as they appear in annotation file, rather than converting to positive strand.  Default: convert alleles to positive strand")

    parser.add_option("-v", "--verbose", default=False, action="store_true",
                      help="Write informational message to stderr, e.g. that locus or allele information could not be found.")
    parser.add_option("--include_affx_snps", action="store_true", default=False,
                      help="""Include AFFX-SNP SNPs in the output.  Default: exclude these SNPs.""")

    dctOptions, lstArgs = parser.parse_args(argv)
    if not utils.validateRequiredOptions(dctOptions, lstRequiredOptions):
        parser.print_help()
        return 1

    iterAnnot = utils.parseAnnotationFile(dctOptions.annotations, bYieldHeaderLine=True)

    lstHeaders = iterAnnot.next()

    # Get the column indices for the desired columns
    lstColumnIndices = [lstHeaders.index(strHeader) for strHeader in lstCOLUMN_HEADERS]

    dctAnnotations = {}
    
    while True:
        try: lstFields = iterAnnot.next()
        except StopIteration: break
        lstValues = [lstFields[i] for i in lstColumnIndices]

        dctAnnotations[lstValues[0]] = lstValues[1:]

    fCalls = open(dctOptions.calls)
    utils.skipHeader(fCalls, "probeset_id")

    fOut = open(dctOptions.output, "w")

    for strLine in  fCalls:
        strSNP = strLine.split(None, 1)[0]
        if not dctOptions.include_affx_snps and strSNP.startswith("AFFX-SNP"):
            continue
        try:
            lstAnnotations = dctAnnotations[strSNP]
            writeBim(fOut, lstAnnotations, strSNP, dctOptions.affy_names, dctOptions.affy_strand, dctOptions.verbose)
        except KeyError:
            if dctOptions.verbose:
                print >> sys.stderr, "WARNING: No annotation found for", strSNP
            print >> fOut, "\t".join(["0", strSNP, "0", "0", "0", "0"])

    fOut.close()
    
if __name__ == "__main__":
    sys.exit(main())
    
