from urllib.request import urlopen
from bs4 import BeautifulSoup
import signal
import pandas as pd
import time
from datetime import datetime
import WebTools
Tools = WebTools.Tools()
import DataframeShortcuts
DS = DataframeShortcuts.Shortcuts()
from tkinter import *
from tkinter import ttk
from PIL import ImageTk,Image
import os
import sys
import shutil
import matplotlib.pyplot as plt
import numpy as np

global temp_folder
temp_folder = sys.path[0] + '/Data/temp'

# Creating timeout error to limit the runtime of a function if needed
class TimeoutException(Exception): # Creating custom error
    pass

def timeout_handler(): # Creating function to handle error
    raise TimeoutException
    
signal.signal(signal.SIGABRT, timeout_handler);
def on_start():
   global run
   run = True

def on_stop():
   global run
   run = False

def autoprocess(data_path,dl_folder):
    try:
        data = pd.read_csv(data_path)
    except:
        return

    failed = [False for col in data]
    for idx,col in enumerate(data):
        try:
            filename = data_path.split(sep='/')[-1]
            fig,ax = plt.subplots(nrows=1,ncols=1,figsize=(8,8))
            ax.hist(np.array(data[col]))
            fig.savefig(dl_folder + '/' + filename + str(idx) + '.png')
            plt.close(fig)
            del fig,ax
        except:
            failed[idx] = True
            continue

    if all(failed):
        filename = data_path.split(sep='/')[-1]
        failed_to_process = open(dl_folder + '/failed_to_process.txt','a')
        e = datetime.now()
        failed_to_process.write(f'{filename} failed to open on {str(e.year) + ", " + str(e.month) + ", " + str(e.day)}\n')
        failed_to_process.close()

def main():
   if run:
      # Check if data folder exists
      data_folder_path = sys.path[0] + '/Data'
      if not os.path.isdir(data_folder_path):
         print('Directory "Data" does not exists in current directory. Creating Directory.')
         os.mkdir(path=data_folder_path)
         os.mkdir(path=data_folder_path+'/temp')

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

         # 2: Iterate over all entries to check if enough time has passed

         if True: # Replace with -> (round(time.time()) - info[2] >= 7.884e+6) This is not ready to be tested yet
            df.iloc[idx] = [info[0],info[1],int(time.time())]
            
            dl_folder = data_folder_path + '/' + info[0]
            if os.path.isdir(dl_folder):
               try:
                  # download file in temp folder
                  filename = next(os.walk(temp_folder), (None, None, []))[2][0]
                  filepath = dl_folder + '/' + filename
                  shutil.move(temp_folder + '/' + filename, filepath)
                  autoprocess(filepath,dl_folder)
               except:
                  continue
            else:
               try:
                  # download file in temp folder
                  os.mkdir(dl_folder)
                  filename = next(os.walk(temp_folder), (None, None, []))[2][0]
                  filepath = dl_folder + '/' + filename
                  shutil.move(temp_folder + '/' + filename, filepath)
                  autoprocess(filepath,dl_folder)
               except:
                  continue      
            
            # Make sure nothing is left in temp, this is just a failsafe
            # move should delete the file that got moved from its original directory
            for root, dirs, files in os.walk('/path/to/folder'):
               for f in files:
                  os.unlink(os.path.join(root, f))
      
      # 3. Check to see if user asked for entry to be deleted

      # 4. Overwrite file 
      df.to_csv('websites.csv',index=False)
      print('looped')
      
   window.after(1, main)
window = Tk()
window.title('Transportation Data Manager')
window.iconbitmap(sys.path[0] + '/Resources/car1.ico')

frame = Frame(window)
frame.pack()

canvas = Canvas(frame, width=400, height=300, bg='#D3D3D3')
canvas.pack()

global run
run = False

start_label = Text(canvas,wrap=WORD,width=30,height=2,padx=6,pady=5,highlightthickness=0)
start_label.tag_configure('center',justify='center')  
start_label.insert('1.0','When pressed, this button will start the loop')
start_label.tag_add('center',1.0,'end')
start_label.place(relx = 0.3, rely = 0.4,anchor=CENTER)

start_button = Button(canvas, text="Start", command=on_start, padx=6,pady=5,highlightthickness=0)
start_button.place(relx=0.75, rely=0.4, anchor=CENTER)

end_label = Text(canvas,wrap=WORD,width=30,height=2,padx=6,pady=5,highlightthickness=0)
end_label.tag_configure('center',justify='center')  
end_label.insert('1.0','When pressed, this button will end the loop')
end_label.tag_add('center',1.0,'end')
end_label.place(relx = 0.3, rely = 0.6,anchor=CENTER)

end_button = Button(canvas, text="Stop", command=on_stop,padx=6,pady=5,highlightthickness=0)
end_button.place(relx=0.75,rely=0.6,anchor=CENTER)

info_label = Text(canvas,wrap=WORD,width=30,height=5,padx=6,pady=5,highlightthickness=0)
info_label.tag_configure('center',justify='center')  
info_label.insert('1.0','''This rudimentary GUI controls the script. 
New buttons and features may be added later if I can make it work''')
info_label.tag_add('center',1.0,'end')
info_label.place(relx=0.5, rely = 0.15,anchor=CENTER)

resized_img = Image.open(sys.path[0] + '/Resources/UT_logo.png').resize((130,100),Image.LANCZOS);
img = ImageTk.PhotoImage(resized_img)
canvas.create_image(350,260,image=img)

who_made_this = Text(canvas,wrap=WORD,width=35,height=3,padx=6,pady=5,highlightthickness=0)
who_made_this.tag_configure('center',justify='center')  
who_made_this.insert('1.0','''This program was made by Collin Dobson for the UTORII SMaRT internship''')
who_made_this.tag_add('center',1.0,'end')
who_made_this.place(relx=0.35, rely = 0.85,anchor=CENTER)

window.after(1, main)

window.mainloop()
