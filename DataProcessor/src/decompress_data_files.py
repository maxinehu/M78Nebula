'''
Created on Oct 8, 2013

@author: wenjie

Use: python decompress_data_files.py [arg], arg == year of the file you want to decompress
Note: 
      File tree:
      gsod_%year.tar (downloaded files)->
        [0-9]{6}-[0-9]{5}-%s.op.gz->
          [0-9]{6}-[0-9]{5}-%s.op (which are the actual data files)
'''

import gzip
import os
import re
import sys
import tarfile

# decompress yearly data files
def decompress_year(year):  
    yearFileName = "gsod_%s.tar" % str(year)
    tar = tarfile.open(yearFileName)
    names = tar.getnames()
    
    for name in names:
        tar.extract(name, path=".")
    tar.close()
    
    os.remove(yearFileName)

# decompress actual data files
def decompress_day(year):
    gzList = os.listdir('.')
    
    regex = r"[0-9]{6}-[0-9]{5}-%s.op.gz" % str(year)
    filePattern = re.compile(regex)
    
    if(os.path.exists("./data/") == False):
        os.mkdir("./data/")
    
    print "DECOMPRESSING DATA OF '%s'" % str(year)
    for gzName in gzList:
        match = filePattern.match(gzName)
        if match:
            tmp = gzip.GzipFile(gzName)
            content = tmp.read()
            tmp.close()
            
            os.remove(gzName)
            
            decompressedFile = file("data/" + gzName[0:-3], 'w')
            decompressedFile.write(content)
            decompressedFile.close()
            
    print "DECOMPRESS COMPLETED\n"

if __name__ == '__main__':
    year = int(sys.argv[1])
    
    #decompress_year(year)
    decompress_day(year)