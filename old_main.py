from urllib.request import urlopen
from bs4 import BeautifulSoup
import signal
import pandas as pd
import time
import WebTools
Tools = WebTools.Tools()
import DataframeShortcuts
DS = DataframeShortcuts.Shortcuts()
from tkinter import *
from tkinter import ttk
import os
import sys

window = Tk()
window.title('Transportation Data Manager')
window.geometry('600x600')

run = False

# Creating timeout error to limit the runtime of a function if needed
class TimeoutException(Exception): # Creating custom error
    pass

def timeout_handler(): # Creating function to handle error
    print('Reached maximum allotted time')
    raise TimeoutException
    
signal.signal(signal.SIGALRM, timeout_handler);

def on_start():
   global run
   run = True

def on_stop():
   global run
   run = False

def main():
   if run:
      # Check if data folder exists
      data_folder_path = sys.path[0] + '/Data'
      if not os.path.isdir(data_folder_path):
         print('Directory "Data" does not exists in current directory. Creating Directory.')
         os.mkdir(path=data_folder_path)

      # Check if websites.csv exists
      websites_csv_path = sys.path[0] + '/websites.csv'
      if not os.path.isfile(websites_csv_path):
         sys.exit('Necessary file "websites.csv" does not exsist in current directory. Exiting Program.')

      # 1. Read in csv with websites
      try:
         df = pd.read_csv(websites_csv_path,header=0)
         df = df.reset_index(drop=True)
      except:
         sys.exit('Failed to open websites.csv. Exiting Program.')

      for idx,info in df.iterrows():
         pass
         # 2: Iterate over all entries to check if enough time has passed
         # 3: If data was updated, update the time on the websites csv to current time
         # 4: if data was updated, download data(?) into folder named after the title of the website
         # 5: attempt to process data, if that fails, make some sort of identifier, maybe a text file in the same directory
         #    with the file name and date that it failed to process
         continue
      
      # 3. Check to see if user asked for entry to be deleted

      # 4. Overwrite file 
      df.to_csv('websites.csv',index=False)
      print('looped')
   window.after(1, main)

start_label = Text(window,wrap=WORD,width=30,height=2,padx=1,pady=1)
start_label.tag_configure('center',justify='center')  
start_label.insert('1.0','When pressed, this button will start the loop')
start_label.tag_add('center',1.0,'end')
start_label.place(relx = 0.3, rely = 0.3,anchor=CENTER)

start_button = ttk.Button(window, text="Start", command=on_start)
start_button.place(relx=0.7, rely=0.3, anchor=CENTER)


end_label = Text(window,wrap=WORD,width=30,height=2,padx=1,pady=1)
end_label.tag_configure('center',justify='center')  
end_label.insert('1.0','When pressed, this button will end the loop')
end_label.tag_add('center',1.0,'end')
end_label.place(relx = 0.3, rely = 0.7,anchor=CENTER)

end_button = ttk.Button(window, text="Stop", command=on_stop)
end_button.place(relx=0.7,rely=0.7,anchor=CENTER)

window.after(1, main)

window.mainloop()