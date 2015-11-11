import csv, openpyxl, re, sys, optparse

class SelfPaced:
    """
    To cleanup the output csv files on bash:
    python self-paced.py input.csv 2> cleanup
    cat cleanup | sed -e 's/^/rm /' | sh

    To cleanup the output csv files on tcsh:
    python self-paced.py input.csv >& cleanup
    cat cleanup | sed -e 's/^/rm /' | sh
    """
    def __init__(self):
        # outputFileName contains the default output filename for stdin. 
        # If a filename.csv is given in sys.argv then the output filename will be filename-regions.csv
        # This is commented out because stdin is not used anymore: 
        # self.outputFileName = 'default-regions' 

        # default number of regions, at least one to pass through the sentence without any split
        self.numRegions = 0
        # set charcounts to True to enable additional columns containing the character count for each region
        self.charcounts = False
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
        self.headerMap = {}
        # different input files get their own reader and writer functions
        self.fileTypes = {
            'csv': (self.readCSV, self.writeCSV),
            'xlsx': (self.readExcel, self.writeExcel),
        }

    def getRegionsHeader(self, numregions):
        outputList = []
        for index in xrange(numregions):
            outputList.append('R' + str(index))
            if self.charcounts:
                outputList.append('R' + str(index) + 'CharCount')
        return outputList

    def convertSentence(self, sentence, numregions):
        regionList = sentence.split(' - ')
        hiddenList = map(lambda x: re.sub(r'[^ ]', '_', x), regionList)
        outputList = [ " ".join(hiddenList) ]
        if self.charcounts:
            outputList.append( 0 )
        for (index, region) in enumerate(regionList, start=1):
            outputList.append( 
                " ".join(hiddenList[0:index-1] + [regionList[index-1]] + hiddenList[index:])
                )
            if self.charcounts:
                outputList.append( len(regionList[index-1]) )
                # print >>sys.stderr, regionList[index-1], len(regionList[index-1])
        if self.charcounts:
            if len(outputList) > numregions*2:
                raise ValueError("invalid number of regions: outputList len is %d and numregions is %d" % (len(outputList), numregions))
        else:
            if len(outputList) > numregions:
                raise ValueError("invalid number of regions: outputList len is %d and numregions is %d" % (len(outputList), numregions))
        outputList += [''] * (numregions - len(outputList))
        return outputList

    def readCSV(self, inputfilename):
        data = []
        with open(inputfilename, 'rU') as csvfile:
            inputf = csv.reader(csvfile)
            for row in inputf:
                data.append(row)
        return data

    def writeCSV(self, outputHeader, outputRows, outputFileName):
        with open(outputFileName, 'wb') as outputfile:
            outputf = csv.writer(outputfile, quoting=csv.QUOTE_NONNUMERIC)
            outputf.writerow(outputHeader)
            for outputRow in outputRows:
                outputf.writerow(outputRow)

    def readExcel(self, inputfilename):
        data = []
        wb = openpyxl.load_workbook(inputfilename)
        for ws in wb:
            for wr in ws.rows:
                row = []
                for cell in wr:
                    row.append(cell.value)
                data.append(row)
        return data

    def writeExcel(self, outputHeader, outputRows, outputFileName):
        wb = openpyxl.Workbook()
        ws = wb.active
        for j, headerValue in enumerate(outputHeader):
            ws.cell(row = 0, column = j).value = headerValue
        for i, row in enumerate(outputRows, start=1):
            for j, value in enumerate(row):
                ws.cell(row = i, column = j).value = value
        wb.save(outputFileName)

    def create(self, inputfilename, numregions, charcounts):
        # produce output filename, e.g. input.csv will become input-regions.csv
        # if there is more than one extension e.g. input.x.y then output will be input-regions.x.y
        self.charcounts = charcounts
        fileNameSuffix = re.sub(r'[^.]*\.(.*)$', r'\1', inputfilename)
        outputFileName = re.sub(r'([^.]*)\.(.*)$', r'\1-regions.\2', inputfilename)
        headerRow = True
        outputHeader = []
        outputRows = []
        data = []

        print >>sys.stderr, "file name suffix:", fileNameSuffix
        if fileNameSuffix in self.fileTypes:
            (readfunc, _) = self.fileTypes[fileNameSuffix]
            data = readfunc(inputfilename)
        else:
            raise ValueError("unknown file name type: %s" % (inputfilename))

        for row in data:
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
                            # if the value of headerTransform for header is None then the column is dropped
                    else:
                        outputRow.append(value)
                #print >>sys.stderr, outputRow
                #print >>sys.stderr, outputRows
                #print >>sys.stderr, "\n\n"
                outputRows.append(outputRow)

        if fileNameSuffix in self.fileTypes:
            (_, writefunc) = self.fileTypes[fileNameSuffix]
            writefunc(outputHeader, outputRows, outputFileName)
            print >>sys.stderr, outputFileName
        else:
            raise ValueError("unknown file name type: %s" % (inputfilename))

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
        optparser.add_option("-c", "--charcounts", dest="charcounts", action="store_true", default=False, help="add character counts of each region to output")
        (opts, _) = optparser.parse_args()
        s = SelfPaced()
        if int(opts.numregions) <= 0:
            optparser.print_help()
            sys.exit(1)
        s.create(opts.inputfile, int(opts.numregions), opts.charcounts)

