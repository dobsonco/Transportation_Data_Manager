# This is the repository my Transportation Data Manager
The purpose of this repository is to be a place to store the code for my program in case of my laptop dying.

# Very Important Note:
__This code does not run on Windows. I will likely try to make it work, but idk__

## Who wrote this code?:
I, that being Collin Dobson wrote this. This is my first shot at making a GUI/app, which will hopefully justify any gripes you may have with my code. 

## What is the purpose?:
The purpose is to maintain an active/up to date catalog of data from a list of databases. You can pretty much just turn this program on and leave it running on a machine in the corner as long as you want. The program will check to see if enough time has past for each link. If that is the case, then the program will check the site to see if new data has been uploaded. If it has, then the program will download the file to a temp folder in Data, and then it will move it to a folder with the name of the website it came from. 

## How to use:
__See SETUP.txt for insructions to get this working__
Try not to just hit the 'x' button on the GUI, that could corrupt websites.csv, which will basically brick the script. If you want to hit the 'x' button, make sure you hit the 'stop' button first. As of right now, if you want to add new websites to the csv use edit_websites_csv.ipynb. It will take a list of tuples containing a name in slot 0, a link in slot 1, and the type (the file extension e.g. 'csv' or 'zip') in slot 2. Make sure the link is a link to a download, otherwise this won't work.
