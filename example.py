import pandas as pd

df = pd.read_csv("dataset/20201107_1100.csv", index_col="id_comune")
print(df)
