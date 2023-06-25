from requests import head,ConnectionError,get
from pandas import read_csv,DataFrame
from time import time,sleep
from datetime import datetime
from tkinter import *
from PIL import ImageTk,Image
import os
from sys import path,exit
import matplotlib.pyplot as plt
from numpy import array
from zipfile import ZipFile
from glob import glob
from filecmp import cmpfiles,cmp
from shutil import move,rmtree
from threading import Thread
import re

global sys_path
sys_path = path[0]

global temp_folder
temp_folder = os.path.join(sys_path,'Data','temp')

global websites_csv_path
websites_csv_path = os.path.join(sys_path,'websites.csv')

global data_folder_path
data_folder_path = os.path.join(sys_path,'Data')

global ConnectedToInternetTimer
ConnnectedToInternetTime = round(time(),0) + 1000

global run
run = False

global stopped
stopped = False

def on_start():
   '''
   This mess of a function starts the manin thread
   '''
   global run
   run = True
   global ConnectedToInternetTimer
   ConnnectedToInternetTime = round(time(),0)
   global stopped
   stopped = False
   global main_thread
   main_thread = Thread(target=main).start()
   print('started main thread')
   switch()

def on_stop():
   '''
   This function stops the main thread
   '''
   global run
   run = False
   global stopped
   stopped = True
   switch()

def switch():
   # Toggles the buttons on the the GUI, because of the multithreading, make sure to not change this
   if (start_button["state"] == "normal") and (end_button["state"] == "normal") and (run == False):
      start_button["state"] = "normal"
      end_button["state"] = "disabled"
   elif start_button["state"] == "normal":
      start_button["state"] = "disabled"
      end_button["state"] = "normal"
   elif (start_button["state"] != "normal"):
      start_button["state"] = "normal"
      end_button["state"] = "disabled"

def connected_to_internet(url='http://www.google.com/', timeout=5):
   '''
   Does what it says, returns true if connected to internet, else returns false
   '''
   try:
      _ = head(url, timeout=timeout)
      return True
   except:
      return False

def download_url(url, save_path, chunk_size=1024, type='csv'):
   '''
   Save path is just the folder you want to download it in.

   Type must be a string, with the type of file you're downloading

   returns name of new file and its filepath. If downloaded is a zip, it will extract it and then 
   return the path to the folder along with the name of the folder
   '''
   files_in_directory = len(next(os.walk(save_path), (None, None, []))[2])
   name = os.path.basename(save_path) + '-' + str(files_in_directory) + '.' + type
   filepath = os.path.join(save_path,name)

   r = get(url, stream=True)
   with open(filepath, 'wb') as fd:
      for chunk in r.iter_content(chunk_size=chunk_size):
         fd.write(chunk)
   
   try:
      if type == 'zip':
         with ZipFile(filepath,'r') as zObject:  
            zObject.extractall(path=save_path)
            zObject.close()
            os.unlink(filepath)
         filepath = max(glob(os.path.join(save_path, '*/')), key=os.path.getmtime)
         name = os.path.basename(filepath)
   except:
      raise ValueError
   return filepath

def clear_temp(dir=temp_folder):
   '''
   Clears all files and directories from temp folder, can be used on other folders
   '''
   for filename in os.listdir(dir):
      file_path = os.path.join(dir, filename)
      try:
         if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
         elif os.path.isdir(file_path):
            rmtree(file_path)
      except:
         pass

def autoprocess():
   if not run:
      window.after(100,autoprocess)
      return

   to_process = []
   to_process = glob(data_folder_path + '/*/*.csv')

   for i,vals in enumerate(to_process):
      data_path = vals
      dl_folder = data_path[0:(len(data_path)-(len(os.path.basename(data_path))))]
      filename = os.path.basename(data_path)
      try:
         data = read_csv(data_path,low_memory=False)
      except:
         data_folder = os.path.join(dl_folder,filename.split(sep='.')[0])
         if not os.path.isdir(data_folder):
            os.mkdir(data_folder)
         failed_to_process = open(os.path.join(data_folder,'failed_to_process.txt'),'a')
         e = datetime.now()
         failed_to_process.write(f'{filename} failed to open on {str(e.year)}, {str(e.month)}, {str(e.day)}\n')
         failed_to_process.close()
         continue

      data_folder = os.path.join(dl_folder,(filename.split(sep='.')[0] + '_Data'))
      if not os.path.isdir(data_folder):
         os.mkdir(data_folder)
         histogram_path = os.path.join(data_folder,'Histograms')
         os.mkdir(histogram_path)
         plots_path = os.path.join(data_folder,'Plots')
         os.mkdir(plots_path)

      for j,col in enumerate(data):
         if (data.dtypes[j] != 'object') and (data.dtypes[j] != 'bool'):
            try:            
               fig,ax = plt.subplots(nrows=1,ncols=1,figsize=(8,8))
               ax.hist(array(data[col]))
               ax.set_xlabel(col)
               ax.set_title('Autogenerated Histogram ' + str(j + 1))
               ax.set_facecolor('#ADD8E6')
               ax.set_axisbelow(True)
               ax.yaxis.grid(color='white', linestyle='-')
               savepath = os.path.join(histogram_path,(filename+'_Histogram-'+str(j + 1)+'.png'))
               fig.savefig(savepath,format='png')
               plt.close('all')
            except:
               plt.close('all')
               pass
            try:            
               fig,ax = plt.subplots(nrows=1,ncols=1,figsize=(8,8))
               ax.plot([idx+1 for idx,j in enumerate(data[col])],array(data[col]))
               ax.set_xlabel(col)
               ax.set_title('Autogenerated Plot ' + str(j + 1))
               ax.set_facecolor('#ADD8E6')
               ax.set_axisbelow(True)
               ax.yaxis.grid(color='white', linestyle='-')
               ax.xaxis.grid(color='white', linestyle='-')
               savepath = os.path.join(plots_path,(filename+'_Plot-'+str(j + 1)+'.png'))
               fig.savefig(savepath,format='png')
               plt.close('all')
            except:
               plt.close('all')
               pass
      try:
         del data_path,dl_folder,filename,data,fig,ax
      except:
         continue

   window.after(100,autoprocess)
   return

def main():
   while True:
      if run:
         if not connected_to_internet(timeout=1):
            if (round(time(),0) - ConnnectedToInternetTime >= 1000) or (round(time(),0) - ConnnectedToInternetTime <= 5):
               print('Not connected to internet')
            return

         # Check if data folder exists
         if not os.path.isdir(data_folder_path):
            print('Directory "Data" does not exist in current directory. Creating Directory.')
            os.mkdir(path=data_folder_path)
            os.mkdir(path=temp_folder)

         # Check if websites.csv exists
         if not os.path.isfile(websites_csv_path):
            exit('Necessary file "websites.csv" does not exist in current directory. Exiting Program.')
         else:
         # Read in the csv with websites and info
            try:
               df = read_csv(websites_csv_path,header=0)
               df = df.reset_index(drop=True)
            except:
               exit('Failed to open websites.csv. Exiting Program.')

         # Iterate over rows of websites.csv
         for idx,info in df.iterrows():

            title = re.sub('[^0-9a-zA-Z._:/\\\]+', '', info[0].replace(' ','_')).replace('__','_')
            df.iloc[idx,0] = title
            
            dl_folder = os.path.join(data_folder_path,title)  

            if (info[4] == 'empty') or (not os.path.isdir(dl_folder)):
               try:
                  if not os.path.isdir(dl_folder):
                     os.mkdir(dl_folder)
                  filepath = download_url(url=info[1],save_path=dl_folder,type=info[2])
                  df.iloc[idx,4] = filepath
               except:
                  pass

            # Check if enough time has passed
            if ((round(time(),0) - info[3]) >= 100):
               df.iloc[idx,3] = int(time()) 

               if (info[4] != 'empty') and ((os.path.isfile(info[4])) or (os.path.isdir(info[4]))):
                  try:
                     #Download data to temp folder using url, return temp filepath and name of file
                     new_filepath = download_url(url=info[1],save_path=temp_folder,type=info[2])
                     old_filepath = info[4]

                     #Check to see if files are the same
                     if (info[2] == 'zip'):
                        same_file = cmpfiles(a=new_filepath,b=old_filepath,shallow=False)
                     else:
                        same_file = cmp(f1=new_filepath,f2=old_filepath,shallow=False)

                     #If files are the same, clear temp folder
                     if same_file:
                        clear_temp()

                     #If files are different, move new file in temp to overwrite old file
                     #clear temp folder, delete old data folder, and process new data
                     elif not same_file:
                        move(src=new_filepath,dst=old_filepath)
                        clear_temp()

                        filename = os.path.basename(old_filepath)
                        data_folder = os.path.join(dl_folder,(filename.split(sep='.')[0] + '_Data'))
                        rmtree(path=data_folder)
                  except:
                     pass

            try:
               clear_temp()
            except:
               pass
         
         # 3. Check to see if user asked for entry to be deleted <- Not sure if this will get implemented

         # 4. Overwrite file 
         df.to_csv(websites_csv_path,index=False)

      elif not run:
         print('exititng main thread')
         break

      else:
         print('how did you get here?\nGonna exit the program')
         sleep(0.5)
         exit('Exiting')

   global stopped 
   stopped = True

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
start_label.config(state= DISABLED)

start_button = Button(canvas, text="Start", command=on_start, padx=6,pady=5,highlightthickness=0)
start_button.place(relx=0.75, rely=0.4, anchor=CENTER)

end_label = Text(canvas,wrap=WORD,width=30,height=2,padx=6,pady=5,highlightthickness=0)
end_label.tag_configure('center',justify='center')  
end_label.insert('1.0','When pressed, this button will end the loop')
end_label.tag_add('center',1.0,'end')
end_label.place(relx = 0.3, rely = 0.6,anchor=CENTER)
end_label.config(state= DISABLED)

end_button = Button(canvas, text="Stop", command=on_stop,padx=6,pady=5,highlightthickness=0)
end_button.place(relx=0.75,rely=0.6,anchor=CENTER)

info_label = Text(canvas,wrap=WORD,width=30,height=5,padx=6,pady=5,highlightthickness=0)
info_label.tag_configure('center',justify='center')  
info_label.insert('1.0','''This rudimentary GUI controls the script. 
New buttons and features may be added later if I can make it work''')
info_label.tag_add('center',1.0,'end')
info_label.place(relx=0.5, rely = 0.15,anchor=CENTER)
info_label.config(state= DISABLED)

resized_img = Image.open(os.path.join(sys_path,'Resources','UT_logo.png')).resize((130,100),Image.LANCZOS);
img = ImageTk.PhotoImage(resized_img)
canvas.create_image(350,260,image=img)

who_made_this = Text(canvas,wrap=WORD,width=35,height=3,padx=6,pady=5,highlightthickness=0)
who_made_this.tag_configure('center',justify='center')  
who_made_this.insert('1.0','''This program was made by Collin Dobson for the UTORII SMaRT internship''')
who_made_this.tag_add('center',1.0,'end')
who_made_this.place(relx=0.35,rely = 0.85,anchor=CENTER)
who_made_this.config(state= DISABLED)

window.after(100,autoprocess)

window.mainloop()

if stopped:
   print('successfully exited program')