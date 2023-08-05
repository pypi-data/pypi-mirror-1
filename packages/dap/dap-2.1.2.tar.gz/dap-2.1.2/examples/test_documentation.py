import glob
import doctest

for file in glob.glob('*.txt'):
    doctest.testfile(file)
