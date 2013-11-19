#!/bin/sh

# It will cause maximum ftp connection exceeds error
# if download files inside python code.
# So I use this script to execute downloader repeatedly.

# Need to change year to correct number: 1929 to 2014
# Data from Gaineville starts from 1943 to 2013
for((year = 1929; year < 2014; year++)) {
    python download_original_data.py "$year"
    
   	python decompress_data_files.py "$year"
}
