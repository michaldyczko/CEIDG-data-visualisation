import numpy as np
import pandas as pd
from lifelines.fitters.kaplan_meier_fitter import KaplanMeierFitter


df = pd.read_csv('./ceidg_data_surviv_preprocessed.csv')
features = [
    'MainAddressVoivodeshipFromTERCVerbose', 'IsPhoneNoEncoded',
    'IsEmailEncoded', 'IsWWWEncoded', 'HasLicencesEncoded',
    'HasPolishCitizenshipEncoded', 'ShareholderInOtherCompaniesEncoded',
    'SexEncoded', 'CommunityPropertyEncoded'
]
values = {feature: df[feature].unique().tolist() for feature in features}

surv = {}
label = 'whole_dataset'
surv[label] = KaplanMeierFitter() \
    .fit(durations=df['DurationOfExistenceInMonths'],
         event_observed=df['Terminated'], label=label) \
    .survival_function_
timeline = surv['whole_dataset'].index.tolist()

for feature in values:
    for val in values[feature]:
        label = feature + '_' + str(val)
        if val is np.nan:
            df_ = df.loc[df[feature].isna()]
        else:
            df_ = df.loc[df[feature] == val]
        surv[label] = KaplanMeierFitter() \
            .fit(durations=df_['DurationOfExistenceInMonths'],
                 event_observed=df_['Terminated'],
                 label=label, timeline=timeline) \
            .survival_function_

km_curves = pd.concat(surv.values(), axis=1).reset_index()
km_curves.to_csv('km_curves.csv', index=False)
