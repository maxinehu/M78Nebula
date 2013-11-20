'''
Created on Nov 19, 2013

@author: wenjie

Use: python knn_local_predict.py

Note: Only use temperature as feature, e.g., [t11,t12,t13,...], [t21,t22,t23...]...
      Look for the 10(arbitrary value) nearest neighbors and use 7 days after to predict.
      Simply use the mean of these 7-day time sequences.
'''

import os
import re

PATH = "data/"

# All rows are string, need to specify the first/last index
STN_START = 0           # Station number
STN_END = 5
WBAN_START = 7          # historical "Weather Bureau Air Force Navy" number
WBAN_END = 11
YEAR_START = 14         # The year
YEAR_END = 17
MODA_START = 18         # The month and day
MODA_END = 21
TEMP_START = 24         # Mean temperature for the day
TEMP_END = 29

def load_weather(year):
    file_list = os.listdir(PATH)
    
    regex = r"[0-9]{6}-[0-9]{5}-%s.op" % str(year)
    file_pattern = re.compile(regex)
    
    # should only one file in file list
    for file_name in file_list:
        match = file_pattern.match(file_name)
        if match:
            first_line = True
            
            real_data = {}
            real_data["TEMP"] = []
            for line in open(PATH + file_name):
                # skip first line
                if first_line: 
                    first_line = False
                    continue
                
                # extract data, they are stored as string for each row
                row = line.strip().split('\t')
                # read only January, and first week of February as of now
                cur_moda = int(row[0][MODA_START: MODA_END + 1])
                if cur_moda < 208:
                    # I forgot why I needed a zero here...if not, an error occurs
                    temp = float(row[0][TEMP_START: TEMP_END + 1])
                    if temp == 9999.9:
                        temp = 50.0
                    real_data["TEMP"].append(temp)
                else:
                    break        

            # first 31 elements are used to train, last 7 elements used to test
            return real_data

def knn_predict(real_data, num_neighbors):
    from sklearn.neighbors import NearestNeighbors
    import numpy as np
    
    samples = []
    for i in range(1979, 2009):
        samples.append(real_data[i][:31])

    X = np.array(samples)
    nbrs = NearestNeighbors(n_neighbors=num_neighbors, algorithm='ball_tree').fit(X)
    distances, indices = nbrs.kneighbors(real_data[2009][:31])
    
    return distances, indices

def draw_result(predicted_temps, real_temps):
    import pylab as pl
    
    history = range(1, 39)
    future = range(32, 39)
    
    pl.plot(history, real_temps, c='k', label="Real Temperature")
    pl.hold('on')
    pl.plot(future, predicted_temps, c='g', label="Predicted Temperature")
    pl.xlabel("date")
    pl.ylabel("TEMP")
    pl.title('K Nearest Neighbors on TEMP')
    pl.legend()
    pl.show()

if __name__ == '__main__':
    real_data = {}
    for i in range(1979, 2010):
        temp_dict = load_weather(str(i))
        real_data[i] = temp_dict["TEMP"]
    distances, indices = knn_predict(real_data, 10)
    
    nearest_neighbors = []
    for i in indices[0]:
        nearest_neighbors.append(real_data[1979 + i])
    
    predicted_temps = []
    for i in range(7):
        temp = 0
        for n in nearest_neighbors:
            temp += n[i]
        predicted_temps.append(temp/10)
    
    draw_result(predicted_temps, real_data[2009])
    #print predicted_temps
    #print real_data[2009][31:]