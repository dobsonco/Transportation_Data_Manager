from requests import head,get
from pandas import read_csv
from time import time,sleep,localtime
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
from random import choice
from datetime import datetime
from tzlocal import get_localzone
from pandastable import Table

################# Horrible Mess of Global Variables #################
sys_path = path[0]

websites_csv_path = os.path.join(sys_path,'websites.csv')

data_folder_path = os.path.join(sys_path,'Data')

temp_folder = os.path.join(data_folder_path,'temp')

################# Core Functions #################
class CoreUtils(object):
   def __init__(self):
      self.run = False
      self.stopped = True
      self.CheckAgain = int(time() + 1000)
   
   def destroy(self):
      del self

   def set_run(self):
      self.run = True

   def stop_run(self):
      self.run = False

   def set_stopped(self):
      self.stopped = False

   def connected_to_internet(self,timeout: int = 5) -> bool:
      '''
      Does what it says, returns true if connected to internet, else returns false.
      '''
      options = ['http://www.google.com/','https://www.wikipedia.org/','https://github.com/']
      url = choice(options)
      try:
         _ = head(url,timeout=timeout)
         return True
      except:
         return False

   def download_url(self,url: str,save_path: str,chunk_size = 1024,type: str ='csv') -> str:
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
         for chunk in r.iter_content(chunk_size=int((chunk_size))):
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

   def clear_temp(self,dir: str = temp_folder) -> None:
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
      del filename
      return

   def check_internet_and_wait(self) -> bool:
      '''
      This function basically just pings websites until it gets a response, if no response
      it will enter a loop where it checks again once a second, once it connectes it will
      return False. If the user clicks the stop button, it will return true if it is
      looping
      '''
      if (abs(self.CheckAgain-time()) >= 5):
         self.CheckAgain = time()
         connected = self.connected_to_internet(timeout=5)
         was_diconnected = False
         if not connected:
            start = time()
            was_diconnected = True
            print('Not connected to internet')
            while not connected:
               sleep(1)
               connected = self.connected_to_internet()
               if not self.run:
                  return True
            print('Connected to internet')
            end = time()
         if was_diconnected:
            print(f'Time disconnected: {end-start}s')
            del connected,was_diconnected,end,start
      return False

   def check_size(self,filepath: str,exp: int = 3,ceiling: int = 1) -> bool:
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
      
   def main(self) -> None:
      '''
      So basically this runs on a thread and will only actually run after you press start on the GUI.

      This is the core loop that handles the data and determines where data goes. Reads websites.csv,
      so try not to mess anything up. Use edit_websites_csv.ipynb to add entries to the csv. If you want to
      remove an entry, you can just delete the line.
      '''
      sleep(0.1)
      print('Main thread started')

      while True:

         if (not self.run) or (self.check_internet_and_wait()):
            sleep(0.1)
            print('Exititng main thread')
            break

         # Check if websites.csv exists
         if not os.path.isfile(websites_csv_path):
            self.run = False
            window.on_stop()
            print('Necessary file "websites.csv" does not exist in current directory. Exiting main thread.')
            continue

         # Check if data folder exists
         if not os.path.isdir(data_folder_path):
            print('Directory "Data" does not exist in current directory. Creating Directory.')
            os.mkdir(path=data_folder_path)
            os.mkdir(path=temp_folder)

         # Read in the csv with websites and info
         try:
            df = read_csv(websites_csv_path,header=0)
            df = df.reset_index(drop=True)
            df_changed = False
            self.stopped = False
         except:
            self.run = False
            window.on_stop()
            print('Failed to open websites.csv, exiting main thread')
            continue

         # Iterate over rows of websites.csv
         for idx,info in df.iterrows():

            name = info[0]
            url = info[1]
            dtype = info[2]
            last_checked = info[3]
            dpath = info[4]

            if not self.run:
               df_changed = False
               df.to_csv(websites_csv_path,index=False)
               del df
               break

            title = sub('[^0-9a-zA-Z._:/\\\]+','',name.replace(' ','_')).replace('__','_')
            if name != title:
               df_changed = True
               df.iloc[idx,0] = title

            dl_folder = os.path.join(data_folder_path,title)
            del title

            # If theres no path download it
            if ((dpath=='empty')):
               try:
                  if not os.path.isdir(dl_folder):
                     os.mkdir(dl_folder)
                  filepath = self.download_url(url=url,save_path=dl_folder,type=dtype)
                  df.iloc[idx,4] = filepath
                  df.iloc[idx,3] = int(time())
                  del filepath
                  df_changed = True
               except:
                  pass
               continue

            # Check if enough time has passed
            if (abs(round(time()) - last_checked) >= 10000):
               df.iloc[idx,3] = int(time())
               df_changed = True

               if (dpath!='empty') and ((os.path.isfile(dpath)) or (os.path.isdir(dpath))):
                  try:
                     # Download data to temp folder using url, return temp filepath
                     new_filepath = self.download_url(url=url,save_path=temp_folder,type=dtype)
                     old_filepath = dpath

                     # Check to see if files are the same
                     if (dtype == 'zip'):
                        same_file = cmpfiles(a=temp_folder,b=old_filepath,shallow=False)
                     else:
                        same_file = cmp(f1=new_filepath,f2=old_filepath,shallow=False)

                     # If files are the same, clear temp folder
                     if same_file:
                        self.clear_temp()

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
                        self.clear_temp()
                        # Delete old figures directory so that autoprocess can process it
                        filename = os.path.basename(old_filepath)
                        data_folder = os.path.join(dl_folder,(filename.split(sep='.')[0]+'_Data'))
                        rmtree(path=data_folder)
                        del same_file,data_folder,new_filepath,old_filepath
                        df_changed = True
                  except:
                     pass
                  try:
                     self.clear_temp()
                  except:
                     pass

         try:
            self.clear_temp()
         except:
            pass

         # 3. Check to see if user asked for entry to be deleted <- Not sure if this will get implemented

         # 4. Overwrite file
         try:
            if df_changed:
               df.to_csv(websites_csv_path,index=False)
            del df
         except:
            pass

         sleep(0.2)

      print("Exited main thread")
      self.stopped = True

   def autoprocess(self) -> None:
      '''
      Horrible Mess of a Function Held together by spit and duct tape

      Call this function to process any and all csv's in the data folder
      No inputs are required to make this work
      '''
      global window

      if (not self.run):
         window.queue_autoprocess()
         return
      
      all_dls = []
      all_dls = list(read_csv(filepath_or_buffer=websites_csv_path,usecols=['path']).iloc[:,0])

      if (len(all_dls) <= 0):
         del all_dls
         return

      all_csv = []
      all_csv = [csv for csv in all_dls if '.csv' in csv]

      to_process = []
      for csv in all_csv:
         if not self.check_size(filepath=csv,exp=3,ceiling=0.5):
            continue
         dl_folder = csv[0:(len(csv)-(len(os.path.basename(csv))))]
         filename = os.path.basename(csv).split(sep='.')[0]
         data_folder = os.path.join(dl_folder,(filename.split(sep='.')[0] +'_Data'))
         a = len(dl_folder)
         b = len(temp_folder)
         if a >= b:
            upper = b
         else:
            upper = a
         if os.path.isdir(data_folder) or (dl_folder[0:upper] == temp_folder[0:upper]):
            del dl_folder,filename,data_folder,a,b,upper
            continue
         to_process.append((csv,data_folder,filename))
         del dl_folder
         if len(to_process) >= 5:
            del filename,data_folder,a,b,upper
            break

      while len(to_process) > 0:
         vals = to_process.pop()

         if not self.run:
            window.queue_autoprocess()
            del to_process
            return

         csv_path = vals[0]
         data_folder = vals[1]
         filename = vals[2]
         histogram_path = os.path.join(data_folder,'Hist')
         plots_path = os.path.join(data_folder,'Plots')

         try:
            data = read_csv(csv_path,low_memory=False)
         except:
            os.mkdir(data_folder)
            failed_to_process = open(os.path.join(data_folder,'failed_to_process.txt'),'a')
            e = datetime.now()
            failed_to_process.write(f'{filename} failed to open on {str(e.year)}, {str(e.month)}, {str(e.day)}\n')
            failed_to_process.close()
            del data_folder,e,filename,csv_path,histogram_path,plots_path
            continue

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
            del data,csv_path,filename,data,histogram_path,plots_path,fig,ax
         except:
            continue
      
      del all_csv
      collect()
      window.queue_autoprocess()
      return

################# GUI Window #################
class GUI(Tk):
   def __init__(self) -> Tk:
      super().__init__()

      self.protocol("WM_DELETE_WINDOW",self.on_x)

      self.title('Transportation Data Manager')
      self.iconphoto(False,ImageTk.PhotoImage(file=os.path.join(sys_path,'Resources','road-210913_1280.jpg'),format='jpg'))

      self.frame = Frame(self)
      self.frame.pack()

      self.canvas = Canvas(self.frame, width=425, height=400, bg='#D3D3D3')
      self.canvas.pack()

      self.start_label = Text(self.canvas,wrap=WORD,width=30,height=2,padx=6,pady=5,highlightthickness=0)
      self.start_label.tag_configure('center',justify='center')
      self.start_label.insert('1.0','When pressed, this button will start the loop')
      self.start_label.tag_add('center',1.0,'end')
      self.start_label.place(relx = 0.35, rely = 0.33,anchor=CENTER)
      self.start_label.config(state= DISABLED)

      self.start_button = Button(self.canvas,text="    Start    ",command=self.on_start,padx=6,pady=5,highlightthickness=0)
      self.start_button.place(relx=0.8,rely=0.33,anchor=CENTER)

      self.end_label = Text(self.canvas,wrap=WORD,width=30,height=2,padx=6,pady=5,highlightthickness=0)
      self.end_label.tag_configure('center',justify='center')
      self.end_label.insert('1.0','When pressed, this button will end the loop')
      self.end_label.tag_add('center',1.0,'end')
      self.end_label.place(relx = 0.35, rely = 0.5,anchor=CENTER)
      self.end_label.config(state=DISABLED)

      self.end_button = Button(self.canvas,text="    Stop    ",command=self.on_stop,padx=6,pady=5,highlightthickness=0)
      self.end_button.place(relx=0.8,rely=0.5,anchor=CENTER)

      self.monitor_label = Text(self.canvas,wrap=WORD,width=30,height=3,padx=6,pady=5,highlightthickness=0)
      self.monitor_label.tag_configure('center',justify='center')
      self.monitor_label.insert('1.0','This button will create a window with the current spreadsheet')
      self.monitor_label.tag_add('center',1.0,'end')
      self.monitor_label.place(relx = 0.35, rely = 0.67,anchor=CENTER)
      self.monitor_label.config(state=DISABLED)

      self.monitor_button = Button(self.canvas,text="Spreadsheet",command=self.create_monitor,padx=6,pady=5,highlightthickness=0)
      self.monitor_button.place(relx=0.8,rely=0.67,anchor=CENTER)

      self.info_label = Text(self.canvas,wrap=WORD,width=30,height=4,padx=6,pady=5,highlightthickness=0)
      self.info_label.tag_configure('center',justify='center')
      self.info_label.insert('1.0','''This rudimentary GUI controls the script. New buttons and features may be added later if I can make it work''')
      self.info_label.tag_add('center',1.0,'end')
      self.info_label.place(relx=0.5, rely = 0.12,anchor=CENTER)
      self.info_label.config(state=DISABLED)

      self.resized_img = Image.open(os.path.join(sys_path,'Resources','UT_logo.png')).resize((130,100),Image.LANCZOS);
      self.img = ImageTk.PhotoImage(self.resized_img)
      self.canvas.create_image(375,360,image=self.img)

      self.who_made_this = Text(self.canvas,wrap=WORD,width=35,height=3,padx=6,pady=5,highlightthickness=0)
      self.who_made_this.tag_configure('center',justify='center')
      self.who_made_this.insert('1.0','''This program was made by Collin Dobson for the UTORII SMaRT internship''')
      self.who_made_this.tag_add('center',1.0,'end')
      self.who_made_this.place(relx=0.399,rely = 0.9,anchor=CENTER)
      self.who_made_this.config(state=DISABLED)

      self.after(ms=10000,func=process.autoprocess)

   def create_monitor(self):
      self.monitor = Toplevel(master=self,bg='#D3D3D3')
      self.monitor.geometry('1000x400')
      self.monitor.protocol("WM_DELETE_WINDOW",self.delete_monitor)
      self.monitor.iconphoto(False,ImageTk.PhotoImage(file=os.path.join(sys_path,'Resources','road-210913_1280.jpg'),format='jpg'))
      self.monitor.title('Websites.csv')
      self.monitor_button['state'] = 'disabled'

      self.f = Frame(self.monitor,height=1000,width=1600,bg='#D3D3D3')
      self.f.pack(fill=BOTH,expand=1)
      data = read_csv(websites_csv_path,header=0)
      tz = get_localzone()
      data.iloc[:,3] = [datetime.fromtimestamp(unix_timestamp, tz).strftime("%D %H:%M") for unix_timestamp in data.iloc[:,3]]
      self.pt = Table(self.f,dataframe=data,showtoolbar=False,showstatusbar=False)
      self.pt.show()

      self.monitor.after(ms=10000,func=self.update_monitor)

   def update_monitor(self):
      data = read_csv(websites_csv_path,header=0)
      tz = get_localzone()
      data.iloc[:,3] = [datetime.fromtimestamp(unix_timestamp, tz).strftime("%D %H:%M") for unix_timestamp in data.iloc[:,3]]
      self.pt.model.df = data
      self.pt.redraw()
      self.monitor.after(5000,self.update_monitor)

   def delete_monitor(self):
      self.monitor.destroy()
      self.monitor_button['state'] = 'normal'

   def switch(self) -> None:
      '''
      Toggles the buttons on the the GUI, because of the multithreading, make sure to not change this.
      '''
      if (self.start_button["state"] == "normal") and (self.end_button["state"] == "normal") and (process.run == False):
         self.start_button["state"] = "normal"
         self.end_button["state"] = "disabled"
      elif self.start_button["state"] == "normal":
         self.start_button["state"] = "disabled"
         self.end_button["state"] = "normal"
      elif (self.start_button["state"] != "normal"):
         self.start_button["state"] = "normal"
         self.end_button["state"] = "disabled"

   def on_start(self) -> None:
      '''
      This mess of a function starts the manin thread.
      '''
      global ConnectedToInternetTimer
      global main_thread

      if (not process.stopped):
         return

      process.set_run()
      ConnnectedToInternetTime = round(time(),0)
      process.set_stopped()
      main_thread = Thread(target=process.main).start()
      print('Starting main thread')
      self.switch()

   def on_stop(self) -> None:
      '''
      This function stops the main thread.
      '''
      if not process.run:
         self.switch()
         return
      print('Waiting for main thread to reach stopping point')
      process.stop_run()
      self.switch()

   def on_x(self) -> None:
      if process.run:
         print('Waiting for main thread to reach stopping point')
      process.stop_run()
      self.destroy()

   def queue_autoprocess(self,ms=5000) -> None:
      self.after(ms=ms,func=process.autoprocess)

process = CoreUtils()
window = GUI()
window.mainloop()

while True:
   sleep(0.1)
   if process.stopped:
      del window
      del process
      exit('Successfully exited program')