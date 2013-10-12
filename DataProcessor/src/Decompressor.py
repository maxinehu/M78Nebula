'''
Created on Oct 8, 2013

@author: wenjie
'''

import gzip
import tarfile
import os
import re
import sys

def decompress(year):
    gzList = os.listdir('.')
    
    regex = r"[0-9]{6}-[0-9]{5}-%s.op.gz" % str(year)
    filePattern = re.compile(regex)
    
    print "DECOMPRESSING DATA OF '%s'" % str(year)
    for gzName in gzList:
        match = filePattern.match(gzName)
        if match:
            tmp = gzip.GzipFile(gzName)
            content = tmp.read()
            tmp.close()
            
            os.remove(gzName)
            
            decompressedFile = file(gzName[0:-3], 'w')
            decompressedFile.write(content)
            decompressedFile.close()
            
    print "DECOMPRESS COMPLETED"

if __name__ == '__main__':
    year = int(sys.argv[1])
    
    decompress(year)