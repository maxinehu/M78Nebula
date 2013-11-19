'''
Created on Oct 13, 2013

@author: wenjie

Use: python svr_local_predict.py

Note: As of now, we only use weather data in January 2013 to "predict"
      the first week in February.
      
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
DEWP_START = 35         # Mean dew point for the day ***
DEWP_END = 40
SLP_START = 46          # Mean sea level pressure for the day ***
SLP_END = 51
STP_START = 57          # Mean station pressure for the day ***
STP_END = 62
VISIB_START = 68        # Mean visibility for the day in miles 
VISIB_END = 72
WDSP_START = 78         # Mean wind speed for the day ***
WDSP_END = 82
MXSPD_START = 88        # Maximum sustained wind speed reported for the day ***
MXSPD_END = 92
GUST_START = 95         # Maximum wind gust reported for the day ***
GUST_END = 99
MAX_START = 102         # Maximum temperature reported during the day
MAX_END = 107
MIN_START = 110         # Minimum temperature reported during the day
MIN_END = 115
PRCP_START = 118        # Total precipitation (rain and/or melted snow) reported during the day ***
PRCP_END = 122
SNDP_START = 125        # Snow depth in inches ***
SNDP_END = 129

# load the weather data for a specific year
# including TEMP, DEWP, SLP, STP, WDSP, MXSPD, GUST, PRCP, SNDP
def load_weather(year):
    fileList = os.listdir(PATH)
    
    regex = r"[0-9]{6}-[0-9]{5}-%s.op" % str(year)
    filePattern = re.compile(regex)
    
    # should only one file in file list
    for fileName in fileList:
        match = filePattern.match(fileName)
        if match:
            firstLine = True
            
            features = {}
            features["TEMP"] = []
            features["DEWP"] = []
            features["SLP"] = []
            features["STP"] = []
            features["MXSPD"] = []
            features["GUST"] = []
            features["PRCP"] = []
            features["SNDP"] = []
            features["WDSP"] = []
            
            for line in open(PATH + fileName):
                # skip first line
                if firstLine: 
                    firstLine = False
                    continue
                # extract data, they are stored as string for each row
                row = line.strip().split('\t')
                # skip January to November
                curModa = int(row[0][MODA_START: MODA_END + 1])
                if(curModa == 201):
                    break
                
                # I forgot why I needed a zero here...if not, an error occurs
                temp = float(row[0][TEMP_START: TEMP_END + 1])
                if temp == 9999.9:
                    temp = 50.0
                features["TEMP"].append(temp)
                
                dewp = float(row[0][DEWP_START: DEWP_END + 1])
                if dewp == 9999.9:
                    dewp = 50.0
                features["DEWP"].append(dewp)
                
                slp = float(row[0][SLP_START: SLP_END + 1])
                if slp == 9999.9:
                    slp = 1010.0
                features["SLP"].append(slp)
                
                stp = float(row[0][STP_START: STP_END + 1])
                if stp == 9999.9:
                    stp = 1010.0
                features["STP"].append(stp)
                
                mxspd = float(row[0][MXSPD_START: MXSPD_END + 1])
                if mxspd == 999.9:
                    mxspd = 10.0
                features["MXSPD"].append(mxspd)
                
                gust = float(row[0][GUST_START: GUST_END + 1])
                if gust == 999.9:
                    gust = 22.0
                features["GUST"].append(gust)
                
                prcp = float(row[0][PRCP_START: PRCP_END + 1])
                if prcp == 99.99:
                    prcp = 0.0
                features["PRCP"].append(prcp)
                
                sndp = float(row[0][SNDP_START: SNDP_END + 1])
                if sndp == 999.9:
                    sndp = 0.0
                features["SNDP"].append(sndp)
                
                wdsp = float(row[0][WDSP_START: WDSP_END + 1])
                if wdsp == 999.9:
                    wdsp = 5.0
                features["WDSP"].append(wdsp)     

            return features

def train_single(feature, name):
    from sklearn.svm import SVR
    
    svr_rbf = SVR(kernel='rbf', C=1e3, gamma=0.1)
    svr_lin = SVR(kernel='linear', C=1e3)
    svr_poly = SVR(kernel='poly', C=1e3, degree=2)
    
    # 31 days history
    history = []
    for i in range(1, 32):
        h = [i]
        history.append(h)
    # predict 7 days ahead
    future = []
    for i in range(32, 39):
        f = [i]
        future.append(f)
    
    predicted_feature = svr_rbf.fit(history, feature).predict(future)
    
    return predicted_feature
    
    '''
    y_rbf = svr_rbf.fit(X, feature).predict(X)
    y_lin = svr_lin.fit(X, feature).predict(X)
    y_poly = svr_poly.fit(X, feature).predict(X)
    
    
    import pylab as pl
    pl.scatter(X, feature, c='k', label=name)
    pl.hold('on')
    pl.plot(X, y_rbf, c='g', label='RBF model')
    pl.plot(X, y_lin, c='r', label='Linear model')
    pl.plot(X, y_poly, c='b', label='Polynomial model')
    pl.xlabel('date')
    pl.ylabel(name)
    pl.title('Support Vector Regression on ' + name)
    pl.legend()
    pl.show()
    '''

if __name__ == '__main__':
    features = load_weather("2000")
    
    # these are actual data
    feature_names = ["TEMP", "DEWP", "SLP", "STP", "MXSPD", "GUST", "PRCP", "SNDP", "WDSP"]
    ind = 0
    print train_single(features[feature_names[ind]], feature_names[ind])