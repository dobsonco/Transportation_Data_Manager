from requests import head,get
from pandas import read_csv
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
from re import sub
from gc import collect

################# Horrible Mess of Global Variables #################
sys_path = path[0]

websites_csv_path = os.path.join(sys_path,'websites.csv')

data_folder_path = os.path.join(sys_path,'Data')

temp_folder = os.path.join(data_folder_path,'temp')

global CheckAgain
CheckAgain = int(time() + 1000)

global run
run = False

global stopped
stopped = True

global autoprocess_running
autoprocess_running = False

################# Horrible Mess of Functions #################
class CoreUtils():
   def connected_to_internet(url='http://www.google.com/',timeout=5):
      '''
      Does what it says, returns true if connected to internet, else returns false.
      '''
      try:
         _ = head(url,timeout=timeout)
         return True
      except:
         return False

   def download_url(url,save_path,chunk_size=1024,type='csv'):
      '''
      Save path is just the folder you want to download it in.

      Type must be a string, with the type of file you're downloading.

      returns name of new file and its filepath. If downloaded is a zip, it will extract it and then 
      return the path to the folder along with the name of the folder.
      '''

      files_in_directory = len(next(os.walk(save_path),(None, None, []))[2])
      dir_name = os.path.basename(save_path)
      num_ = len([i for i,j in enumerate(dir_name) if j == '_'])
      filename = '_'.join(dir_name.split(sep='_')[0:round(num_/2)])+'-'+str(files_in_directory)+'.'+type
      filepath = os.path.join(save_path,filename)
      del files_in_directory,dir_name,num_,filename

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
            filepath = max(glob(os.path.join(save_path,'*/')),key=os.path.getmtime)
            try:
               del zObject
            except:
               pass
      except:
         raise ValueError
      return filepath

   def clear_temp(dir=temp_folder):
      '''
      Clears all files and directories from temp folder, can be used on other folders.
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
         del file_path
         return

   def check_internet_and_wait():
      global CheckAgain
      if (abs(CheckAgain-time()) >= 10):
         CheckAgain = time()
         connected = CoreUtils.connected_to_internet(timeout=5)
         was_diconnected = False
         if not connected:
            start = time()
            was_diconnected = True
            print('Not connected to internet')
            while not connected:
               sleep(1)
               connected = CoreUtils.connected_to_internet()
            print('Connected to internet')
            end = time()
         if was_diconnected:
            print(f'Time disconnected: {end-start}s')  
            del connected,was_diconnected,end,start

   def check_size(filepath,exp,ceiling=1):
      size = os.path.getsize(filepath)
      rel_size = size/(1024**exp)
      if (rel_size > ceiling):
         del size,rel_size
         return False
      elif (rel_size <= ceiling):
         del size,rel_size
         return True
      else:
         raise ValueError

def autoprocess():
   '''
   Horrible Mess of a Function Held together by spit and duct tape

   Call this function to process any and all csv's in the data folder
   No inputs are required to make this work
   '''
   global autoprocess_running
   global window

   if autoprocess_running:
      window.after(ms=45000,func=autoprocess)
      return
   
   if not run:
      window.after(ms=45000,func=autoprocess)
      return
   
   autoprocess_running = True

   to_process = []
   to_process = glob(data_folder_path+'/*/*.csv')

   for i,vals in enumerate(to_process):
      data_path = vals
      dl_folder = data_path[0:(len(data_path)-(len(os.path.basename(data_path))))]
      filename = os.path.basename(data_path).split(sep='.')[0]
      data_folder = os.path.join(dl_folder,(filename.split(sep='.')[0] +'_Data'))
      histogram_path = os.path.join(data_folder,'Hist')
      plots_path = os.path.join(data_folder,'Plots')

      try:
         data = read_csv(data_path,low_memory=False)
      except:
         if os.path.isdir(dl_folder):
            del data_path,dl_folder,filename,data_folder,histogram_path,plots_path
            continue
         else: 
            os.mkdir(data_folder)
         failed_to_process = open(os.path.join(data_folder,'failed_to_process.txt'),'a')
         e = datetime.now()
         failed_to_process.write(f'{filename} failed to open on {str(e.year)}, {str(e.month)}, {str(e.day)}\n')
         failed_to_process.close()
         del data_folder,e,filename,dl_folder,data_path,histogram_path,plots_path
         continue

      if not os.path.isdir(data_folder):
         os.mkdir(data_folder)
         os.mkdir(histogram_path)
         os.mkdir(plots_path)

      for j,col in enumerate(data):
         if (data.dtypes[j] != 'object') and (data.dtypes[j] != 'bool'):
            try:            
               fig,ax = plt.subplots(nrows=1,ncols=1,figsize=(8,8))
               plt.switch_backend('agg')
               ax.hist(array(data[col]))
               ax.set_xlabel(col)
               ax.set_title('Autogenerated Histogram '+str(j+1))
               ax.set_facecolor('#ADD8E6')
               ax.set_axisbelow(True)
               ax.yaxis.grid(color='white', linestyle='-')
               savepath = os.path.join(histogram_path,(filename+'_Hist-'+str(j+1)+'.png'))
               fig.savefig(savepath,format='png')
               del savepath
               plt.cla()
               plt.clf()
               plt.close('all')
            except:
               plt.cla()
               plt.clf()
               plt.close('all')

            try:            
               fig,ax = plt.subplots(nrows=1,ncols=1,figsize=(8,8))
               plt.switch_backend('agg')
               ax.plot([idx+1 for idx,j in enumerate(data[col])],array(data[col]))
               ax.set_xlabel(col)
               ax.set_title('Autogenerated Plot '+str(j+1))
               ax.set_facecolor('#ADD8E6')
               ax.set_axisbelow(True)
               ax.yaxis.grid(color='white', linestyle='-')
               ax.xaxis.grid(color='white', linestyle='-')
               savepath = os.path.join(plots_path,(filename+'_Plot-'+str(j+1)+'.png'))
               fig.savefig(savepath,format='png')
               del savepath
               plt.cla()
               plt.clf()
               plt.close('all')
            except:
               plt.cla()
               plt.clf()
               plt.close('all')

      try:
         del data,data_path,dl_folder,filename,data,histogram_path,plots_path,fig,ax
      except:
         continue

   del to_process
   autoprocess_running = False
      
   collect()
   window.after(ms=45000,func=autoprocess)
   return

def main():
   '''
   So basically this runs on a thread and will only actually run after you press start on the GUI.

   This is the core loop that handles the data and determines where data goes. Reads websites.csv, 
   so try not to mess anything up. Use edit_websites_csv.ipynb to add entries to the csv. If you want to 
   remove an entry, you can just delete the line.
   '''
   sleep(0.3)
   print('Main thread started')
   while True:
      if not run:
         print('Exititng main thread')
         break

      elif (not run) and (run):
         print('How did you get here?\nGonna exit the program')
         sleep(0.5)
         exit('Exiting, something really bad happened.')
   
      global stopped
      stopped = False

      # Check if internet is connected, if not connected then wait till it is
      CoreUtils.check_internet_and_wait()

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

         title = sub('[^0-9a-zA-Z._:/\\\]+','',info[0].replace(' ','_')).replace('__','_')
         df.iloc[idx,0] = title
         
         dl_folder = os.path.join(data_folder_path,title)
         del title

         # If theres no path or the data directory does not exist, download it
         if (info[4]=='empty') or (not os.path.isdir(dl_folder)):
            try:
               if not os.path.isdir(dl_folder):
                  os.mkdir(dl_folder)
               filepath = CoreUtils.download_url(url=info[1],save_path=dl_folder,type=info[2])
               df.iloc[idx,4] = filepath
               del filepath
            except:
               pass

         # Check if enough time has passed
         if ((round(time(),0) - info[3]) >= 1000):
            df.iloc[idx,3] = int(time()) 

            if (info[4]!='empty') and ((os.path.isfile(info[4])) or (os.path.isdir(info[4]))):
               try:
                  # Download data to temp folder using url, return temp filepath
                  new_filepath = CoreUtils.download_url(url=info[1],save_path=temp_folder,type=info[2])
                  old_filepath = info[4]

                  # Check to see if files are the same
                  if (info[2] == 'zip'):
                     same_file = cmpfiles(a=new_filepath,b=old_filepath,shallow=False)
                  else:
                     same_file = cmp(f1=new_filepath,f2=old_filepath,shallow=False)

                  # If files are the same, clear temp folder
                  if same_file:
                     CoreUtils.clear_temp()

                  # If files are different, move new file in temp to overwrite old file
                  # clear temp folder, delete old data folder, and process new data
                  elif not same_file:
                     # Check to see if old path is a file or directory
                     if os.path.isdir(old_filepath):
                        rmtree(old_filepath)
                     elif os.path.isfile(old_filepath):
                        os.unlink(old_filepath)
                     # Move file from temp to corresponding data folder
                     move(src=new_filepath,dst=old_filepath)
                     CoreUtils.clear_temp()
                     # Delete old figures directory so that autoprocess can process it
                     filename = os.path.basename(old_filepath)
                     data_folder = os.path.join(dl_folder,(filename.split(sep='.')[0]+'_Data'))
                     rmtree(path=data_folder)
                     del same_file,data_folder,new_filepath,old_filepath
               except:
                  pass

         try:
            CoreUtils.clear_temp()
         except:
            pass
      
      # 3. Check to see if user asked for entry to be deleted <- Not sure if this will get implemented

      # 4. Overwrite file
      df.to_csv(websites_csv_path,index=False)
      del df

      sleep(0.1)

   stopped = True

################# GUI Window #################
class GUI(Tk):
   def __init__(self):
      super().__init__()

      self.protocol("WM_DELETE_WINDOW",self.on_x)

      self.title('Transportation Data Manager')
      self.iconphoto(False,ImageTk.PhotoImage(file=os.path.join(sys_path,'Resources','road-210913_1280.jpg'),format='jpg'))

      self.frame = Frame(self)
      self.frame.pack()

      self.canvas = Canvas(self.frame, width=425, height=300, bg='#D3D3D3')
      self.canvas.pack()

      self.start_label = Text(self.canvas,wrap=WORD,width=30,height=2,padx=6,pady=5,highlightthickness=0)
      self.start_label.tag_configure('center',justify='center')  
      self.start_label.insert('1.0','When pressed, this button will start the loop')
      self.start_label.tag_add('center',1.0,'end')
      self.start_label.place(relx = 0.35, rely = 0.4,anchor=CENTER)
      self.start_label.config(state= DISABLED)

      self.start_button = Button(self.canvas,text="Start",command=self.on_start,padx=6,pady=5,highlightthickness=0)
      self.start_button.place(relx=0.8,rely=0.4,anchor=CENTER)

      self.end_label = Text(self.canvas,wrap=WORD,width=30,height=2,padx=6,pady=5,highlightthickness=0)
      self.end_label.tag_configure('center',justify='center')  
      self.end_label.insert('1.0','When pressed, this button will end the loop')
      self.end_label.tag_add('center',1.0,'end')
      self.end_label.place(relx = 0.35, rely = 0.6,anchor=CENTER)
      self.end_label.config(state=DISABLED)

      self.end_button = Button(self.canvas,text="Stop",command=self.on_stop,padx=6,pady=5,highlightthickness=0)
      self.end_button.place(relx=0.8,rely=0.6,anchor=CENTER)

      self.info_label = Text(self.canvas,wrap=WORD,width=30,height=4,padx=6,pady=5,highlightthickness=0)
      self.info_label.tag_configure('center',justify='center')  
      self.info_label.insert('1.0','''This rudimentary GUI controls the script. New buttons and features may be added later if I can make it work''')
      self.info_label.tag_add('center',1.0,'end')
      self.info_label.place(relx=0.5, rely = 0.15,anchor=CENTER)
      self.info_label.config(state=DISABLED)

      self.resized_img = Image.open(os.path.join(sys_path,'Resources','UT_logo.png')).resize((130,100),Image.LANCZOS);
      self.img = ImageTk.PhotoImage(self.resized_img)
      self.canvas.create_image(375,260,image=self.img)

      self.who_made_this = Text(self.canvas,wrap=WORD,width=35,height=3,padx=6,pady=5,highlightthickness=0)
      self.who_made_this.tag_configure('center',justify='center')  
      self.who_made_this.insert('1.0','''This program was made by Collin Dobson for the UTORII SMaRT internship''')
      self.who_made_this.tag_add('center',1.0,'end')
      self.who_made_this.place(relx=0.399,rely = 0.85,anchor=CENTER)
      self.who_made_this.config(state=DISABLED)

      self.after(ms=10000,func=autoprocess)

   def switch(self):
      '''
      Toggles the buttons on the the GUI, because of the multithreading, make sure to not change this.
      '''
      if (self.start_button["state"] == "normal") and (self.end_button["state"] == "normal") and (run == False):
         self.start_button["state"] = "normal"
         self.end_button["state"] = "disabled"
      elif self.start_button["state"] == "normal":
         self.start_button["state"] = "disabled"
         self.end_button["state"] = "normal"
      elif (self.start_button["state"] != "normal"):
         self.start_button["state"] = "normal"
         self.end_button["state"] = "disabled"

   def on_start(self):
      '''
      This mess of a function starts the manin thread.
      '''
      global stopped
      global run
      global ConnectedToInternetTimer
      global main_thread

      if (not stopped):
         return

      run = True
      ConnnectedToInternetTime = round(time(),0)
      stopped = False
      main_thread = Thread(target=main).start()
      print('Starting main thread')
      self.switch()

   def on_stop(self):
      global run
      '''
      This function stops the main thread.
      '''
      if run == False:
         self.switch()
         return
      
      run = False
      print('Waiting for main thread to reach stopping point')
      self.switch()
   
   def on_x(self):
      global run
      global stopped
      stopped = False
      run = False
      self.destroy()

window = GUI()
window.mainloop()

while True: 
   sleep(0.1) 
   if stopped:
      del window
      exit('Successfully exited program') 