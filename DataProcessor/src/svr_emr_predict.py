'''
Created on Nov 18, 2013

@author: wenjie
'''
from mrjob.job import MRJob
import re

WORD_RE = re.compile(r"[\w']+")

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

FEATURES_IN_USE = ["TEMP", "DEWP", "WDSP", "PRCP"]

class MRSupportVectorRegressionPredict(MRJob):

    def mapper_parse_city(self, _, line):
        if line[0] != "S":
            # extract data, they are stored as string for each row
            row = line.strip().split('\t')
            stn = int(row[0][STN_START: STN_END + 1])
            moda = int(row[0][MODA_START: MODA_END + 1])
            temp = float(row[0][TEMP_START: TEMP_END + 1])
            if temp == 9999.9:
                temp = 50.0
            dewp = float(row[0][DEWP_START: DEWP_END + 1])
            if dewp == 9999.9:
                dewp = 50.0
            slp = float(row[0][SLP_START: SLP_END + 1])
            if slp == 9999.9:
                slp = 1010.0
            stp = float(row[0][STP_START: STP_END + 1])
            if stp == 9999.9:
                stp = 1010.0
            mxspd = float(row[0][MXSPD_START: MXSPD_END + 1])
            if mxspd == 999.9:
                mxspd = 10.0
            gust = float(row[0][GUST_START: GUST_END + 1])
            if gust == 999.9:
                gust = 22.0
            prcp = float(row[0][PRCP_START: PRCP_END + 1])
            if prcp == 99.99:
                prcp = 0.0
            sndp = float(row[0][SNDP_START: SNDP_END + 1])
            if sndp == 999.9:
                sndp = 0.0
            wdsp = float(row[0][WDSP_START: WDSP_END + 1])
            if wdsp == 999.9:
                wdsp = 5.0
            
            attributes = {}
            attributes["MODA"] = moda
            attributes["TEMP"] = temp
            attributes["DEWP"] = dewp
            attributes["SLP"] = slp
            attributes["STP"] = stp
            attributes["MXSPD"] = mxspd
            attributes["GUST"] = gust
            attributes["PRCP"] = prcp
            attributes["SNDP"] = sndp
            attributes["WDSP"] = wdsp
            
            yield (stn, attributes)
    
    def reducer_combine_attr(self, stn, atts):
        all_sorted_samples = sorted(atts, key=lambda atts: atts["MODA"])
        samples = []
        for sample in all_sorted_samples:
            if sample["MODA"] < 208:
                samples.append(sample)
        yield (stn, samples)
    
    def mapper_pick_desired_features(self, stn, all_samples):
        samples = []
        for sample in all_samples:
            desired_features = {}
            desired_features["MODA"] = sample["MODA"]
            for i in range(len(FEATURES_IN_USE)):
                desired_features[FEATURES_IN_USE[i]] = sample[FEATURES_IN_USE[i]]
            samples.append(desired_features)
        yield (stn, samples)
        
    def reducer_svr_predict(self, stn, years_samples):
        real_data = {}
        for i in range(len(FEATURES_IN_USE)):
            real_data[FEATURES_IN_USE[i]] = []
        # only one list in desired_samples, since each input city has one year data
        for year in years_samples:
            for day in year:
                for i in range(len(FEATURES_IN_USE)):
                    real_data[FEATURES_IN_USE[i]].append(day[FEATURES_IN_USE[i]])
                    
        predicted_data = {}
        for i in range(1, len(FEATURES_IN_USE)):
            predicted_data[FEATURES_IN_USE[i]] = self.__predict_single(real_data[FEATURES_IN_USE[i]][:31])
        
        predicted_features = self.__compose_features(predicted_data)
        real_features = self.__compose_features(real_data)
        
        predicted_temps = self.__predict_all(real_features, predicted_features, real_data["TEMP"])
        
        output_predicted_temps = []
        for temp in predicted_temps:
            output_predicted_temps.append(temp)
        
        yield stn, output_predicted_temps
    
    def steps(self):
        return [
            self.mr(mapper=self.mapper_parse_city,
                    reducer=self.reducer_combine_attr),
            self.mr(mapper=self.mapper_pick_desired_features,
                    reducer=self.reducer_svr_predict)
        ]
    
    def __compose_features(self, features_dict):
        features = []
        num_samples = 0
        for key in features_dict:
            num_samples = len(features_dict[key])
            break
        
        for i in range(num_samples):
            feature = []
            for j in range(1, len(FEATURES_IN_USE)):
                feature.append(features_dict[FEATURES_IN_USE[j]][i])
            # print feature
            features.append(feature)
        return features
    
    # return 7 days prediction
    def __predict_single(self, feature):
        from sklearn.svm import SVR
        
        svr_rbf = SVR(kernel='rbf', C=1e3, gamma=0.1)
        #svr_lin = SVR(kernel='linear', C=1e3)
        #svr_poly = SVR(kernel='poly', C=1e3, degree=2)
        
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

    # combine all the predicted features to predict temperature
    def __predict_all(self, real_features, predicted_features, temp):
        from sklearn.svm import SVR
        
        svr_rbf = SVR(kernel='rbf', C=1e3, gamma=0.1)
        #svr_lin = SVR(kernel='linear', C=1e3)
        #svr_poly = SVR(kernel='poly', C=1e3, degree=2)
        
        # fit the model, real_features are independent variants
        predicted_temps = svr_rbf.fit(real_features[:31], temp[:31]).predict(predicted_features)
        
        return predicted_temps
    
if __name__ == '__main__':
    MRSupportVectorRegressionPredict.run()