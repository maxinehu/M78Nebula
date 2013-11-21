'''
Created on Nov 20, 2013

@author: wenjie

Note: Combine all the files under ./data/ into one single file
'''

import os
import re

def combine_files():
    file_list = os.listdir("./data/")
    
    regex = r"[0-9]{6}-[0-9]{5}-2009.op"
    file_pattern = re.compile(regex)
    
    combined_data = file("entire_data_of_the_year", 'a')
    for data_file_name in file_list:
        match = file_pattern.match(data_file_name)
        if match:
            data_file = file("./data/" + data_file_name, 'r')
        
            content = data_file.read()
            data_file.close()
            
            os.remove("./data/" + data_file_name)
            
            combined_data.write(content)
    
    combined_data.close()
    
if __name__ == '__main__':
    combine_files()