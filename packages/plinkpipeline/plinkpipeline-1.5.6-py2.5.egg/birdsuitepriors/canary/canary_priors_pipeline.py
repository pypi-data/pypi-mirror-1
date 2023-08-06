'''
Created on Aug 27, 2009

@author: nemesh
'''

import optparse
import sys
import mpgutils.utils as utils

import birdsuite.cn_annotate_allele_summary
import birdsuite.cn_locus_summarize
import birdsuite.cn_probeset_summarize
import birdsuitepriors.canary.prep_clusters
from mpgutils.RUtils import RscriptToPython

class EnvironmentSpec(object):
    def __init__(self, intensityFile, genotypeFile, probe_locus, tempDir, basename, outputFile, force_cn_summarization, cnpDefsFile, missingValueLabel):
        self._intensityFile = intensityFile
        self._genotypeFile = genotypeFile
        self._tempDir = tempDir
        self._outputFile = outputFile
        self._probe_locus= probe_locus
        self._basename = basename
        self._force_cn_summarization = force_cn_summarization
        self._cnpDefsFile = cnpDefsFile
        self._missingValueLabel = missingValueLabel
        
    def probe_locus(self):
        return self._probe_locus
    
    def missingValueLabel(self):
        return self._missingValueLabel
    
    def cnpDefsFile(self):
        return self._cnpDefsFile
    
    def intensityFile(self):
        return self._intensityFile

    def genotypeFile(self):
        return self._genotypeFile
    
    def genotypesFiltered(self):
        return self._genotypesFiltered
    
    def setGenotypesFiltered (self, genotypesFiltered):
        self._genotypesFiltered=genotypesFiltered
        
    def tempDir(self):
        return self._tempDir
    
    def outputFile(self):
        return self._outputFile
    
    def basename(self):
        return self._basename
    
    def sumZFile(self):
        if self._tempDir is not None :
            return (self._tempDir+"/birdseed.sumz")

    def force_cn_summarization(self):
        return self._force_cn_summarization
    
    def annotateAlleleSummaryOut(self):
        outFile=self._tempDir+"/"+ self._basename+ ".annotated_summary"
        return (outFile)
    
    def locusSummarizeOut(self):
        outFile=self._tempDir+"/"+ self._basename+ ".locus_summary"
        return (outFile)
    
    def cnSummarizeOut(self):
        outFile=self._tempDir+"/"+ self._basename+ ".probeset_summary"
        return (outFile)
    
    def prepClusterOut(self):
        outFile=self._tempDir+"/"+ self._basename+ ".prepped_clusters"
        return (outFile)
        
def annotate_allele_summary(envSpec):
    argv=["cn_annotate_allele_summary",
          "--probe_locus", envSpec.probe_locus(),
          "--summary",envSpec.intensityFile(),
          "--output", envSpec.annotateAlleleSummaryOut(),
          "--tmpdir", envSpec.tempDir()]
    
    birdsuite.cn_annotate_allele_summary.main(argv)
    print ("FINISHED annotate allele summary")
    
def locus_summarize(envSpec):
    argv=["cn_locus_summarize", 
          "--output", envSpec.locusSummarizeOut()]
    if envSpec.force_cn_summarization():
          t=["--force_cn_summarization", envSpec.force_cn_summarization()]
          argv.extend(t)
          
    argv.extend([envSpec.annotateAlleleSummaryOut()])
    
    
    birdsuite.cn_locus_summarize.main(argv)
    print ("FINISHED locus summarize")
    
def cn_summarize(envSpec):
    argv=["cn_probeset_summarize",
          "--cnps", envSpec.cnpDefsFile(),
          "--output", envSpec.cnSummarizeOut(),
          "--missing_value_label", envSpec.missingValueLabel(),
          "--output", envSpec.cnSummarizeOut(),
          envSpec.locusSummarizeOut()
          ]
    birdsuite.cn_probeset_summarize.main(argv)
    
    print ("FINISH CN SUMMARIZATION") 

def alignGenotypesIntensityData(envSpec):
    print ("intersecting genotypes and CNV intensity data")
    lstLibraries=["broadgap.birdsuitepriors"]
    methodName="align"
    genotypesOut=envSpec.tempDir()+"/" + envSpec.basename()+ ".filteredGenotypes"
    envSpec.setGenotypesFiltered(genotypesOut)
    
    #genotypesFileIn, intensityFileIn, genotypesFileOut, intensityFileOut
    dctArguments={"genotypesFileIn":envSpec.genotypeFile(),
                  "intensityFileIn":envSpec.cnSummarizeOut(),
                  "genotypesFileOut":envSpec.genotypesFiltered(),
                  "intensityFileOut":envSpec.cnSummarizeOut()+".filtered"
                  }
    RscriptToPython.callRscript(lstLibraries, methodName, dctArguments, captureOutput=False, bVerbose=True)
    

def prep_clusters(envSpec):
    print ("START PREPPING CLUSTERS")
    genoF=envSpec.genotypesFiltered()
    intF=envSpec.cnSummarizeOut()+".filtered"
    argv=['prep_clusters', 
          '--intensities', intF,
          '--genotypes', genoF,
          '--output', envSpec.prepClusterOut()
          ]
    
    
    birdsuitepriors.canary.prep_clusters.main(argv)
    
    print ("FINISH PREPPING CLUSTERS")
    
    
def fill_clusters(envSpec):
    lstLibraries=["broadgap.birdsuitepriors"]
    methodName="fillClusters"
    #sourceFile, outputFile, 
    dctArguments={"sourceFile":envSpec.prepClusterOut(),
                  "outputFile":envSpec.outputFile()}
    RscriptToPython.callRscript(lstLibraries, methodName, dctArguments, captureOutput=False, bVerbose=True)
        
def main(argv=None):
    if argv is None:
        argv = sys.argv

    lstSteps=[annotate_allele_summary, locus_summarize, cn_summarize, alignGenotypesIntensityData, prep_clusters, fill_clusters]
    
    strSteps = "\n\t".join([str(i+1) + ": " + step.func_name for i, step in enumerate(lstSteps)])
    
    parser = optparse.OptionParser(usage=__doc__ + "\nSteps are: " + strSteps + "\n")
    
    parser.add_option("-b", "--basename",
                      help="""Used to name all the temp output files.""")
    
    parser.add_option("-o", "--output", dest="outputFile", default=None,
                      help="""Where to write output.  Default: stdout""")
    
    parser.add_option("-i", "--intensity_file", dest="intensityFile", default=None,
                      help="""Intensity summary file, (output using the sumz option of apt-probeset-genotype).  Can be
                      generated by other programs.  The first column name is probeset_id, followed by sample names.  
                      Each row contains the intensity information for an A or B probe for those samples (with a -A or -B 
                      to indicate which allele is being measured.) The A probe is always followed by the B probe for an allele. 
                      File is tab separated.  
                      
                      Example: 
                      
                      probeset_id     NA06985     NA06991
                      SNP_A-2131660-A 1403.81353      1175.07797
                      SNP_A-2131660-B 1507.16102      1160.32130""")
    
    parser.add_option("--genotype_file", dest="genotypeFile", default=None,
                      help="""Hapmap genotype file.  Each row is a CNV, each column an individual.  
                      SNPS should match the SNPs in the intensity file.  There must be a SNP here for each SNP
                      in the intensity file, and the same set of samples. File is tab separated.
                      
                      Example:
                      
                      probeset_id     NA06985 NA06991
                      AFFX-SNP_10000979       1       1""")

    parser.add_option("--probe_locus", dest="probe_locus",
                      help="(Required for step 1)  SNP and CN probe positions.")

    parser.add_option("--force_cn_summarization", dest="force_cn_summarization", default=False, action="store_true",
                      help="""Force summarization of CN probes if they have an A and B allele.
                      Optional for step 2.""")
    
    parser.add_option("-c", "--cnps", dest="cnpDefsFile", 
                      help="""Tab-separated input file with the following columns:
CNP ID, chromosome, start genomic position, end genomic position (inclusive).
Required for step 3.""")
      
    parser.add_option("-m", "--missing_value_label", dest="strMissingValueLabel", default="-9999", 
                      help="""Label of data that is missing from the platform.  
                      Illumina products do not always have data available for every probe/individual combination.
                      Default is %default.  Required for step 3""")
    
    parser.add_option("--tempDir", dest="tempDir", default=None,
                      help="""A temp directory to put intermediate files in.""")
    
    parser.add_option("--first_step", type="int", default=1,
                      help="""What step to start with in birdseed priors generation process.  Default: %default""")
    parser.add_option("--last_step", type="int", default=len(lstSteps),
                      help="""What step to end with in birdseed priors generation process (1-based, inclusive).  Default: %default""")
    
    lstRequiredOptions=['intensityFile', 'genotypeFile', 'probe_locus', 'tempDir', 'basename', 'outputFile', 'cnpDefsFile']
    
    dctOptions, lstArgs = parser.parse_args(argv)
    
    if not utils.validateRequiredOptions(dctOptions, lstRequiredOptions):
        parser.print_help()
        return 1
    
    envSpec=EnvironmentSpec(dctOptions.intensityFile, dctOptions.genotypeFile, 
                            dctOptions.probe_locus, dctOptions.tempDir, 
                            dctOptions.basename, dctOptions.outputFile, 
                            dctOptions.force_cn_summarization, dctOptions.cnpDefsFile, 
                            dctOptions.strMissingValueLabel)
    
    for step in lstSteps[dctOptions.first_step-1:dctOptions.last_step]:
        print ("Running step: " + step.func_name)
        step(envSpec)
        print ("Finished step: " + step.func_name)

if __name__ == "__main__":
    sys.exit(main())