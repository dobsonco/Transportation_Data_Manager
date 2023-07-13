import pandas as pd
import sys
import os
import shutil

df = pd.read_csv(sys.path[0] + '/../websites.csv')
df.iloc[:,4] = ['empty' for x in df.iloc[:,4]]
df.to_csv(sys.path[0] + '/../websites.csv',index=False)

try:
    Data_Path = os.path.join(sys.path[0],'..','Data')
    shutil.rmtree(Data_Path)
except:
    print('Could not remove Data')