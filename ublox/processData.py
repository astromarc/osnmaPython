# This code aims to process an input data named "data.csv" from an ublo M9 Receiver, especially the UBX messages SBFRX concerning GALILEO only (no GPS, GLONASS and others) 

import pandas as pd

fields = ['gnssId', 'svId', 'reserved0', 'freqId', 'numWords', 'chn', 'version', 'reserved1', 'dwrd_01', 'dwrd_02', 'dwrd_03'
, 'dwrd_04', 'dwrd_05', 'dwrd_06', 'dwrd_07',  'dwrd_08', 'dwrd_09']

df = pd.read_csv("data.csv",names=fields)
df_drop = df.drop(columns=['gnssId', 'svId', 'reserved0', 'freqId', 'numWords', 'chn', 'version', 'reserved1'])
df_drop_hex = df_drop.applymap(hex)

df_drop_hex['dwrd_HEX'] = df['dwrd_01'].map(hex) + df['dwrd_02'].map(hex) + df['dwrd_03'].map(hex) + df['dwrd_04'].map(hex) + df['dwrd_05'].map(hex) + df['dwrd_06'].map(hex) + df['dwrd_07'].map(hex) + df['dwrd_08'].map(hex) + df['dwrd_09'].map(hex)

df = df.join(df_drop_hex['dwrd_HEX'])

print(df)

df.to_csv ('data_processed.csv', index = False, header=True)