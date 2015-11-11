psychopy-utils
==============

Utility programs to help create PsychoPy experiments 

v2: updated to new output file format that does not require multiple files to be loaded into PyschoPy

how to run it:

    cd self-paced
    python self-paced-v2.py

or if you know the number of regions and the input file name:

    cd self-paced
    python self-paced-v2.py -i input-v2.csv -n 11

if you have an excel file:

    cd self-paced
    python self-paced-v3.py -i input-v3.xlsx -n 12

(you might have to manually change the font for UTF-8 in the Excel output file. Just select those columns and change to the desired font.)

if you want character counts for each region:

    cd self-paced
    python self-paced-v3.py -i input-v3-eng.xlsx -n 11 -c

