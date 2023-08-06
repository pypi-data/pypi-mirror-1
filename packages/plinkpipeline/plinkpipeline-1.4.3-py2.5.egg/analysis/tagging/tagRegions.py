'''
Created on Jun 19, 2009

@author: nemesh
'''

from mpgutils.RUtils import RscriptToPython

import sys
import optparse
from mpgutils import utils
from mpgutils.RUtils import RscriptToPython


def main(argv=None):
    if argv is None:
        argv = sys.argv
   
    parser = optparse.OptionParser(usage=__doc__)
    
    parser.add_option("--cnvMapFile", dest="cnvMapFile",
                      help="""map file for CNVs.  4 columns:
                      id, chromosome, start, end""")
    
    parser.add_option("--cnvGenotypeFile", dest="cnvGenotypeFile",
                      help="""A matrix of genotypes.  Each row is a CNV label, each column a sample. Genotypes are numeric copy number calls.""")
    
    parser.add_option("--snpMapFile", dest="snpMapFile",
                      help="""map file for SNPs.  4 columns:
                      id, chromosome, start, end""")
    
    parser.add_option("--snpGenotypeFile", dest="snpGenotypeFile",
                      help="""A matrix of genotypes.  Each row is a SNP label, each column a sample. Genotypes are numeric calls.  If using SNP data, can be produced from hapmap data  via hapmapFormatToGenotypes.R""")
    
    parser.add_option("--outFile", dest="outFile", 
                      help="""Where to put output results.""")

    parser.add_option("--window", dest="window", default=20000,
                      help="""How far to search into the test data set on each side of the regions to be tagged. For example, if tagging CNVs with SNP data, look at SNPs on 20000 bp window to each side of the CNV.""")

    parser.add_option("--excludeOverlaps", dest="excludeOverlaps", action="store_true", default=False,
                      help="""Should regions in the two data sets that overlap be analyzed?  If this is set to true, regions that are overlapping will not be in the final output.""")

    parser.add_option("--partitionSize", dest="partitionSize", default=1000000,
                      help="""Controls how much data is loaded for each round of testing.  This partitions both the items being tagged and the items they are tagged by.  Setting this appropriately can speed up search time, as each item to be tagged needs to find all it's possible tagging elements within the search space.""")

    parser.add_option("--method", dest="method", default="snp_cnv",
                      help="""The tagging method to use.  Defines which data sets will be required, and how they will be used. 
                      snp_cnv: tag each CNV region with SNP genotype data.  Finds SNPs to either side of the CNV (controlled by window parameter) and attempts to tag the CNV via pairwise correlation.""")
    
    parser.add_option("--testString", dest="strTestStrings",
                      help="""Add test string here.  'rsq,cor' """)
    
    parser.add_option("--filterString", dest="strFilterStrings",
                      help="""Add filter string here. 'rsq:gte:0.8'""")
    
    dctOptions, lstArgs = parser.parse_args(argv)
    
    lstLibraries=["broadgap.hapmaptools"]
    
    method=dctOptions.method
    if method=="snp_cnv":
        lstRequiredOptions=["cnvMapFile", "cnvGenotypeFile", "snpMapFile", "snpGenotypeFile", "outFile", "strTestStrings"]
    
        if not utils.validateRequiredOptions(dctOptions, lstRequiredOptions):
            parser.print_help()
            return 1
        methodName="tagCNVBySNPs"
       
        dctArguments={"cnvMapFile":dctOptions.cnvMapFile,
                      "cnvGenotypeFile":dctOptions.cnvGenotypeFile,
                      "snpMapFile":dctOptions.snpMapFile,
                      "snpGenotypeFile":dctOptions.snpGenotypeFile, 
                      "outFile":dctOptions.outFile,
                      "window":dctOptions.window,
                      "partitionSize":dctOptions.partitionSize,
                      "excludeOverlap":dctOptions.excludeOverlaps,
                      "listTestStrings":dctOptions.strTestStrings,
                      "filterString":dctOptions.strFilterStrings
                      }
        
        RscriptToPython.callRscript(lstLibraries, methodName, dctArguments, True)

if __name__ == "__main__":
    sys.exit(main())
    
