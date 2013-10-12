#!/bin/sh

# It will cause maximum ftp connection exceeds error
# if download files inside python code.
# So I use this script to execute downloader repeatedly.

# Need to change year to correct number: 1929 to 2014
for((year = 1929; year < 2014; year++)) {
    python Downloader.py "$year"
	python GeneralDecompressor.py "$year"
    python Decompressor.py "$year"
}