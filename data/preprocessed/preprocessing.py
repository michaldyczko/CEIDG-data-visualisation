import pandas as pd
import numpy as np
import json
from slugify import slugify

# ================== PRZYGOTOWANIE DANYCH


def mapping_function(series):
    series_name = series.name
    if series_name in [
        'MainAndCorrespondenceAreTheSame',
        'IsPhoneNo',
        'IsEmail',
        'IsWWW',
        'HasLicences',
        'HasPolishCitizenship',
        'ShareholderInOtherCompanies'
    ]:
        series = series.replace(True, 1).replace(False, 0).astype('int')
    elif series_name == 'Sex':
        sexes = ['M', 'F']
        sexes_out = [0, 1]
        series = series.replace(sexes, sexes_out).astype('int')
    elif series_name == 'Status':
        statuses = [
            'Wykreślony',
            'Aktywny',
            'Zawieszony',
            'Działalność jest prowadzona wyłącznie w formie spółki/spółek cywilnych'
        ]
        statuses_out = [
            0,
            1,
            2,
            3
        ]
        series = series.replace(statuses, statuses_out).astype('int')
    elif series_name == 'CommunityProperty':
        properties = [
            'tak',
            'nie',
            'ustała',
            '-'
        ]
        properties_out = [
            0,
            1,
            2,
            3
        ]
        series = series.replace(properties, properties_out).astype('int')
    elif series_name == "MainAddressVoivodeship":
        voivodeships = sorted(series.replace(
            np.nan, '').apply(slugify).unique().tolist())
        series = series.replace(np.nan, '').apply(slugify).replace(
            voivodeships,
            range(len(voivodeships))
        )
    elif series_name == "CorrespondenceAddressVoivodeship":
        voivodeships = sorted(series.replace(
            np.nan, '').apply(slugify).unique().tolist())
        series = series.replace(np.nan, '').apply(slugify).replace(
            voivodeships,
            range(len(voivodeships))
        )
    elif series_name == "MainAddressCounty":
        counties = sorted(series.replace(
            np.nan, '').apply(slugify).unique().tolist())
        series = series.replace(np.nan, '').apply(slugify).replace(
            counties,
            range(len(counties))
        )
    elif series_name == "CorrespondenceAddressCounty":
        counties = sorted(series.replace(
            np.nan, '').apply(slugify).unique().tolist())
        series = series.replace(np.nan, '').apply(slugify).replace(
            counties,
            range(len(counties))
        )
    elif series_name in ["PKDMainGroup", 'PKDMainClass']:
        series = series.astype(int, errors='ignore')
    else:
        pass

    return series


# Nazwy województw, powiatów, gmin i rodzajów gmin

terc_df = pd.read_csv('data/original/TERC_Urzedowy_2020-05-14.csv', header=0, dtype={
    'WOJ': str,
    'POW': str,
    'GMI': str,
    'RODZ': str,
    'NAZWA': str,
    'NAZWA_DOD': str,
}, sep=";")

terc_voivodeships = {row[1][0]: row[1][1] for row in terc_df[
    pd.isna(terc_df['POW'])
][["WOJ", "NAZWA"]].iterrows()}

terc_counties = {row[1][0]+row[1][1]: row[1][2] for row in
                 terc_df[terc_df['POW'].notna()][pd.isna(
                     terc_df['GMI'])][["WOJ", "POW", "NAZWA"]].iterrows()}

terc_communes = {row[1][0]+row[1][1]+row[1][2]: row[1][3] for row
                 in terc_df[pd.notna(terc_df['RODZ'])][["WOJ", "POW", "GMI", "NAZWA"]].iterrows()}

terc_communetypes = {row[1][0]+row[1][1]+row[1][2]+row[1][3]: row[1][4] for row
                     in terc_df[pd.notna(terc_df['RODZ'])][["WOJ", "POW", "GMI", "RODZ", "NAZWA_DOD"]].iterrows()}


# Populacje w gminach


terc_populations = {}

for i, population in pd.read_excel(
        'data/original/tabela17.xls', usecols="B:C", header=5, na_values=["       "], sheet_name=list(range(16)), dtype={0: str}).items():
    population = population.dropna(subset=["Identyfikator terytorialny\nCode"])
    population.columns = ["TERC", "Population"]
    terc_populations.update(
        dict(zip(population.TERC, population.Population)))

terc_populations = {k: int(v) for k, v in terc_populations.items()}


# Dochody gmin ogółem

incomes_df = pd.read_csv(
    'data/original/gminy_dochody_ogolem.csv', sep=";", header=0, dtype={0: str})
incomes_df = incomes_df.iloc[:, [0, 2]]
incomes_df.columns = ["TERC", "Incomes"]
terc_incomes = dict(zip(incomes_df.TERC, incomes_df.Incomes))
terc_incomes = {k: float(v.replace(",", ".")) for k, v in terc_incomes.items()}

# Dochody gmin pc

incomes_pc_df = pd.read_csv(
    'data/original/gminy_dochody_pc.csv', sep=";", header=0, dtype={0: str})
incomes_pc_df = incomes_pc_df.iloc[:, [0, 2]]
incomes_pc_df.columns = ["TERC", "Incomes"]
terc_incomes_pc = dict(zip(incomes_pc_df.TERC, incomes_pc_df.Incomes))
terc_incomes_pc = {k: float(v.replace(",", "."))
                   for k, v in terc_incomes_pc.items()}

# Nazwy klas PKD

with open("scrapers/PKDMainClassName.json", "r") as f:
    pkd_main_class_names = json.loads(f.read())

# =================== PREPROCESSING


ceidg_data_surviv = pd.read_csv(
    'data/original/ceidg_data_surv.csv', header=0, dtype={
        "MainAddressTERC": str,
        'CorrespondenceAddressTERC': str,
        'PKDMainClass': str,
    })

ceidg_data_surviv_encoded = ceidg_data_surviv[[
    'MainAndCorrespondenceAreTheSame',
    'IsPhoneNo',
    'IsEmail',
    'IsWWW',
    'HasLicences',
    'HasPolishCitizenship',
    'ShareholderInOtherCompanies',
    'Sex',
    'Status',
    'CommunityProperty',
    'MainAddressVoivodeship',
    'CorrespondenceAddressVoivodeship',
    'MainAddressCounty',
    'CorrespondenceAddressCounty',
    "PKDMainGroup",
    'PKDMainClass'
]].apply(
    mapping_function, axis=0).add_suffix('Encoded')

ceidg_data_surviv = ceidg_data_surviv.join(ceidg_data_surviv_encoded)

columns_unique_values = {column: list(ceidg_data_surviv[column].unique(
)) for column in list(ceidg_data_surviv.columns)}

ceidg_data_surviv['MainAddressVoivodeshipFromTERC'] = ceidg_data_surviv['MainAddressTERC'].str.slice(
    start=0, stop=2).astype(str)
ceidg_data_surviv['MainAddressCountyFromTERC'] = ceidg_data_surviv['MainAddressTERC'].str.slice(
    start=0, stop=4).astype(str)
ceidg_data_surviv['MainAddressCommuneFromTERC'] = ceidg_data_surviv['MainAddressTERC'].str.slice(
    start=0, stop=6).astype(str)
ceidg_data_surviv['MainAddressCommuneTypeFromTERC'] = ceidg_data_surviv['MainAddressTERC'].str.slice(
    start=0, stop=7).astype(str)


ceidg_data_surviv['CorrespondenceAddressVoivodeshipFromTERC'] = ceidg_data_surviv['CorrespondenceAddressTERC'].str.slice(
    start=0, stop=2).astype(str)
ceidg_data_surviv['CorrespondenceAddressCountyFromTERC'] = ceidg_data_surviv['CorrespondenceAddressTERC'].str.slice(
    start=0, stop=4).astype(str)
ceidg_data_surviv['CorrespondenceAddressCommuneFromTERC'] = ceidg_data_surviv['CorrespondenceAddressTERC'].str.slice(
    start=0, stop=6).astype(str)
ceidg_data_surviv['CorrespondenceAddressCommuneTypeFromTERC'] = ceidg_data_surviv['CorrespondenceAddressTERC'].str.slice(
    start=0, stop=7).astype(str)


ceidg_data_surviv['MainAddressVoivodeshipFromTERCVerbose'] = ceidg_data_surviv['MainAddressVoivodeshipFromTERC'].map(
    terc_voivodeships)
ceidg_data_surviv['MainAddressCountyFromTERCVerbose'] = ceidg_data_surviv['MainAddressCountyFromTERC'].map(
    terc_counties)
ceidg_data_surviv['MainAddressCommuneFromTERCVerbose'] = ceidg_data_surviv['MainAddressCommuneFromTERC'].map(
    terc_communes)
ceidg_data_surviv['MainAddressCommuneTypeFromTERCVerbose'] = ceidg_data_surviv['MainAddressCommuneTypeFromTERC'].map(
    terc_communetypes)

ceidg_data_surviv['CorrespondenceddressVoivodeshipFromTERCVerbose'] = ceidg_data_surviv['CorrespondenceAddressVoivodeshipFromTERC'].map(
    terc_voivodeships)
ceidg_data_surviv['CorrespondenceAddressCountyFromTERCVerbose'] = ceidg_data_surviv['CorrespondenceAddressCountyFromTERC'].map(
    terc_counties)
ceidg_data_surviv['CorrespondenceAddressCommuneFromTERCVerbose'] = ceidg_data_surviv['CorrespondenceAddressCommuneFromTERC'].map(
    terc_communes)
ceidg_data_surviv['CorrespondenceAddressCommuneTypeFromTERCVerbose'] = ceidg_data_surviv['CorrespondenceAddressCommuneTypeFromTERC'].map(
    terc_communetypes)

ceidg_data_surviv['MainAddressPopulation'] = ceidg_data_surviv["MainAddressTERC"].map(
    terc_populations)
ceidg_data_surviv['CorrespondenceAddressPopulation'] = ceidg_data_surviv["CorrespondenceAddressTERC"].map(
    terc_populations)

ceidg_data_surviv['MainAddressIncomes'] = ceidg_data_surviv["MainAddressTERC"].map(
    terc_incomes)
ceidg_data_surviv['CorrespondenceAddressIncomes'] = ceidg_data_surviv["CorrespondenceAddressTERC"].map(
    terc_incomes)

ceidg_data_surviv['MainAddressIncomesPC'] = ceidg_data_surviv["MainAddressTERC"].map(
    terc_incomes_pc)
ceidg_data_surviv['CorrespondenceAddressIncomesPC'] = ceidg_data_surviv["CorrespondenceAddressTERC"].map(
    terc_incomes_pc)

ceidg_data_surviv["PKDMainClassName"] = ceidg_data_surviv["PKDMainClass"].map(
    pkd_main_class_names)

ceidg_data_surviv.to_csv('ceidg_data_surviv_preprocessed.csv')
