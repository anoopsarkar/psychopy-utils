import csv
import re
import sys

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
        # outputFileHeader contains the prefix for the output filename with a .csv suffix
        self.outputFileHeader = 'Id'
        self.headerMap = {}
        # lastIndex is the number of columns in the input (currently unused)
        self.lastIndex = -1
        # headerTransform contains the mapping from input to output
        # if the value is None, the column is removed (typically these values from input are used elsewhere)
        # if the value contains a tuple, the first element is a function that takes the entire input row
        # as input and produces possibly several rows of output with multiple columns returned as a list
        # of rows; the second element of the tuple refers to the output column headers to be created
        self.headerTransform = {
            'Sentence': (self.selfPacedSentences, ['Region','Sentence','CorrectAns','NofCharacters']),
            'CompQInstruction': None,
            'CompQuestion': None,
            'CorrectAns': None,
        }

    def convertSentence(self, sentence, compQInstructionValue, compQuestionValue, correctAnsValue):
        correctAns = 'space'
        regionList = sentence.split(' - ')
        hiddenList = map(lambda x: re.sub(r'[^ ]', '_', x), regionList)
        outputList = [ ['R0', " ".join(hiddenList), correctAns, str(0)] ]
        lastIndex = -1
        for (index, region) in enumerate(regionList, start=1):
            outputList.append([ 
                'R' + str(index),
                " ".join(hiddenList[0:index-1] + [regionList[index-1]] + hiddenList[index:]), 
                correctAns,
                str(len(regionList[index-1]))
                ])
            lastIndex = index
        outputList.append([ 
            'R' + str(lastIndex+1),
            compQInstructionValue,
            correctAns,
            str(len(compQInstructionValue))
            ])
        outputList.append([ 
            'R' + str(lastIndex+2),
            compQuestionValue,
            correctAnsValue,
            str(len(compQuestionValue))
            ])
        return outputList

    def selfPacedSentences(self, row):
        commonValues = []
        for (index,value) in enumerate(row):
            if index not in self.headerMap:
                raise ValueError
            header = self.headerMap[index]
            if header == 'Sentence':
                sentenceValue = value
            elif header == 'CompQInstruction':
                compQInstructionValue = value
            elif header == 'CompQuestion':
                compQuestionValue = value
            elif header == 'CorrectAns':
                correctAnsValue = value
            else:
                commonValues.append(value)
        outputRows = []
        for sentenceOutput in self.convertSentence(sentenceValue, compQInstructionValue, compQuestionValue, correctAnsValue): 
            output = []
            output.extend(commonValues)
            output.extend(sentenceOutput)
            outputRows.append(output)
        return outputRows

    def create(self, inputfilename):
        headerRow = True
        outputHeader = []
        with open(inputfilename, 'rU') as csvfile:
            inputf = csv.reader(csvfile)
            for row in inputf:
                if headerRow:
                    outputRow = []
                    for (index,header) in enumerate(row):
                        self.headerMap[index] = header
                        self.lastIndex = index
                        if header in self.headerTransform:
                            if self.headerTransform[header] is not None:
                                (func, outputList) = self.headerTransform[header]
                                outputHeader.extend(outputList)
                        else:
                            outputHeader.append(header)
                    headerRow = False
                else:
                    func = None
                    outputfilename = None
                    for (index,value) in enumerate(row):
                        header = self.headerMap[index]
                        if header in self.headerTransform:
                            if self.headerTransform[header] is not None:
                                (func, outputList) = self.headerTransform[header]
                        if header == self.outputFileHeader:
                            outputfilename = value
                    if func is None or outputfilename is None:
                        raise ValueError
                    outputfilename += ".csv"
                    with open(outputfilename, 'wb') as outputfile:
                        outputf = csv.writer(outputfile)
                        outputf.writerow(outputHeader)
                        for outputRow in func(row):
                            outputf.writerow(outputRow)
                    print >>sys.stderr, outputfilename

if __name__ == '__main__':
    if len(sys.argv) == 2:
        s = SelfPaced()
        #print s.convertSentence('A man who - the fact - that the manager - hired him - last year - was amazing - became a reporter.', '', '', '')
        s.create(sys.argv[1])
    else:
        print >>sys.stderr, "usage: %s file.csv" % (sys.argv[0])
