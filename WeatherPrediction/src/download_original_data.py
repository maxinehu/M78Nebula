'''
Created on Oct 8, 2013

@author: wenjie

Use: python download_original_data.py [arg], arg == year of the file you want to decompress

Note: Download the original data from ftp.ncdc.noaa.gov
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

def get_html(url):
    page = urllib.urlopen(url)
    html = page.read()
    
    return html

def download(year):
    # connect to the ftp server
    try:
        ftp_connection = ftplib.FTP(HOST)
    except (socket.error, socket.gaierror):
        print "ERROR: CANNOT REACH '%s'" % HOST
        return
    print "CONNECTED TO HOST '%s'" % HOST
    
    # log in
    try:
        ftp_connection.login(user = USER, passwd = PWD)
    except ftplib.error_perm:
        print "ERROR: CANNOT LOG IN WITH USER '%s'" % USER
        ftp_connection.quit()
        return
    print "LOGGED IN AS '%s'" % USER
    
    # download all the data file
    try:
        directory = "pub/data/gsod/"
        ftp_connection.cwd(directory)
        
        print "DOWNLOADING THE DATA OF " + str(year)
        
        # download all the data files
        regex = r"gsod_%s.tar" % str(year)
        # download only the data from Gainesville, FL
        # regex = r"722146-12816-%s.op.gz|747560-12816-%s.op.gz" % (str(year), str(year))
        # download only the data from Seattle, WA
        # regex = r"727930-24233-%s.op.gz" % str(year)
        # download only the data from New York City, NY
        # regex = r"725030-14732-%s.op.gz" % str(year)
        # download only the data from Washington, D.C.
        # regex = r"724050-13743-%s.op.gz" % str(year)
        # download only the data from Orlando, FL
        # regex = r"722050-12815-%s.op.gz" % str(year)
        
        file_pattern = re.compile(regex)
        
        url = PREFIX + HOST + '/' + directory + str(year) + '/'
        file_list = re.findall(file_pattern, get_html(url))

        ftp_connection.cwd(str(year))
        
        # in fact, only one file if regex = r"gsod_%s.tar" % str(year)
        for file_name in file_list:
            ftp_connection.retrbinary("RETR %s" % file_name, open(file_name, 'wb').write)
            
    except ftplib.error_perm:
        print "ERROR: CANNOT READ '%s'" % file_name
        os.unlink(file_name)
        return
    else:
        print "DOWNLOAD COMPLETED\n"

if __name__ == '__main__':
    year = int(sys.argv[1])
    
    download(year)