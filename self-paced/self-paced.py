import csv
import re

class SelfPaced:
    def __init__(self):
        self.headerMap = {}
        self.lastIndex = -1
        self.headerTransform = {
            'Sentence': (self.selfPacedSentences, ['Region','Sentence','CorrectAns','NofCharacters']),
            'CompQInstruction': None,
            'CompQuestion': None,
            'CorrectAns': None,
        }

    def convertSentence(self, sentence):
        correctAns = 'space'
        regionList = sentence.split(' - ')
        hiddenList = map(lambda x: re.sub(r'[^ ]', '_', x), regionList)
        outputList = [ ['R0', " ".join(hiddenList), correctAns, str(0)] ]
        for (index, region) in enumerate(regionList, start=1):
            outputList.append([ 
                'R' + str(index),
                " ".join([ "".join( hiddenList[0:index-1] ) , regionList[index-1] , "".join(hiddenList[index:] if index < len(regionList) else []) ]),
                str(len(regionList[index-1]))
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
        for sentenceOutput in self.convertSentence(sentenceValue):
            output = []
            output.extend(commonValues)
            output.extend(sentenceOutput)
            outputRows.append(output)
        return outputRows

    def create(self, inputfilename, outputfilename):
        headerRow = True
        with open(inputfilename, 'rU') as csvfile:
            with open(outputfilename, 'wb') as outputfile:
                inputf = csv.reader(csvfile)
                outputf = csv.writer(outputfile)
                for row in inputf:
                    if headerRow:
                        outputRow = []
                        for (index,header) in enumerate(row):
                            self.headerMap[index] = header
                            self.lastIndex = index
                            if header in self.headerTransform:
                                if self.headerTransform[header] is not None:
                                    (func, outputList) = self.headerTransform[header]
                                    outputRow.extend(outputList)
                            else:
                                outputRow.append(header)
                        headerRow = False
                        outputf.writerow(outputRow)
                        print outputRow, self.headerMap, self.lastIndex
                    else:
                        func = None
                        for (index,value) in enumerate(row):
                            header = self.headerMap[index]
                            if header in self.headerTransform:
                                if self.headerTransform[header] is not None:
                                    (func, outputList) = self.headerTransform[header]
                        for outputRow in func(row):
                            outputf.writerow(outputRow)
                            print "     ".join(outputRow)

if __name__ == '__main__':
    s = SelfPaced()
    #print s.convertSentence('A man who - the fact - that the manager - hired him - last year - was amazing - became a reporter.')
    s.create('input.csv', 'output.csv')
