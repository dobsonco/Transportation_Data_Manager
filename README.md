# This is the repository of my Transportation Data Manager
The purpose of this repository is to be a place to store the code for my program in case of my laptop dying.

## Who wrote this code?:
I, that being Collin Dobson wrote this. This is my first shot at making a GUI/app, which will hopefully justify any gripes you may have with my code. 

## What is the purpose?:
The purpose is to maintain an active/up to date catalog of data from a list of databases. You can pretty much just turn this program on and leave it running on a machine in the corner as long as you want. The program will check to see if enough time has past for each link or if the entry has 'empty' for the path. If that is the case, then the program will check the site to see if new data has been uploaded. If it has, then the program will download the file to a temp folder in Data, and then it will move it to a folder with the name of the website it came from. 

## How to use:
__See SETUP.txt for insructions to get this working__
Just run the program using your python interpreter and use the interface to start and stop the program, there is a third button that will create a window with the current websites.csv. In this version it is safe to press start and then close the window, this will set a flag that will stop it on the next loop. The version I used to make this is 3.9.16, so it likely wont work if you change the version (I have not tested this). If you want to add new websites to the csv use edit_websites_csv.ipynb or the add entry button on the main script. It will take a list of tuples containing a name in slot 0, a link in slot 1, and the type (the file extension e.g. 'csv' or 'zip') in slot 2. Make sure the link is a download, otherwise this won't work.

## Documentation:
__Read Documentation.txt__
