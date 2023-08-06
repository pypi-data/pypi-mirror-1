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
"""usage: %prog [options] --basename BASENAME

Merge the birdseye calls files from subdirectories BASENAME.<chromosome_number>.birdseye_dir into
a single file in the current directory BASENAME.birdseye_calls.

Merge the birdseye CNclusters.txt files subdirectories BASENAME.<chromosome_number>.birdseye_dir into
a single file in the current directory BASENAME.birdseye_cn_clusters
"""

from __future__ import division
import bisect
import copy
import fileinput
import math
import optparse
import os
import sys

import cn_create_exclude_list
import cnv_definition_collection
import pre_birdseye
from mpgutils import utils

# Indices of attributes in birdseye and canary records
iSAMPLE_NUMBER_INDEX=0
iCOPY_NUMBER_INDEX=1
iCHROMOSOME_INDEX=2
iSTART_INDEX=3
iEND_INDEX=4

strBIRDSEYE_OUTPUT_FILENAME = "cn_segments.txt"

lstRequiredOptions = ["basename", "cnv_defs", "output", "probe_locus"]

def makeBirdseyeDirList(strBasename, strRootDir):
    """Create a list of birdseye subdirectories in chromosome order"""
    strDirectoryPrefix = strBasename + "."
    lstDirs = [strDir for strDir in os.listdir(strRootDir) \
               if strDir.startswith(strDirectoryPrefix) and \
               strDir.endswith(pre_birdseye.strBIRDSEYE_DIRECTORY_EXTENSION)]

    def cmpDirectories(strA, strB):
        """Defined in line in order to access strDirectoryPrefix."""
        assert(strA.startswith(strDirectoryPrefix))
        assert(strA.endswith(pre_birdseye.strBIRDSEYE_DIRECTORY_EXTENSION))
        assert(strB.startswith(strDirectoryPrefix))
        assert(strB.endswith(pre_birdseye.strBIRDSEYE_DIRECTORY_EXTENSION))

        strAChr = strA[len(strDirectoryPrefix):-len(pre_birdseye.strBIRDSEYE_DIRECTORY_EXTENSION)]
        strBChr = strB[len(strDirectoryPrefix):-len(pre_birdseye.strBIRDSEYE_DIRECTORY_EXTENSION)]
        return cmp(int(strAChr), int(strBChr))

    lstDirs.sort(cmpDirectories)
    return lstDirs

def mergeCNClusters(strClusterOutputPath, strBasename, strRootDir):
    """Concatenate all CNclusters.txt files into strClusterOutputPath"""
    lstDirs = makeBirdseyeDirList(strBasename, strRootDir)
    fIn = fileinput.input([os.path.join(strRootDir, os.path.join(strDir, "CNclusters.txt")) for strDir in lstDirs])
    fOut = open(strClusterOutputPath, "w")
    for strLine in fIn:
        fOut.write(strLine)
    fOut.close()

def makeBirdseyeMergedFileReader(strRootDir, strBasename):
    """Return a file-like object that returns lines from the Birdseye calls file in genomic order"""
    lstDirs = makeBirdseyeDirList(strBasename, strRootDir)
    return fileinput.input([os.path.join(strRootDir, os.path.join(strDir, strBIRDSEYE_OUTPUT_FILENAME)) \
                            for strDir in lstDirs])

def concatenateBirdseyeCalls(strOutputPath, strRootDir, strBasename, lstSampleNames):
    """Create a file that is just the concatenation of Birdseye calls, with sample names added.
    Note that sample IDs in Birdseye output are one-based, and lstSampleNames is also one-based"""
    fOut = open(strOutputPath, "w")
    print >> fOut, "\t".join(["sample", "sample_index", "copy_number", "chr", "start", "end", "per_probe_score", "size", "num_probes", "lod_score"])
    fIn = makeBirdseyeMergedFileReader(strRootDir, strBasename)
    for strLine in fIn:
        lstFields = strLine.split(None, 1)
        strSampleName = lstSampleNames[int(lstFields[0])]
        fOut.write(strSampleName)
        fOut.write("\t")
        fOut.write(strLine)
    fOut.close()
    

class BirdseyeOutputIterator(object):
    def __init__(self, strBasename, strRootDir):
        self._fIn = makeBirdseyeMergedFileReader(strRootDir, strBasename)

        self._lstRecords = []
        self._bIterationDone = False

    def advance(self):
        """Advance to the next record in the file.  Return False if there are no more records.
        Must be called before the first record can be read."""
        if len(self._lstRecords) > 0:
            del self._lstRecords[0]
        if len(self._lstRecords) > 0:
            return True
        strCurrentLine = self._fIn.readline()
        if len(strCurrentLine) == 0:
            self._bIterationDone = True
            return False
        lstFields = strCurrentLine.split()
        for i in xrange(5):
            lstFields[i] = int(lstFields[i])
        # Replace 3 fields with LOD score.
        lstFields[5:] = [float(lstFields[8])]
        self._lstRecords = [lstFields]
        return True

    def current(self):
        """Returns a list or tuple (1-based-sample-number, num-copies, 1-based-chromosome-number,
        start-position, end-position, cooked score)"""
        return self._lstRecords[0]

    def split(self, iEnd):
        """Split the current record into two records.  The first record will end at iEnd,
        and the second record will begin at iEnd + 1"""
        assert(len(self._lstRecords) > 0)
        assert(self._lstRecords[0][iSTART_INDEX] <= iEnd)
        assert(self._lstRecords[0][iEND_INDEX] > iEnd)
        lstNew = self._lstRecords[0][:]
        self._lstRecords[0][iEND_INDEX] = iEnd
        lstNew[iSTART_INDEX] = iEnd + 1
        self._lstRecords.insert(1, lstNew)

    def done(self):
        return self._bIterationDone


def cmpCanaryTuple(a, b):
    """a and b are both tuples (cnvDefinition, iCall, fConf)"""
    iCmp = cmp(a[2], b[2])
    if iCmp != 0:
        return iCmp
    aCNVDef = a[0]
    bCNVDef = b[0]
    iCmp = cmp(aCNVDef.iChr, bCNVDef.iChr)
    if iCmp != 0:
        return iCmp
    # prefer longer to shorter -- I'm not sure if that is right.
    return -cmp(aCNVDef.length(), bCNVDef.length())

class CanaryOutputIterator(object):
    def __init__(self, strCNVDefinitionsFile, strCallsFile, strConfsFile, fConfidenceThreshold, fOutputScore):
        self._fOutputScore = fOutputScore
        cnvDefs = cnv_definition_collection.CNVDefinitionCollection(strCNVDefinitionsFile)
        dctCNVCalls = cn_create_exclude_list.loadCNVCalls(strCallsFile)
        dctCNVConfs = cn_create_exclude_list.loadCNVConfidences(strConfsFile)
        self._lstByChromosome = []
        if len(dctCNVCalls) == 0:
            iNumSamples = 0
        else: iNumSamples = len(dctCNVCalls.values()[0])

        lstTemplateBySample = [[] for i in xrange(iNumSamples)]
        lstCNVsBySample = [[] for i in xrange(iNumSamples)]
        
        # Group the CNV calls by sample, skipping no-calls or calls below threshold
        for strCNV, lstCalls in dctCNVCalls.iteritems():
            assert(len(lstCalls) == iNumSamples)
            if lstCalls[0] == 'NA':
                continue
            if strCNV not in dctCNVConfs:
                continue
            lstConfs = dctCNVConfs[strCNV]
            assert(len(lstConfs) == iNumSamples)
            if lstConfs[0] == 'NA':
                continue

            assert(strCNV.startswith("CNP"))
            cnvDef = cnvDefs.getCNV(strCNV)
            cnvDef.iChr = int(utils.convertChromosomeStr(cnvDef.strChrName))

            for iSampleNum in xrange(iNumSamples):
                iCall = lstCalls[iSampleNum]
                fConf = lstConfs[iSampleNum]
                if iCall == -1 or fConf > fConfidenceThreshold:
                    continue
                lstCNVsBySample[iSampleNum].append((cnvDef, iCall, fConf))

        for iSampleNum, lstCNVTuples in enumerate(lstCNVsBySample):
            # sort each sample's calls by (confidence, chromosome, length)
            lstCNVTuples.sort(cmpCanaryTuple)

            # separate each sample's calls by chromosome, discarding conflicting
            # calls of worse confidence or shorter length.
            for tupCNV in lstCNVTuples:
                cnvDef, iCall, fConf = tupCNV
                # Extend list if this chromosome hasn't been seen before
                if len(self._lstByChromosome) < cnvDef.iChr:
                    self._lstByChromosome += \
                               [copy.deepcopy(lstTemplateBySample)
                                for i in xrange(cnvDef.iChr - len(self._lstByChromosome))]

                lstTuplesForSample = self._lstByChromosome[cnvDef.iChr - 1][iSampleNum]

                # already organized by sample and chromosome, so don't need them.
                # Order of tuple is important, so that bisect works properly.
                tupToInsert = [cnvDef.iStartPosn, cnvDef.iEndPosn, fConf, iCall]
                # find insertion point for this CNV call
                iInsertPosn = bisect.bisect(lstTuplesForSample, tupToInsert)

                # discard it if it overlaps an existing call, since the existing call is better.
                if iInsertPosn > 0 and lstTuplesForSample[iInsertPosn-1][1] >= cnvDef.iStartPosn:
                    continue
                if iInsertPosn < len(lstTuplesForSample) and \
                       lstTuplesForSample[iInsertPosn][0] <= cnvDef.iEndPosn:
                    continue
                lstTuplesForSample.insert(iInsertPosn, tupToInsert)

        # Initialize iteration variables
        self._iCNVIndex = -1
        self._iSampleIndex = 0
        self._iChrIndex = 0
        self._bIterationDone = False
            
    def advance(self):
        """Advance to the next record in the file.  Return False if there are no more records.
        Must be called before the first record can be read."""
        self._iCNVIndex += 1
        while True:
            # Need to loop because there might be a chromosome/sample combination for which
            # there is no CNV call within confidence threshold.
            if self._iCNVIndex >= len(self._lstByChromosome[self._iChrIndex][self._iSampleIndex]):
                self._iCNVIndex = 0
                self._iSampleIndex += 1
            if self._iSampleIndex >= len(self._lstByChromosome[self._iChrIndex]):
                self._iSampleIndex = 0
                self._iChrIndex += 1
            if self._iChrIndex >= len(self._lstByChromosome):
                self._bIterationDone = True
                return False
            if self._iCNVIndex < len(self._lstByChromosome[self._iChrIndex][self._iSampleIndex]):
                return True
            
    def current(self):
        """Returns a list or tuple (1-based-sample-number, num-copies, 1-based-chromosome-number,
        start-position, end-position, score (which is fixed for all canary calls))"""
        tup = self._lstByChromosome[self._iChrIndex][self._iSampleIndex][self._iCNVIndex]
        return (self._iSampleIndex+1, tup[3], self._iChrIndex + 1, tup[0], tup[1], self._fOutputScore)

    def split(self, iEnd):
        """Split the current record into two records.  The first record will end at iEnd,
        and the second record will begin at iEnd + 1"""
        lstCurrent = self._lstByChromosome[self._iChrIndex][self._iSampleIndex][self._iCNVIndex]
        lstNew = lstCurrent[:]
        assert(lstCurrent[0] <= iEnd)
        assert(lstCurrent[1] > iEnd)
        lstCurrent[1] = iEnd
        lstNew[0] = iEnd + 1
        self._lstByChromosome[self._iChrIndex][self._iSampleIndex].insert(self._iCNVIndex + 1, lstNew)
        
    def done(self):
        return self._bIterationDone

class ProbeCounter(object):
    def __init__(self, strProbeLocusPath):
        self._lstProbesByChromosome = []
        for lstFields in utils.iterateProbeLocus(strProbeLocusPath):
            iChromosome = int(lstFields[1])
            if iChromosome == 0:
                # Skip probe with no position
                continue
            iPosition = lstFields[2]
            while len(self._lstProbesByChromosome) < iChromosome + 1:
                self._lstProbesByChromosome.append([])
            self._lstProbesByChromosome[iChromosome].append(iPosition)
        for lst in self._lstProbesByChromosome:
            lst.sort()

    def countProbesInRange(self, iChromosome, iStartGenomicPosition, iEndGenomicPosition):
        assert(iStartGenomicPosition <= iEndGenomicPosition)
        iStartProbeIndex = bisect.bisect_left(self._lstProbesByChromosome[iChromosome], iStartGenomicPosition)
        iEndProbeIndex = bisect.bisect_right(self._lstProbesByChromosome[iChromosome], iEndGenomicPosition)
        return iEndProbeIndex - iStartProbeIndex
        
        
def writeOneFromSource(fOut, lst, lstSampleNames):
    # Convert from one-based sample index to sample name.
    lst = [lstSampleNames[lst[0]]] + list(lst)
    print >>fOut, "\t".join([str(val) for val in lst])

def writeAllFromSource(fOut, iterator, lstSampleNames):
    while not iterator.done():
        writeOneFromSource(fOut, iterator.current(), lstSampleNames)
        iterator.advance()

def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = optparse.OptionParser(usage=__doc__)
    parser.add_option("-b", "--basename",
                      help="""(Required)  Used to find the birdseye subdirectories.""")
    parser.add_option("--input_dir", default=".",
                      help="""Parent directory of the birdseye subdirectories.  Default: current directory""")
    parser.add_option("-c", "--cnv_defs",
                      help="""(Required)  CNV definitions file.  Must be relative to same genome build as birdseye calls.""")
    parser.add_option("--probe_locus",
                      help="""(Required)  List of SNP and CN probe locations, sorted by chromosome and position.
This is used to determine how many probes are encompassed by a Birdseye or Canary call.
Must be relative to same genome build as birdseye calls.""")
    parser.add_option("--canary_calls", 
                      help="""(Required)  Canary calls file.""")
    parser.add_option("--canary_confs", 
                      help="""(Required)  Canary confidences file.""")
    parser.add_option("-o", "--output",
                      help="""(Required) Output file.""")
    
    parser.add_option("--birdseye_calls",
                      help="""If present, all the " + strBIRDSEYE_OUTPUT_FILENAME + " files will be concatenated into this file, 
with sample names added.""")
    
    parser.add_option("--cluster_output",
                      help="""CN probe cluster file.  If present, all the CNclusters.txt files will be concatenated into this file.""")
    
    parser.add_option("-t", "--canary_threshold", type="float", default="0.1",
                      help="""Discard canary calls > this.  Default: %default""")

    parser.add_option("--canary_score", type="float", default="10.0",
                      help="""All canary calls withing canary_threshold get this score in the output.  Default: %default""")
    parser.add_option("--birdseye_canary_overlap_threshold", type="int", default="2",
                      help="""If a birdseye call completely encloses a canary call, has the same copy number
as the canary call, and is not longer (in number of CN and SNP probes spanned) by at least this amount,
then discard the birdseye call.  Default: %default""")

    dctOptions, lstArgs = parser.parse_args(argv)
    if not utils.validateRequiredOptions(dctOptions, lstRequiredOptions):
        parser.print_help()
        return 1
    
    
    
    # Get sample names from canary_calls header line
    fCalls = open(dctOptions.canary_calls)
    strCallsHeader = utils.skipHeader(fCalls, "cnp_id")
    fCalls.close()
    lstSampleNames = strCallsHeader.split()
    
    birdseyeIterator = BirdseyeOutputIterator(dctOptions.basename, dctOptions.input_dir)

    canaryIterator = CanaryOutputIterator(dctOptions.cnv_defs,
                                          dctOptions.canary_calls,
                                          dctOptions.canary_confs,
                                          dctOptions.canary_threshold,
                                          dctOptions.canary_score)

    probeCounter = ProbeCounter(dctOptions.probe_locus)

    birdseyeIterator.advance()
    canaryIterator.advance()

    fOut = open(dctOptions.output, "w")
    print >> fOut, "\t".join(["sample", "sample_index", "copy_number", "chr", "start", "end", "confidence"])

    while True:
        if birdseyeIterator.done():
            writeAllFromSource(fOut, canaryIterator, lstSampleNames)
            break
        if canaryIterator.done():
            writeAllFromSource(fOut, birdseyeIterator, lstSampleNames)
            break
        lstCanary = canaryIterator.current()
        lstBirdseye = birdseyeIterator.current()
        iCmp = cmp(lstCanary[iCHROMOSOME_INDEX], lstBirdseye[iCHROMOSOME_INDEX])
        if iCmp == 0:
            iCmp = cmp(lstCanary[iSAMPLE_NUMBER_INDEX], lstBirdseye[iSAMPLE_NUMBER_INDEX])
        if iCmp == 0:
            if lstCanary[iEND_INDEX] < lstBirdseye[iSTART_INDEX]:
                iCmp = -1
            elif lstBirdseye[iEND_INDEX] < lstCanary[iSTART_INDEX]:
                iCmp = 1
        if iCmp < 0:
            writeOneFromSource(fOut, lstCanary, lstSampleNames)
            canaryIterator.advance()
        elif iCmp > 0:
            writeOneFromSource(fOut, lstBirdseye, lstSampleNames)
            birdseyeIterator.advance()
        else:
            # overlap
            if lstCanary[iCOPY_NUMBER_INDEX] == lstBirdseye[iCOPY_NUMBER_INDEX]:
                # copy numbers agree
                if lstBirdseye[iSTART_INDEX] <= lstCanary[iSTART_INDEX] and \
                       lstBirdseye[iEND_INDEX] >= lstCanary[iEND_INDEX]:
                    # one call is enclosed in the other, and their copy numbers agree
                    if probeCounter.countProbesInRange(lstBirdseye[iCHROMOSOME_INDEX],
                                                       lstBirdseye[iSTART_INDEX],
                                                       lstBirdseye[iEND_INDEX]) - \
                       probeCounter.countProbesInRange(lstCanary[iCHROMOSOME_INDEX],
                                                       lstCanary[iSTART_INDEX],
                                                       lstCanary[iEND_INDEX]) < \
                       dctOptions.birdseye_canary_overlap_threshold:
                        # Birdseye has mistakenly extended a common CNV by a little bit.  Discard birdseye call.
                        birdseyeIterator.advance()
                    else:
                        # Birdseye call is significantly longer than Canary call, so discard the Canary call
                        # since the longer Birdseye call has the same copy number
                        canaryIterator.advance()
                    continue
                if lstCanary[iSTART_INDEX] <= lstBirdseye[iSTART_INDEX] and \
                       lstCanary[iEND_INDEX] >= lstBirdseye[iEND_INDEX]:
                    # one call is enclosed in the other, and their copy numbers agree
                    birdseyeIterator.advance()
                    continue
                    
            # need to split
            if lstCanary[iSTART_INDEX] <= lstBirdseye[iSTART_INDEX]:
                # Canary record overlaps start of Birdseye record.
                # Split Birdseye record (unless it is completely enclosed
                # in the canary region) and discard overlapping region.
                if lstCanary[iEND_INDEX] < lstBirdseye[iEND_INDEX]:
                    birdseyeIterator.split(lstCanary[iEND_INDEX])
                birdseyeIterator.advance()
            else:
                # Birdseye record overlaps start of Canary record.
                # Split Birdseye record so there is a piece that end just before
                # start of canary record.
                birdseyeIterator.split(lstCanary[iSTART_INDEX] - 1)
            # Then just loop and next iteration should output the appropriate record.
                


    fOut.close()

    if dctOptions.birdseye_calls is not None:
        absBaseName=dctOptions.input_dir+'/'+ dctOptions.basename    
        concatenateBirdseyeCalls(dctOptions.birdseye_calls, dctOptions.input_dir, dctOptions.basename, lstSampleNames)
        concatenateBirdseyeResults(absBaseName +".cn_variances", dctOptions.input_dir, dctOptions.basename, lstSampleNames, "cn_sample_variances.txt")
        concatenateBirdseyeResults(absBaseName +".snp_variances", dctOptions.input_dir, dctOptions.basename, lstSampleNames, "snp_sample_variances.txt")
        concatenateBirdseyeResults(absBaseName +".chr_cn_estimates", dctOptions.input_dir, dctOptions.basename, lstSampleNames, "overall_cn_estimate.txt")
        
    if dctOptions.cluster_output is not None:
        mergeCNClusters(dctOptions.cluster_output, dctOptions.basename, dctOptions.input_dir)
    
    
def concatenateBirdseyeResults (strOutputPath, strRootDir, strBasename, lstSampleNames, targetFileName):
    #cut out the CNP id
    lstSampleNames=lstSampleNames[1:]
    fOut = open(strOutputPath, "w")
    lstHeaders="\t".join(["sample", "sample_index"])
    
    for x in range(1,25):
        lstHeaders="\t".join([lstHeaders,str(x)])
        
    print >> fOut, lstHeaders
    
    lstDirs=makeBirdseyeDirList(strBasename, strRootDir)
    
    dctFileHandles={}
    
    for d in lstDirs:
        fIn=open (strRootDir+'/'+d+'/'+targetFileName, 'r')
        dctFileHandles[d]=fIn
    
    for i in range (1, len(lstSampleNames)+1):
        
        strSampleName=lstSampleNames[i-1]
        fOut.write(strSampleName)
        fOut.write("\t")
        fOut.write(str(i))
        for d in lstDirs:
            line=dctFileHandles[d].readline().split()
            fOut.write("\t")
            fOut.write(line[1])
        fOut.write('\n')    
    fOut.close()        
               
        
if __name__ == "__main__":
    sys.exit(main())
    
