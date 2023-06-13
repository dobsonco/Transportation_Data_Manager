import pandas as pd
import time
import numpy as np


def add_to_dataframe(df,name_link_type):
    '''
    This method can be used to add/save websites to the website csv, returns dataframe with new 
    entries added to end of frame.

    df: This is the dataframe you want to add the entries to.

    name_link_type: This is an array that contains tuples with title of a website in the first position
    the link in the second position, and the type of each dataset. 
    Should Look like this -> 
    '''
    new_df = df.copy()
    del df
    for tup in name_link_type:
        new_df.loc[len(new_df.index)] = [tup[0], tup[1], tup[2], round(time.time()), "empty"]

    return new_df

def remove_entry(df,idx,save_immediately=False):
    '''
    This method deletes an entry by index, saves changes immediately depending on you choice, and then returns the new dataframe
    If save_immediately is set to false, then if the program is unable to reach then end of the main loop, the change will not be saved,
    

    df: Dataframe you are working with

    idx: integer, index of the row/entry you want deleted

    returns: New dataframe with entry removed
    '''
    new_df = df.copy()
    del df

    new_df = new_df.drop(idx).reset_index(drop=True)

    if save_immediately:
        new_df.to_csv('websites.csv',index=False)

    return new_df