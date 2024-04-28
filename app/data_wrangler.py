import csv
import pandas as pd

def merge_columns(row):
    return '\n'.join([f"{column}: {value}" for column, value in row.items()])

file = 'organization_data.csv'
df = pd.read_csv(file, header='infer')
df_filtered = df.dropna(thresh=len(df.columns) - 5 + 1)
df_filtered = df_filtered.fillna('NA')
# print(df_filtered.head())
# df_filtered['Organization Data'] = df_filtered.apply(merge_columns, axis=1)
# print(df_filtered['Organization Data'][6])
df_filtered.to_csv('organization_data_updated.csv')

     