import pandas as pd
import sys

df = pd.read_csv(sys.path[0] + '/websites.txt')
l = ['empty' for x in df.iloc[:,4]]
df.iloc[:,4] = l
df.to_csv(sys.path[0] + '/websites.txt',index=False)