'''
Created on Oct 13, 2013

@author: wenjie
'''

import os
import re

PATH = "data/"

# All rows are string, need to specify the first index
STN_START = 0
STN_LENGTH = 6
WBAN_START = 7
WBAN_LENGTH = 5
DATE_START = 14
DATE_LENGTH = 8
TEMP_START = 26
TEMP_LENGTH = 4
# As of now, only consider temperature

# 
def load(year):
    fileList = os.listdir(PATH)
    
    regex = r"[0-9]{6}-[0-9]{5}-%s.op" % str(year)
    filePattern = re.compile(regex)
    
    # should only one file in file list, need to modify
    for fileName in fileList:
        match = filePattern.match(fileName)
        if match:
            firstLine = True
            
            features = []
            results = []
            
            count = 0
            for line in open(PATH + fileName):
                # skip first line
                if firstLine: 
                    firstLine = False
                    continue
                
                # how many is appropriate?
                if count >= 30:
                    break
                
                # extract data, they are stored as string for each row
                row = line.strip().split('\t')
                feature = []
                #
                #feature.append(int(row[0][DATE_START: DATE_START + DATE_LENGTH]))                
                feature.append(count)
                features.append(feature)
                #
                results.append(float(row[0][TEMP_START: TEMP_START + TEMP_LENGTH]))
                
                count += 1

            return features, results

def train(features, results):
    from sklearn.svm import SVR
    
    svr_rbf = SVR(kernel='rbf', C=1e3, gamma=0.1)
    svr_lin = SVR(kernel='linear', C=1e3)
    svr_poly = SVR(kernel='poly', C=1e3, degree=2)
    y_rbf = svr_rbf.fit(features, results).predict(features)
    y_lin = svr_lin.fit(features, results).predict(features)
    y_poly = svr_poly.fit(features, results).predict(features)
    
    import pylab as pl
    pl.scatter(features, results, c='k', label='data')
    pl.hold('on')
    pl.plot(features, y_rbf, c='g', label='RBF model')
    pl.plot(features, y_lin, c='r', label='Linear model')
    pl.plot(features, y_poly, c='b', label='Polynomial model')
    pl.xlabel('data')
    pl.ylabel('target')
    pl.title('Support Vector Regression')
    pl.legend()
    pl.show()

if __name__ == '__main__':
    (features, results) = load("2000")
    train(features, results)