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

FEATURES_IN_USE = ["TEMP", "DEWP", "SLP", "STP", "MXSPD", "GUST", "PRCP", "SNDP", "WDSP"]

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
            real_data["DEWP"] = []
            real_data["SLP"] = []
            real_data["STP"] = []
            real_data["MXSPD"] = []
            real_data["GUST"] = []
            real_data["PRCP"] = []
            real_data["SNDP"] = []
            real_data["WDSP"] = []
            
            for line in open(PATH + file_name):
                # skip first line
                if first_line: 
                    first_line = False
                    continue
                
                # extract data, they are stored as string for each row
                row = line.strip().split('\t')
                # skip January to November
                cur_moda = int(row[0][MODA_START: MODA_END + 1])
                if cur_moda < 208:
                    # I forgot why I needed a zero here...if not, an error occurs
                    temp = float(row[0][TEMP_START: TEMP_END + 1])
                    if temp == 9999.9:
                        temp = 50.0
                    real_data["TEMP"].append(temp)
                    
                    dewp = float(row[0][DEWP_START: DEWP_END + 1])
                    if dewp == 9999.9:
                        dewp = 50.0
                    real_data["DEWP"].append(dewp)
                    
                    slp = float(row[0][SLP_START: SLP_END + 1])
                    if slp == 9999.9:
                        slp = 1010.0
                    real_data["SLP"].append(slp)
                    
                    stp = float(row[0][STP_START: STP_END + 1])
                    if stp == 9999.9:
                        stp = 1010.0
                    real_data["STP"].append(stp)
                    
                    mxspd = float(row[0][MXSPD_START: MXSPD_END + 1])
                    if mxspd == 999.9:
                        mxspd = 10.0
                    real_data["MXSPD"].append(mxspd)
                    
                    gust = float(row[0][GUST_START: GUST_END + 1])
                    if gust == 999.9:
                        gust = 22.0
                    real_data["GUST"].append(gust)
                    
                    prcp = float(row[0][PRCP_START: PRCP_END + 1])
                    if prcp == 99.99:
                        prcp = 0.0
                    real_data["PRCP"].append(prcp)
                    
                    sndp = float(row[0][SNDP_START: SNDP_END + 1])
                    if sndp == 999.9:
                        sndp = 0.0
                    real_data["SNDP"].append(sndp)
                    
                    wdsp = float(row[0][WDSP_START: WDSP_END + 1])
                    if wdsp == 999.9:
                        wdsp = 5.0
                    real_data["WDSP"].append(wdsp)
                else:
                    break        

            # first 31 elements are used to train, last 7 elements used to test
            return real_data

# return 7 days prediction
def train_single(feature):
    from sklearn.svm import SVR
    
    svr_rbf = SVR(kernel='rbf', C=1e3, gamma=0.1)
    svr_lin = SVR(kernel='linear', C=1e3)
    svr_poly = SVR(kernel='poly', C=1e3, degree=2)
    
    # 31 days history, time is independent variant
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

# combine all the predicted features to predict temperature
def train_all(real_features, predicted_features, temp):
    from sklearn.svm import SVR
    
    svr_rbf = SVR(kernel='rbf', C=1e3, gamma=0.1)
    svr_lin = SVR(kernel='linear', C=1e3)
    svr_poly = SVR(kernel='poly', C=1e3, degree=2)
    
    # fit the model, real_features are independent variants
    predicted_temps = svr_rbf.fit(real_features[:31], temp[:31]).predict(predicted_features)
    
    return predicted_temps
    
def compose_features(features_dict):
    features = []
    num_samples = 0
    for key in features_dict:
        num_samples = len(features_dict[key])
        break
    
    for i in range(num_samples):
        feature = []
        for j in range(1, len(FEATURES_IN_USE)):
            feature.append(features_dict[FEATURES_IN_USE[j]][i])
        features.append(feature)
    return features

if __name__ == '__main__':
    # these are actual data, from 20000101 to 20000131, and 20000201 to 20000207
    real_data = load_weather("2000")
    
    predicted_data = {}
    for i in range(1, len(FEATURES_IN_USE)):
        predicted_data[FEATURES_IN_USE[i]] = train_single(real_data[FEATURES_IN_USE[i]][:31])
    
    # dimensions are described as FEATURES_IN_USE
    # it includes 7 samples since we want to predict weather for 1 week
    predicted_features = compose_features(predicted_data)
    real_features = compose_features(real_data)
    
    print train_all(real_features, predicted_features, real_data["TEMP"])