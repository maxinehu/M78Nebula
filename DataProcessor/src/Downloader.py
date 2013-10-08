'''
Created on Oct 8, 2013

@author: wenjie
'''

import ftplib
import urllib
import os
import socket
import re
import sys

HOST = "ftp.ncdc.noaa.gov"
USER = "ftp"
PWD = "leonsun817@gmail.com"

PREFIX = "ftp://"

def getHtml(url):
    page = urllib.urlopen(url)
    html = page.read()
    
    return html

def download(year):
    # connect to the ftp server
    try:
        ftpConnection = ftplib.FTP(HOST)
    except (socket.error, socket.gaierror):
        print "ERROR: CANNOT REACH '%s'" % HOST
        return
    print "CONNECTED TO HOST '%s'" % HOST
    
    # log in
    try:
        ftpConnection.login(user = USER, passwd = PWD)
    except ftplib.error_perm:
        print "ERROR: CANNOT LOG IN WITH USER '%s'" % USER
        ftpConnection.quit()
        return
    print "LOGGED IN AS '%s'" % USER
    
    # download all the data file
    try:
        directory = "pub/data/gsod/"
        ftpConnection.cwd(directory)
        
        print "DOWNLOADING THE DATA OF " + str(year)
        
        regex = r"[0-9]{6}-[0-9]{5}-%s.op.gz" % str(year)
        filePattern = re.compile(regex)
        
        url = PREFIX + HOST + '/' + directory + str(year) + '/'
        fileList = re.findall(filePattern, getHtml(url))
        
        ftpConnection.cwd(str(year))
        
        for fileName in fileList:
            ftpConnection.retrbinary("RETR %s" % fileName, open(fileName, 'wb').write)
            
    except ftplib.error_perm:
        print "ERROR: CANNOT READ '%s'" % fileName
        os.unlink(fileName)
        return
    else:
        print "DOWNLOAD COMPLETED"

if __name__ == '__main__':
    year = int(sys.argv[1])
    
    download(year)