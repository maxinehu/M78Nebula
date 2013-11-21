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
    year_file_name = "gsod_%s.tar" % str(year)
    tar = tarfile.open(year_file_name)
    names = tar.getnames()
    
    for name in names:
        tar.extract(name, path=".")
    tar.close()
    
    os.remove(year_file_name)

# decompress actual data files
def decompress_day(year):
    gz_list = os.listdir('.')
    
    regex = r"[0-9]{6}-[0-9]{5}-%s.op.gz" % str(year)
    file_pattern = re.compile(regex)
    
    if(os.path.exists("./data/") == False):
        os.mkdir("./data/")
    
    print "DECOMPRESSING DATA OF '%s'" % str(year)
    for gz_name in gz_list:
        match = file_pattern.match(gz_name)
        if match:
            tmp = gzip.GzipFile(gz_name)
            content = tmp.read()
            tmp.close()
            
            os.remove(gz_name)
            
            decompressed_file = file("data/" + gz_name[0:-3], 'w')
            decompressed_file.write(content)
            decompressed_file.close()
            
    print "DECOMPRESS COMPLETED\n"

if __name__ == '__main__':
    year = int(sys.argv[1])
    
    decompress_year(year)
    decompress_day(year)