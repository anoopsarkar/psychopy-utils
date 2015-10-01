import csv, re, sys, optparse

class SelfPaced:
    """
    To cleanup the output files on bash:
    python self-paced.py input.csv 2> cleanup
    cat cleanup | sed -e 's/^/rm /' | sh

    To cleanup the output files on tcsh:
    python self-paced.py input.csv >& cleanup
    cat cleanup | sed -e 's/^/rm /' | sh
    """
    def __init__(self):
        # outputFileName contains the default output filename for stdin. 
        # If a filename.csv is given in sys.argv then the output filename will be filename-regions.csv
        self.outputFileName = 'default-regions' 
        # default number of regions, at least one to pass through the sentence without any split
        self.numRegions = 0
        self.headerMap = {}
        # headerTransform contains the mapping from input to output
        # if the value is None, the column is removed (typically these values from input are used elsewhere)
        # if the value contains a tuple, the first element is a function that takes the entire input row
        # as input and produces possibly several rows of output with multiple columns returned as a list
        # of rows; the second element of the tuple refers to the output column headers to be created
        self.headerTransform = {
            'Sentence': (self.getRegionsHeader, self.convertSentence),
            # Put any columns below that will be removed and transformed by direct access into headerMap
            # 'CompQInstruction': None,
            # 'CompQuestion': None,
            # 'CorrectAns': None,
        }

    def getRegionsHeader(self, numregions):
        outputList = []
        for index in xrange(numregions):
            outputList.append('R' + str(index))
        return outputList

    def convertSentence(self, sentence, numregions):
        regionList = sentence.split(' - ')
        hiddenList = map(lambda x: re.sub(r'[^ ]', '_', x), regionList)
        outputList = [ " ".join(hiddenList) ]
        for (index, region) in enumerate(regionList, start=1):
            outputList.append( 
                " ".join(hiddenList[0:index-1] + [regionList[index-1]] + hiddenList[index:])
                )
        if len(outputList) > numregions:
            raise ValueError("invalid number of regions: outputList len is %d and numregions is %d" % (len(outputList), numregions))
        outputList += [''] * (numregions - len(outputList))
        return outputList

    def create(self, inputfilename, numregions):
        # produce output filename, e.g. input.csv will become input-regions.csv
        # if there is more than one extension e.g. input.x.y then output will be input-regions.x.y
        self.fileNameSuffix = re.sub(r'[^.]*\.(.*)$', r'\1', inputfilename)
        self.outputFileName = re.sub(r'([^.]*)\.(.*)$', r'\1-regions.\2', inputfilename)
        headerRow = True
        outputHeader = []
        outputRows = []
        with open(inputfilename, 'rU') as csvfile:
            inputf = csv.reader(csvfile)
            for row in inputf:
                if headerRow:
                    outputHeader = []
                    for (index, header) in enumerate(row):
                        self.headerMap[index] = header
                        if header in self.headerTransform:
                            if self.headerTransform[header] is not None:
                                (headerfunc, _) = self.headerTransform[header]
                                outputHeader.extend(headerfunc(numregions))
                            else:
                                pass
                                # if the value of headerTranform for header is None then the column is dropped
                        else:
                            outputHeader.append(header)
                    headerRow = False
                else:
                    outputRow = []
                    for (index, value) in enumerate(row):
                        header = self.headerMap[index]
                        if header in self.headerTransform:
                            if self.headerTransform[header] is not None:
                                (_, convertfunc) = self.headerTransform[header]
                                outputRow.extend(convertfunc(value, numregions))
                            else:
                                pass
                                # if the value of headerTranform for header is None then the column is dropped
                        else:
                            outputRow.append(value)
                    #print >>sys.stderr, outputRow
                    #print >>sys.stderr, outputRows
                    #print >>sys.stderr, "\n\n"
                    outputRows.append(outputRow)
        with open(self.outputFileName, 'wb') as outputfile:
            outputf = csv.writer(outputfile, quoting=csv.QUOTE_NONNUMERIC)
            outputf.writerow(outputHeader)
            for outputRow in outputRows:
                outputf.writerow(outputRow)
        print >>sys.stderr, self.outputFileName

if __name__ == '__main__':
    if False:
        s = SelfPaced()
        print s.getRegionsHeader(6)
        print s.convertSentence('A man who - the fact - that the manager - hired him - last year - was amazing - became a reporter.')
        sys.exit(0)
    else:
        optparser = optparse.OptionParser()
        optparser.add_option("-n", "--numregions", dest="numregions", default=0, help="number of regions in each sentence (default=0)")
        optparser.add_option("-i", "--inputfile", dest="inputfile", default='input-v2.csv', help="input filename (default=input-v2.csv)")
        (opts, _) = optparser.parse_args()
        s = SelfPaced()
        if int(opts.numregions) <= 0:
            optparser.print_help()
            sys.exit(1)
        s.create(opts.inputfile, int(opts.numregions))
