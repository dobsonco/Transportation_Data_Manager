import pandas as pd
import time

class Shortcuts:

    def add_to_dataframe(self,df,names_and_links):
        '''
        This method can be used to add/save websites to the website csv, returns dataframe with new 
        entries added to end of frame.

        df: This is the dataframe you want to add the entries to.

        names_and_links: This is an array that contains tuples with title of a website in the first position
            and the link in the second position of each. 
        '''
        new_df = df.copy()
        del df
        for tup in names_and_links:
            new_df.loc[len(new_df.index)] = [tup[0], tup[1], round(time.time())]

        return new_df

    def remove_entry(self,df,idx,save_immediately=False):
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