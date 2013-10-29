import csv
with open('input.csv', 'rU') as csvfile:
    r = csv.reader(csvfile)
    header = True
    headerMap = {}
    for row in r:
        print "     ".join(row)

