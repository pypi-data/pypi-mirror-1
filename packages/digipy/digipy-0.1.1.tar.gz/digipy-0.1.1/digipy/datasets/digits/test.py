import ppdataset
d=ppdataset.Dataset("/home/fpieraut/mlboost/test/digits/digits.csv",exception_continuous_fields=['digit'])
d.GenFlayerFormat('digit')
