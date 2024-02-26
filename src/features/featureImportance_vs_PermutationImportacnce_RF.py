

# https://scikit-learn.org/stable/auto_examples/inspection/plot_permutation_importance.html
import os
import glob
import sys
import random
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from sklearn.inspection import permutation_importance

class make_featureCollection_analises(object):

    def __init__(self, nyear= 2022, aBacia= '741', npath=''):

        self.nyear = nyear
        self.nameBacia = aBacia
        print(f"iniciar with bacia {aBacia} an year {nyear} ")

        nameCSV = f'/{aBacia}_{nyear}_c1.csv'
        # /home/superusuario/Dados/mapbiomas/col8/features/        
        lst_pathCSV = glob.glob(npath + '/*.csv')
        # print(lst_pathCSV)
        dirCSVs = [kk for kk in lst_pathCSV[:] if nameCSV in kk]

        print("processing the file => ", dirCSVs)
        dfROIs = pd.read_csv(dirCSVs[0])
        print("the table dfROIs Shape = ", dfROIs.shape)
        # removing unimportant columns of table files
        dfROIs = dfROIs.drop(['system:index', '.geo'], axis=1)    
        # dfROIs = dfROIs[dfROIs['year'] == year]
        print("----> now shape is ", dfROIs.shape)
        columns = [kk for kk in dfROIs.columns]
        print("columns ", columns)
        # sys.exit()
        columns.remove('year')
        columns.remove('class')
        columns.remove('newclass')
        print("=============== All columns ================ \n ", columns)
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
                    dfROIs[columns], dfROIs['class'], stratify=dfROIs['class'], random_state=42)


    def make_classification(self):
        self.rf = Pipeline([
                    # ("classifierRF", RandomForestClassifier()), # n_estimators=115
                    ("classifierGB", GradientBoostingClassifier(n_estimators=115)) # n_estimators=115
                ])
        self.rf.fit(self.X_train, self.y_train)

        # Accuracy of the Model
        print(f"RF train accuracy: {self.rf.score(self.X_train, self.y_train):.3f}")
        print(f"RF test accuracy: {self.rf.score(self.X_test, self.y_test):.3f}")

    def get_featuresImportance(self):

        feature_names = self.rf[:-1].get_feature_names_out()

        mdi_importances = pd.Series(
                    self.rf[-1].feature_importances_, index=feature_names
                ).sort_values(ascending=True)

        self.plot_feature_importancesRF_bar(mdi_importances)


    def get_permutation_Importance(self):

        result = permutation_importance(
            self.rf, self.X_test, self.y_test, n_repeats=10, random_state=42, n_jobs=2
        )
        sorted_importances_idx = result.importances_mean.argsort()
        print("=====  sorted_importances_idx ===== \n", sorted_importances_idx)
        importances = pd.DataFrame(
            result.importances[sorted_importances_idx].T,
            columns= self.X_train.columns[sorted_importances_idx],
        )

        self.plot_permutation_importancesRF_blox(importances)

    def changeParameters(self):
        # We can further retry the experiment by limiting 
        # the capacity of the trees to overfit by setting 
        # min_samples_leaf at 20 data points.

        self.rf.set_params(classifier__min_samples_leaf=20).fit(self.X_train, self.y_train)
        """
            Observing the accuracy score on the training and
            testing set, we observe that the two metrics are
            very similar now. Therefore, our model is not 
            overfitting anymore. We can then check the 
            permutation importances with this new model.
        """
        print(f"RF train accuracy: {self.rf.score(self.X_train, self.y_train):.3f}")
        print(f"RF test accuracy: {self.rf.score(self.X_test, self.y_test):.3f}")


    def test_featureImport_permutation(self):
        train_result = permutation_importance(
                        self.rf, self.X_train, self.y_train, n_repeats=10, random_state=42, n_jobs=2
                    )
        test_results = permutation_importance(
                            self.rf, self.X_test, self.y_test, n_repeats=10, random_state=42, n_jobs=2
                        )
        sorted_importances_idx = train_result.importances_mean.argsort()

        train_importances = pd.DataFrame(
                        train_result.importances[sorted_importances_idx].T,
                        columns=self.X_train.columns[sorted_importances_idx],
                    )
        test_importances = pd.DataFrame(
                        test_results.importances[sorted_importances_idx].T,
                        columns=self.X_test.columns[sorted_importances_idx],
                    )

        self.plot_compare_permImport_featImport (train_importances, test_importances)

    def plot_feature_importancesRF_bar (self, seriepdMDI):
        fig, ax = plt.subplots(figsize=(10,18))
        ax = seriepdMDI.plot.barh()
        ax.set_title("Random Forest Feature Importances (MDI)")
        ax.figure.tight_layout()
        plt.show()

        plt.figure().clear()

    def plot_permutation_importancesRF_blox (self, seriepdperm):
        fig, ax = plt.subplots(figsize=(10,18))
        ax = seriepdperm.plot.box(vert=False, whis=10)
        ax.set_title("Permutation Importances (test set)")
        ax.axvline(x=0, color="k", linestyle="--")
        ax.set_xlabel("Decrease in accuracy score")
        ax.figure.tight_layout()
        plt.show()
        plt.figure().clear()

    def plot_compare_permImport_featImport (self, train_imports, test_imports):
        fig, ax = plt.subplots(figsize=(10,18))
        for name, importances in zip(["train", "test"], [train_imports, test_imports]):
            ax = importances.plot.box(vert=False, whis=10)
            ax.set_title(f"Permutation Importances ({name} set)")
            ax.set_xlabel("Decrease in accuracy score")
            ax.axvline(x=0, color="k", linestyle="--")
            ax.figure.tight_layout()

        plt.show()

def getPathCSV (nfolder):
    # get dir path of script 
    mpath = os.getcwd()
    # get dir folder before to path scripts 
    mpath = str(Path(mpath).parents[0])
    # folder of CSVs ROIs
    roisPath = '/dados/' + nfolder
    mpath += roisPath
    print("path of CSVs Rois is \n ==>",  mpath)
    return mpath
#############################################################################

lstBacias = [
    '741','7421','7422','744','745','746','7492','751','752','753',
    '754','755','756','757','758','759','7621','7622','763','764',
    '765','766','767','771','772','773', '7741','7742','775','776',
    '777','778','76111','76116','7612','7614','7615','7616','7617',
    '7618','7619', '7613'
]
lstYears = [kk for kk in range(1985, 2023)]
lstFolders =  ['Col9_ROIs_cluster/', 'Col9_ROIs_manual/']
nameFolder = lstFolders[0]
pathCSVs = getPathCSV(nameFolder)
byYear = True
byBacia = True
#############################################################################


if __name__ == '__main__':
    
    # sys.exit()
    if byBacia and byYear:
        numbBacias = len(lstBacias)
        numbYears = len(lstYears)
        print(f"we have {numbBacias} bacias and {numbYears} years")

        baciaSel = lstBacias[random.randint(0, numbBacias - 1)]
        yearSel = lstYears[random.randint(0, numbYears - 1)]
        print(f"loading .... Bacia < {baciaSel} > in Year < {yearSel} >")

        makeROIs_analises = make_featureCollection_analises(nyear= yearSel, aBacia= baciaSel, npath= pathCSVs)
        makeROIs_analises.make_classification()
        print("=========== SHOW FEATURES IMPORTANCE ===============")
        makeROIs_analises.get_featuresImportance()
        print("=========== SHOW PERMUTATION IMPORTANCE ===============")
        makeROIs_analises.get_permutation_Importance()
    
    
        print("================================================================")
        print("<> We testing the permutation in training an testing sets <>")
        makeROIs_analises.changeParameters()
        makeROIs_analises.test_featureImport_permutation()

    