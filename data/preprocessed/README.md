# PODSUMOWANIE PREPROCESSINGU

## 1

Zakodowano:

1. 'MainAndCorrespondenceAreTheSame',
1. 'IsPhoneNo',
1. 'IsEmail',
1. 'IsWWW',
1. 'HasLicences',
1. 'HasPolishCitizenship',
1. 'ShareholderInOtherCompanies',
1. 'Sex',
1. 'Status',
1. 'CommunityProperty',
1. 'MainAddressVoivodeship',
1. 'CorrespondenceAddressVoivodeship',
1. 'MainAddressCounty',
1. 'CorrespondenceAddressCounty',
1. "PKDMainGroup",
1. 'PKDMainClass'

i zapisano w kolumnie z suffixem 'Encoded'

## 2

Wyłuskano z 'MainAddressTERC':

1. 'MainAddressVoivodeshipFromTERC'
1. 'MainAddressCountyFromTERC'
1. 'MainAddressCommuneFromTERC'
1. 'MainAddressCommuneTypeFromTERC'

oraz odkodowano ich nazwy do:

1. 'MainAddressVoivodeshipFromTERCVerbose'
1. 'MainAddressCountyFromTERCVerbose'
1. 'MainAddressCommuneFromTERCVerbose'
1. 'MainAddressCommuneTypeFromTERCVerbose'

Analogicznie dla 'CorrespondenceAddressTERC'

## 3

Dodano:

1. 'MainAddressPopulation'
1. 'MainAddressIncomes'
1. 'MainAddressIncomesPC'
1. 'CorrespondenceAddressPopulation'
1. 'CorrespondenceAddressIncomes'
1. 'CorrespondenceAddressIncomesPC'
1. 'PKDMainClassName'