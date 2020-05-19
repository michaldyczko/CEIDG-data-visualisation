#!/usr/bin/env python
# coding: utf-8

import pandas as pd

prep_ceidg = pd.read_csv('ceidg_data_surviv_preprocessed.csv', index_col=0)

prep_ceidg.dtypes['PKDMainDivision'] = str

prep_ceidg['MonthOfStartingOfTheBusiness'] = prep_ceidg['DateOfStartingOfTheBusiness'].apply(lambda x: int(x.split('-')[1]))

X = prep_ceidg[['YearOfStartingOfTheBusiness','MonthOfStartingOfTheBusiness',
               'NoOfAdditionalPlaceOfTheBusiness', 'NoOfLicences', 
               #'PKDMainSection','PKDMainDivision', 'PKDMainGroup', 'PKDMainClass',
               'NoOfUniquePKDSections', 'NoOfUniquePKDDivsions', 'NoOfUniquePKDGroups',
               'NoOfUniquePKDClasses', 'MainAndCorrespondenceAreTheSameEncoded',
               'IsPhoneNoEncoded', 'IsEmailEncoded', 'IsWWWEncoded',
               'HasLicencesEncoded', 'HasPolishCitizenshipEncoded',
               'ShareholderInOtherCompaniesEncoded', 'SexEncoded',
               #'CommunityPropertyEncoded', 'CommunityProperty',
               'MainAddressVoivodeshipFromTERCVerbose',
               #'MainAddressCountyFromTERCVerbose', 
               #'MainAddressCommuneFromTERCVerbose',
               'MainAddressCommuneTypeFromTERCVerbose',
               'MainAddressPopulation',
               'MainAddressIncomes',
               'MainAddressIncomesPC',
               'PKDMainClassName']]

float_cols = X.select_dtypes(include=['float64']).columns
str_cols = X.select_dtypes(include=['object']).columns

X.loc[:, float_cols] = X.loc[:, float_cols].fillna(0)
X.loc[:, str_cols] = X.loc[:, str_cols].fillna('empty')

X = pd.get_dummies(X)
y = prep_ceidg['DurationOfExistenceInMonths']

from sklearn.ensemble import RandomForestRegressor

rf = RandomForestRegressor(max_depth=10, n_jobs=-1, n_estimators=500)
rf.fit(X, y)

feature_importances = pd.DataFrame(rf.feature_importances_,
                                   index = X.columns,
                                    columns=['importance']).sort_values('importance', ascending=False)['importance']

correlations = X.select_dtypes('number').corrwith(y)
correlations.name = 'correlations'
df2 = pd.DataFrame([correlations, feature_importances*100]).T
df2 = df2.fillna(0)
df2.to_csv('corrs_and_features.csv')



