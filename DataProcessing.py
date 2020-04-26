import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import os
import datetime
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
import matplotlib
matplotlib.rcParams.update({'font.size': 20})

class DataProcessing:
    columns = ['WORK', 'EDUCATION', 'ABOUT', 'FAVOURITE QUOTES', 'RELATIONTSHIP',
       'FAMILY MEMBERS', 'CURRENT CITY AND HOME TOWN', 'CONTACT INFO',
       'BASIC INFO', 'LIFE EVENTS', 'Followers', 'All Friends',
       'College Friends', 'Current City Friends', 'Work Friends',
       'Hometown Friends', 'CHECK IN', 'STATUS UPDATE', 'SHARED MEMORY',
       'SHARED A POST', 'CMTS', 'LIKES', 'IMGS', 'MAX_CMTS', 'MAX_LIKES',
       'MAX_IMGS', 'MIN_CMTS', 'MIN_LIKES', 'MIN_IMGS', 'AVG_INTERVAL',
       'MAX_INTERVAL', 'MIN_INTERVAL', 'LAST_INTERVAL']
    def __init__(self, path, seed):
        self.dataset = pd.read_csv(path).iloc[:, 1:]
        self.seed = seed
    
    def show_lost_data(self):
        print(self.dataset.isna().sum())

    def clean(self, mode, assign = None):
        """mode = 'remove' or 'assign'
        assign = 0 or 'mean' (if mode = 'assign')        
        """
        self.__mode__ = mode
        self.__assign__ = assign
        self.__missing_val_columns__ = [ "Followers", 
                                "Following", 
                                "All Friends", 
                                "College Friends", 
                                "Current City Friends", 
                                "Work Friends", 
                                "Hometown Friends"
                            ]
        self.__mean__ = {}
        for col in self.__missing_val_columns__:
            index = self.dataset[col].isna()
            self.__mean__.update({col : self.dataset.loc[index == False, col].mean()})
        
        if mode == 'remove':
            self.dataset = self.dataset.drop(columns = self.__missing_val_columns__)

        elif mode == "assign":
            if assign == 0:
                for col in self.__missing_val_columns__:
                    index = self.dataset[col].isna()
                    self.dataset.loc[index, col] = 0

            elif assign == 'mean':
                for col in self.__missing_val_columns__:
                    index = self.dataset[col].isna()
                    self.dataset.loc[index, col] = self.__mean__[col]

        index = self.dataset["LAST_INTERVAL"].isna()
        self.dataset.loc[index, "LAST_INTERVAL"] = self.dataset.loc[index, "MAX_INTERVAL"]
    
    def __get_dataset_for_visualizing__(self):
        self.dataset_for_vsl = self.dataset.drop(columns = ["ID", "FB_LINK", "FB_TYPE"])

    def remove_bad_distribution_data(self):
        if self.__mode__ == 'assign':
            self.dataset = self.dataset.drop(columns = "Following")
        self.dataset = self.dataset.drop(columns = "OTHERS")
        self.dataset_for_vsl = self.dataset.drop(columns = ["ID", "FB_LINK", "FB_TYPE"])

    def remove_high_correlation_feature(self, threhold = 0.8):
        corr = self.dataset_for_vsl.corr()
        high_corr = []
        for i, col in enumerate(corr.columns):
            for j, row in enumerate(corr.index):
                if (i < j) and abs(corr.iloc[i, j]) > threhold:
                    high_corr.append([col, row, corr.iloc[i, j]])

        self.__high_corr_feature__ = []
        for features in high_corr:
            if features[0] not in self.__high_corr_feature__:
                self.__high_corr_feature__.append(features[0])
            elif features[1] not in self.__high_corr_feature__:
                self.__high_corr_feature__.append(features[1])

        self.dataset = self.dataset.drop(columns = self.__high_corr_feature__)

    def combine_target_types(self):
        index = self.dataset["FB_TYPE"] == 2
        self.dataset.loc[index, "FB_TYPE"] = 0

    def split_dataset(self):
        X = self.dataset.drop(columns = ["FB_LINK", "FB_TYPE"])
        y = self.dataset["FB_TYPE"]
        
        self.X_train, self.X_test, self.y_train, self.y_test = \
            train_test_split(X, y, train_size = 0.8, random_state = self.seed)

        self.id_train = self.X_train["ID"]
        self.X_train = self.X_train.drop(columns = "ID")

        self.id_test = self.X_test["ID"]
        self.X_test = self.X_test.drop(columns = "ID")

    def data_scaling(self):
        self.__scaler__ = StandardScaler()
        self.__scaler__ = self.__scaler__.fit(self.X_train)
        self.X_train[self.X_train.columns] = self.__scaler__.transform(self.X_train)
        self.X_test[self.X_test.columns] = self.__scaler__.transform(self.X_test) 

    def under_sampling(self):
        random_under_sampler = RandomUnderSampler(random_state = self.seed)
        self.under_X_train, self.under_y_train = random_under_sampler.fit_resample(self.X_train, self.y_train)

    def over_sampling(self):
        smote = SMOTE(random_state = self.seed)
        self.over_X_train, self.over_y_train = smote.fit_resample(self.X_train, self.y_train)

    def save_dataset(self, _dir):
        if not os.path.isdir(_dir):
            os.mkdir(_dir)
        now = datetime.date.strftime(datetime.date.today(), "%d-%m")

        over_X_train_df  = pd.DataFrame(self.over_X_train, columns= self.X_train.columns)
        over_y_train_df  = pd.DataFrame(self.over_y_train, columns= ["FB_TYPE"])
        under_X_train_df = pd.DataFrame(self.under_X_train, columns= self.X_train.columns)
        under_y_train_df = pd.DataFrame(self.under_y_train, columns= ["FB_TYPE"])

        over_train  = pd.concat([over_X_train_df, over_y_train_df], axis= 1)
        under_train = pd.concat([under_X_train_df, under_y_train_df], axis = 1)
        test = pd.concat([self.X_test, self.y_test], axis = 1)

        over_train.to_csv("{}/over_train_{}.csv".format(_dir, now))
        under_train.to_csv("{}/under_train_{}.csv".format(_dir, now))
        test.to_csv("{}/test_{}.csv".format(_dir, now))

    def run(self, mode, assign = None, remove_high_corr = False):
        self.__remove_high_corr__ = remove_high_corr
        self.clean(mode, assign)
        self.__get_dataset_for_visualizing__()
        self.remove_bad_distribution_data()
        if self.__remove_high_corr__:
            self.remove_high_correlation_feature()
        self.combine_target_types()
        self.split_dataset()
        self.data_scaling()
        self.under_sampling()
        self.over_sampling()

    def convert(self, profile):
        if self.__mode__ == "remove":
            profile = profile.drop(columns = self.__missing_val_columns__)
        
        if self.__mode__ == "assign":
            if self.__assign__ == 0:
                for col in self.__missing_val_columns__:
                    profile[col] = 0
            
            if self.__assign__ == "mean":
                for col in self.__missing_val_columns__:
                    profile[col] = self.__mean__[col]

        if profile.loc[0, "LAST_INTERVAL"] == None:
            profile.loc[0, "LAST_INTERVAL"] = profile.loc[0, "MAX_INTERVAL"]
        
        if self.__mode__ == "assign":
            profile = profile.drop(columns = "Following")

        profile = profile.drop(columns = "OTHERS")
        if self.__remove_high_corr__:
            profile = profile.drop(columns = self.__high_corr_feature__)
        profile = profile.drop(columns = ["FB_TYPE", "FB_LINK", "ID"])
        profile[profile.columns] = self.__scaler__.transform(profile)
        return profile

    @staticmethod
    def load(path):
        dataset = pd.read_csv(path)
        X   = dataset[DataProcessing.columns]
        y   = dataset["FB_TYPE"]
        _id = None
        if "ID" in dataset.columns:
            _id = dataset["ID"]

        return X, y, _id

if __name__ == "__main__":
    data = DataProcessing("dataset/profiles-7-4-2020.csv", 0)
    data.run("assign", 0)
    import pickle
    with open("DataPreprocessing.dp", mode = "wb") as f:
        pickle.dump(data, f)

    with open("DataPreprocessing.dp", mode = "rb") as f:
        pickle.load(f)