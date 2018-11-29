# -*- coding: utf-8 -*-
"""
Created on Mon May  7 22:26:11 2018

@author: Pablo
"""
from glob2 import glob
import os
import requests
from bs4 import BeautifulSoup
from zipfile import ZipFile
from numpy import zeros, uint8
from cv2 import imread, imwrite
from wand.image import Image
from win32api import SetFileAttributes
#from pdb import set_trace as STOP

# Delete folder '__pycache__' if exists
pycache_path = 'C:/Users/Pablo/Videos/PELIS/__pycache__/'
if glob('C:/Users/Pablo/Videos/PELIS/__pycache__/'):
    for elem in os.listdir(pycache_path):
        os.remove(pycache_path + elem)
    os.rmdir(pycache_path)

# Change folder name
folders = ['C:/Users/Pablo/Videos/PELIS/', 'C:/Users/Pablo/Videos/PELIS/(VISTAS)/']
errorList = []
subtLink = 'http://www.yifysubtitles.com/movie-imdb/'
for folder in folders:
    allDirs = [x for x in os.listdir(folder)[1:] if os.path.isdir(folder + x)] # First folder is '(VISTAS)', exclude it
    for thisDir in allDirs:
        oldname = folder + thisDir
        newname = oldname.replace(' [YTS.AG]', '').replace(' [YTS.AM]', '').replace(' [720p]', '')
        newname = newname.replace(' [1080p]', '').replace(' [BluRay]', '').replace(' [WEBRip]', '')
        if oldname != newname:
            os.rename(oldname, newname)

# Download JPG, create PNG, delete YTS picture, create ICO file and set folder icon
for folder in folders:
    allDirs = [x for x in os.listdir(folder)[1:] if os.path.isdir(folder + x)] # First folder is '(VISTAS)', exclude it
    for thisDir in allDirs:
        currentFolder = folder + thisDir + '/'
        
        # Get YTS.ag web and image link. 'imageLink' example: turn 'Batman: Returns (2017)' into 'batman_returns_2017'
        webLink = thisDir.replace('.','').replace(':','').replace('(','').replace(')','').replace("'",'')
        imgLinkOld = webLink.replace(' ','_') # old movies don't have the img link in lower case
        webLink = webLink.lower()
        ytsLink = webLink.replace(' ','-')
        imgLink = webLink.replace(' - ','_').replace(' ','_').replace('-','_')
        
        # Download English subtitle, if it doesn't exist
        if not glob(currentFolder + 'english.srt'):
            subtError = 0
            # Search subtitle link
            try:
                dataWeb = requests.get('https://yts.am/movie/' + ytsLink)
                soup = BeautifulSoup(dataWeb.content, 'html.parser')
                for tag in soup.find_all('a', {'target':'_blank'}):
                    if subtLink in tag['href']:
                        currentSubtLink = tag['href']
                        break
                dataWeb = requests.get(currentSubtLink)
                soup = BeautifulSoup(dataWeb.content, 'html.parser')
            except:
                errorList.append('ERROR OBTAINING SUBTITLE LINK: ' + thisDir)
                subtError = 1
            if subtError==0:
                try:
                    subtFound = False
                    for elem in soup.find_all('tr'):
                        if 'English' in elem.get_text():
                            subtitleLink = 'http://www.yifysubtitles.com' + elem.find('a')['href']
                            subtFound = True
                            break
                    if subtFound:
                        zipLink = subtitleLink.replace('/subtitles/','/subtitle/') + '.zip'
                        r = requests.get(zipLink, allow_redirects=True)
                        open(currentFolder + 'english.zip', 'wb').write(r.content)
                        zip_ref = ZipFile(currentFolder + 'english.zip')
                        oldname = zip_ref.namelist()[0]
                        zip_ref.extractall(currentFolder)
                        zip_ref.close()
                        os.rename(currentFolder + oldname, currentFolder + 'english.srt')
                        os.remove(currentFolder + 'english.zip')
                        print('Subtitle downloaded (English): ' + thisDir)
                    else:
                        errorList.append('SUBTITLE MISSING (English): ' + thisDir)
                except:
                    errorList.append('SUBTITLE DOWNLOAD ERROR (English): ' + thisDir)
        # Download Spanish subtitle, if it doesn't exist
        if not glob(currentFolder + 'spanish.srt'):
            subtError = 0
            # Search subtitle link
            try:
                dataWeb = requests.get('https://yts.am/movie/' + ytsLink)
                soup = BeautifulSoup(dataWeb.content, 'html.parser')
                for tag in soup.find_all('a', {'target':'_blank'}):
                    if subtLink in tag['href']:
                        currentSubtLink = tag['href']
                        break
                dataWeb = requests.get(currentSubtLink)
                soup = BeautifulSoup(dataWeb.content, 'html.parser')
            except:
                errorList.append('ERROR OBTAINING SUBTITLE LINK: ' + thisDir)
                subtError = 1
            if subtError==0:
                try:
                    subtFound = False
                    for elem in soup.find_all('tr'):
                        if 'Spanish' in elem.get_text():
                            subtitleLink = 'http://www.yifysubtitles.com' + elem.find('a')['href']
                            subtFound = True
                            break
                    if subtFound:
                        zipLink = subtitleLink.replace('/subtitles/','/subtitle/') + '.zip'
                        r = requests.get(zipLink, allow_redirects=True)
                        open(currentFolder + 'spanish.zip', 'wb').write(r.content)
                        zip_ref = ZipFile(currentFolder + 'spanish.zip')
                        oldname = zip_ref.namelist()[0]
                        zip_ref.extractall(currentFolder)
                        zip_ref.close()
                        os.rename(currentFolder + oldname, currentFolder + 'spanish.srt')
                        os.remove(currentFolder + 'spanish.zip')
                        print('Subtitle downloaded (Spanish): ' + thisDir)
                    else:
                        errorList.append('SUBTITLE MISSING (Spanish): ' + thisDir)
                except:
                    if thisDir not in errorList[-1]:
                        errorList.append('SUBTITLE DOWNLOAD ERROR (Spanish): ' + thisDir)
            
        # Download JPG picture, if it doesn't exist
        if not glob(currentFolder + 'untitled.jpg'):
            r = requests.get('https://yts.am/assets/images/movies/' + imgLink + '/medium-cover.jpg', allow_redirects=True)
            if r.status_code == 200:
                open(currentFolder + 'untitled.jpg', 'wb').write(r.content)
            else:
                r = requests.get('https://yts.am/assets/images/movies/' + imgLinkOld + '/medium-cover.jpg')
                if r.status_code == 200:
                    open(currentFolder + 'untitled.jpg', 'wb').write(r.content)
                else:
                    errorList.append('IMG LINK ERROR: ' + imgLink)
                
        # Create PNG picture, if it doesn't exist
        if not glob(currentFolder + 'untitled.png'):
            if glob(currentFolder + 'untitled.jpg'):
                IM = imread(currentFolder + 'untitled.jpg')
                nf, nc, _ = IM.shape
                M = zeros((nf,nf,4), dtype=uint8)
                d = (nf-nc)//2
                M[:,d:d+nc,:-1] = IM[:,:,:]
                M[:,d:d+nc,3] = 255 # In the 4th channel, 0 means transparent, 255 means opaque
                imwrite(currentFolder + 'untitled.png', M)
            else:
                errorList.append('JPG MISSING: ' + thisDir)
        
        # Delete YTS picture, if exists
        if glob(currentFolder + 'WWW.YTS.AG.jpg'):
            os.remove(currentFolder + 'WWW.YTS.AG.jpg')
        if glob(currentFolder + 'WWW.YIFY-TORRENTS.COM.jpg'):
            os.remove(currentFolder + 'WWW.YIFY-TORRENTS.COM.jpg')
        if glob(currentFolder + 'www.YTS.AM.jpg'):
            os.remove(currentFolder + 'www.YTS.AM.jpg')
        
        # Create ICO file from python script CreateICO.py
        if not glob(currentFolder + 'favicon.ico'):
            if glob(currentFolder + 'untitled.png'):
                with Image(filename = currentFolder + 'untitled.png') as img:
                    img.format = 'ico'
                    img.resize(256,256)
                    img.save(filename = currentFolder + 'favicon.ico')
                print('Ico created: ' + thisDir)
        
        # Set ICO picture as folder icon, if it extists
        if glob(currentFolder + 'favicon.ico') and not glob(currentFolder + 'desktop.ini'):
            oldname = currentFolder + 'desktop.txt'
            newname = currentFolder + 'desktop.ini'
            f = open(oldname, 'w')
            f.write('[.ShellClassInfo]\n')
#            f.write('IconResource=' 'C:\\Users\\Pablo\\Videos\\PELIS\\' + thisDir + '\\favicon.ico,0\n')
            f.write('IconResource=favicon.ico,0\n')
            f.write('[ViewState]\n')
            f.write('Mode=\n')
            f.write('Vid=\n')
            f.write('FolderType=Pictures\n')
            f.close()
            os.rename(oldname, newname)
            FILE_ATTRIBUTE_READONLY = 0x01
            FILE_ATTRIBUTE_HIDDEN = 0x02
            FILE_ATTRIBUTE_SYSTEM = 0x04
            Attributes = FILE_ATTRIBUTE_HIDDEN | FILE_ATTRIBUTE_SYSTEM
            SetFileAttributes(newname, Attributes)
            SetFileAttributes(currentFolder, FILE_ATTRIBUTE_READONLY)

# Display errors
if errorList:
    if len(errorList) == 1:
        print('1 ERROR:')
    else:
        print(str(len(errorList)) + ' ERRORS:')
    
    for elem in errorList:
        print(elem)
else:
    print('\nDone')

input('\nPress ENTER to exit...')