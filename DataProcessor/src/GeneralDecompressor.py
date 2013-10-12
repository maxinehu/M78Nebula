'''
Created on Oct 12, 2013

@author: wenjie
'''

import tarfile
import os
import sys

def decompress(year):  
    yearFileName = "gsod_%s.tar" % str(year)
    tar = tarfile.open(yearFileName)
    names = tar.getnames()
    
    for name in names:
        tar.extract(name, path=".")
    tar.close()
    
    os.remove(yearFileName)

if __name__ == '__main__':
    year = int(sys.argv[1])
    
    decompress(year)