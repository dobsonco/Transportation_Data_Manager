import pandas as pd
import sys

df = pd.read_csv(sys.path[0] + '/websites.csv')
l = ['empty' for x in df.iloc[:,4]]
df.iloc[:,4] = l
df.to_csv(sys.path[0] + '/websites.csv',index=False)