min_var = 1e-4
min_mean = 1e-4

import sys

def convert_cluster(x):
    return[float(x[0]),float(x[1]),float(x[2]),float(x[3]),float(x[4]),int(x[5])]

def fixpriors(inputFile, outputFile):

    f = open(inputFile)
    g = open(outputFile, 'w')
    changes_made=0
    
    for line in f:
        groups = line.split(';')
        line_out = groups[0]
        for k in range(1,len(groups)):
            cluster = convert_cluster(groups[k].split())
            if cluster[0] < min_mean:
                cluster[0] = min_mean
                changes_made += 1
            if cluster[1] < min_mean:
                cluster[1] = min_mean
                changes_made += 1
            if cluster[2] < min_var:
                cluster[2] = min_var
                changes_made += 1
            if cluster[4] < min_var:
                cluster[4] = min_var
                changes_made += 1
            cluster = [str(e) for e in cluster]
            line_out += ';' + ' '.join(cluster) 
        g.write(line_out + '\n')
    
    f.close()
    g.close()
    
    changes_made = 0

def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = optparse.OptionParser(usage=__doc__)
    parser.add_option("-o", "--output", dest="output_fname",
                      help="""Where to write output.  Default: stdout""")
    
    parser.add_option("-i", "--input_priors", dest="input_fname",
                      help="""""")
    
    dctOptions, lstArgs = parser.parse_args(argv)
    lstRequiredOptions=['output_fname', 'input_fname']
    
    if not utils.validateRequiredOptions(dctOptions, lstRequiredOptions):
        parser.print_help()
        return 1
        
    fixpriors(dctOptions.input_fname, dctOptions.output_fname)
            
if __name__ == "__main__":
    sys.exit(main())

