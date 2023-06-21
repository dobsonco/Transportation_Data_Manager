from urllib.request import urlopen
import requests
import pandas as pd
import time
from datetime import datetime
from tkinter import *
from PIL import ImageTk,Image
import os
import sys
import matplotlib.pyplot as plt
import numpy as np
from zipfile import ZipFile
import glob
import filecmp
import shutil

global sys_path
sys_path = sys.path[0]

global temp_folder
temp_folder = os.path.join(sys_path,'Data','temp')

global ConnectedToInternetTimer
ConnnectedToInternetTime = round(time.time(),0) + 1000

global run
run = False

def on_start():
   global run
   run = True
   global ConnectedToInternetTimer
   ConnnectedToInternetTime = round(time.time(),0)
   switch_start()
   if end_button["state"] == "disabled":
      switch_stop()

def on_stop():
   global run
   run = False
   switch_stop()
   if start_button["state"] == "disabled":
      switch_start()

def switch_start():
   if start_button["state"] == "normal":
      start_button["state"] = "disabled"
   elif (start_button["state"] != "normal") and (not run):
      start_button["state"] = "normal"

def switch_stop():
   if end_button["state"] == "normal":
      end_button["state"] = "disabled"
   elif (start_button["state"] != "normal"):
      end_button["state"] = "normal"

def connected_to_internet(url='http://www.google.com/', timeout=5):
   try:
      _ = requests.head(url, timeout=timeout)
      return True
   except requests.ConnectionError:
      return False

def download_url(url, save_path, chunk_size=1024, type='csv'):
   '''
   Save path is just the folder you want to download it in.

   Type must be a string, with the type of file you're downloading

   returns name of new file and its filepath. If downloaded is a zip, it will extract it and then 
   return the path to the folder along with the name of the folder
   '''
   files_in_directory = len(next(os.walk(save_path), (None, None, []))[2])
   name = save_path.split(sep='/')[-1] + '-' + str(files_in_directory) + '.' + type
   filepath = os.path.join(save_path,name)

   r = requests.get(url, stream=True)
   with open(filepath, 'wb') as fd:
      for chunk in r.iter_content(chunk_size=chunk_size):
         fd.write(chunk)
   
   try:
      if type == 'zip':
         with ZipFile(filepath,'r') as zObject:  
            zObject.extractall(path=save_path)
            zObject.close()
            os.unlink(filepath)
         filepath = max(glob.glob(os.path.join(save_path, '*/')), key=os.path.getmtime)
         name = filepath.split(sep='/')[-2]
   except:
      raise ValueError

   return filepath

def clear_temp(dir=temp_folder):
   '''
   Clears all files and directories from temp folder
   '''
   for filename in os.listdir(dir):
      file_path = os.path.join(dir, filename)
      try:
         if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
         elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
      except:
         pass

def autoprocess(data_path,dl_folder):
   '''
   Takes path to data and path to download folder and generates plots from it
   '''
   try:
      data = pd.read_csv(data_path,low_memory=False)
   except:
      filename = data_path.split(sep='/')[-1]
      data_folder = os.path.join(dl_folder,filename.split(sep='.')[0])
      if not os.path.isdir(data_folder):
         os.mkdir(data_folder)
      failed_to_process = open(os.path.join(data_folder,'failed_to_process.txt'),'a')
      e = datetime.now()
      failed_to_process.write(f'{filename} failed to open on {str(e.year)}, {str(e.month)}, {str(e.day)}\n')
      failed_to_process.close()
      return

   filename = data_path.split(sep='/')[-1].split(sep='.')[0]
   data_folder = os.path.join(dl_folder,(filename.split(sep='.')[0] + '_Data'))
   if not os.path.isdir(data_folder):
      os.mkdir(data_folder)
      histogram_path = os.path.join(data_folder,'Histograms')
      os.mkdir(histogram_path)
      plots_path = os.path.join(data_folder,'Plots')
      os.mkdir(plots_path)

   failed1 = [False for idx,col in enumerate(data) if (data.dtypes[idx] != 'object') and (data.dtypes[idx] != 'bool')]
   for idx,col in enumerate(data):
      if (data.dtypes[idx] != 'object') and (data.dtypes[idx] != 'bool'):
         try:            
            fig,ax = plt.subplots(nrows=1,ncols=1,figsize=(8,8))
            ax.hist(np.array(data[col]))
            ax.set_xlabel(col)
            ax.set_title('Autogenerated Histogram ' + str(idx + 1))
            ax.set_facecolor('#ADD8E6')
            ax.set_axisbelow(True)
            ax.yaxis.grid(color='white', linestyle='-')
            savepath = os.path.join(histogram_path,(filename+'_Histogram-'+str(idx + 1)+'.png'))
            fig.savefig(savepath,format='png')
            plt.close('all')
         except:
            plt.close('all')
            failed1[idx] = True
            pass
   
   failed2 = [False for idx,col in enumerate(data) if (data.dtypes[idx] != 'object') and (data.dtypes[idx] != 'bool')]
   for idx,col in enumerate(data):
      if (data.dtypes[idx] != 'object') and (data.dtypes[idx] != 'bool'):
         try:            
            fig,ax = plt.subplots(nrows=1,ncols=1,figsize=(8,8))
            ax.plot([idx for idx,j in enumerate(data[col])],np.array(data[col]))
            ax.set_xlabel(col)
            ax.set_title('Autogenerated Plot ' + str(idx + 1))
            ax.set_facecolor('#ADD8E6')
            ax.set_axisbelow(True)
            ax.yaxis.grid(color='white', linestyle='-')
            ax.xaxis.grid(color='white', linestyle='-')
            savepath = os.path.join(plots_path,(filename+'_Plot-'+str(idx + 1)+'.png'))
            fig.savefig(savepath,format='png')
            plt.close('all')
         except:
            plt.close('all')
            failed2[idx] = True
            pass

   if (not all(failed1)) and (not all(failed2)):
      return

   failed_to_process = open(os.path.join(data_folder,'failed_to_process.txt'),'a')
   e = datetime.now()
   filename = data_path.split(sep='/')[-1]
   if all(failed1) and all(failed2):
      failed_to_process.write(f'{filename} failed to process both histograms and plots on {str(e.year)}, {str(e.month)}, {str(e.day)}\n')
      failed_to_process.close()
   elif all(failed1) and not all(failed2):
      failed_to_process.write(f'{filename} failed to process histograms on {str(e.year)}, {str(e.month)}, {str(e.day)}\n')
      failed_to_process.close()
   elif all(failed2) and not all(failed1):
      failed_to_process.write(f'{filename} failed to process plots on {str(e.year)}, {str(e.month)}, {str(e.day)}\n')
      failed_to_process.close()

   return

def main():
   if run:
      if not connected_to_internet():
         if (round(time.time(),0) - ConnnectedToInternetTime >= 1000) or (round(time.time(),0) - ConnnectedToInternetTime <= 5):
            print('Not connected to internet')
         return

      # Check if data folder exists
      data_folder_path = os.path.join(sys_path,'Data')
      if not os.path.isdir(data_folder_path):
         print('Directory "Data" does not exist in current directory. Creating Directory.')
         os.mkdir(path=data_folder_path)
         os.mkdir(path=temp_folder)

      # Check if websites.csv exists
      websites_csv_path = os.path.join(sys_path,'websites.csv')
      if not os.path.isfile(websites_csv_path):
         sys.exit('Necessary file "websites.csv" does not exist in current directory. Exiting Program.')

      # Read in csv with websites
      try:
         df = pd.read_csv(websites_csv_path,header=0)
         df = df.reset_index(drop=True)
      except:
         sys.exit('Failed to open websites.csv. Exiting Program.')

      # Iterate over rows of websites.csv
      for idx,info in df.iterrows():
         dl_folder = os.path.join(data_folder_path,info[0])  

         if (info[4] == 'empty') or (not os.path.isdir(dl_folder)):
            try:
               if not os.path.isdir(dl_folder):
                  os.mkdir(dl_folder)
               filepath = download_url(url=info[1],save_path=dl_folder,type=info[2])
               df.iloc[idx,4] = filepath
               autoprocess(filepath,dl_folder)
            except:
               pass

         # Check if enough time has passed
         if ((round(time.time(),0) - info[3]) >= 1000):
            df.iloc[idx,3] = int(time.time()) 

            if (info[4] != 'empty') and ((os.path.isfile(info[4])) or (os.path.isdir(info[4]))):
               try:

                  #Download data to temp folder using url, return temp filepath and name of file
                  new_filepath = download_url(url=info[1],save_path=temp_folder,type=info[2])
                  old_filepath = info[4]

                  #Check to see if files are the same
                  if (info[2] == 'zip'):
                     same_file = filecmp.cmpfiles(a=new_filepath,b=old_filepath,shallow=False)
                  else:
                     same_file = filecmp.cmp(f1=new_filepath,f2=old_filepath,shallow=False)

                  #If files are the same, clear temp folder
                  if same_file:
                     clear_temp()

                  #If files are different, move new file in temp to overwrite old file
                  #clear temp folder, delete old data folder, and process new data
                  elif not same_file:
                     shutil.move(src=new_filepath,dst=old_filepath)
                     clear_temp()

                     filename = old_filepath.split(sep='/')[-1].split(sep='.')[0]
                     data_folder = os.path.join(dl_folder,(filename.split(sep='.')[0] + '_Data'))
                     shutil.rmtree(path=data_folder)

                     # autoprocess(data_path=old_filepath,dl_folder=dl_folder)

                     try:
                        del old_filepath,new_filepath
                     except:
                        pass

               except:
                  pass

         try:
            clear_temp()
         except:
            pass
      
      # 3. Check to see if user asked for entry to be deleted <- Not sure if this will get implemented

      # 4. Overwrite file 
      df.to_csv(websites_csv_path,index=False)
      
   window.after(1, main)

window = Tk()
window.title('Transportation Data Manager')
window.iconbitmap(os.path.join(sys_path,'Resources','car2.ico'))

frame = Frame(window)
frame.pack()

canvas = Canvas(frame, width=400, height=300, bg='#D3D3D3')
canvas.pack()

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

resized_img = Image.open(os.path.join(sys_path,'Resources','UT_logo.png')).resize((130,100),Image.LANCZOS);
img = ImageTk.PhotoImage(resized_img)
canvas.create_image(350,260,image=img)

who_made_this = Text(canvas,wrap=WORD,width=35,height=3,padx=6,pady=5,highlightthickness=0)
who_made_this.tag_configure('center',justify='center')  
who_made_this.insert('1.0','''This program was made by Collin Dobson for the UTORII SMaRT internship''')
who_made_this.tag_add('center',1.0,'end')
who_made_this.place(relx=0.35,rely = 0.85,anchor=CENTER)

window.after(1, main)

window.mainloop()