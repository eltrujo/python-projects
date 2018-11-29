# -*- coding: utf-8 -*-
"""
Created on Wed May  9 18:14:33 2018

@author: Pablo
"""

from __future__ import division
from pytube import YouTube
from subprocess import check_output
from mp3_tagger import MP3File
from os import rename, remove
from sys import stdout as sys_stdout
from requests import get as requests_get
from bs4 import BeautifulSoup
from unicodedata import normalize
import tkinter as tk
from tkinter import ttk

global first
global totalSize
global link_received
global videoLink
global entry_song
global entry_artist
global btn
global l3

def invoke_btn(event):
    btn.invoke()
    
def get_data():
    global entry_song
    global entry_artist
    global l3
    songName = entry_song.get()
    artistName = entry_artist.get()
    if artistName == '':
        global link_received
        global videoLink
        link_received = True
        videoLink = songName
        entry_song.delete(0, tk.END)
        entry_song.focus()
        l3['text'] = 'Link received'
        root.update()
    else:
        main_function(songName, artistName)
    
def printProgress(stream, chunk, file_handle, bytes_remaining):
    global first
    global totalSize
    global progress
    if first:
        totalSize = bytes_remaining
        first = False
    else:
        progress['value'] = 100*(1-bytes_remaining/totalSize)
        root.update()

def main_function(songName, artistName):
    global entry_song
    global entry_artist
    global btn
    global l3
    global first
    global link_received
    
    btn['state'] = tk.DISABLED
    entry_song['state'] = tk.DISABLED
    entry_artist['state'] = tk.DISABLED
    root.update()
    
    if not link_received:
        l3['text'] = 'Searching YouTube...'
        root.update()
        str1 = songName.replace(' ','+').lower()
        str2 = artistName.replace(' ft','').replace(',','').replace(' &','').replace('.','').replace(' y','').replace(' ','+').lower()
        
        youtube_search = 'https://www.youtube.com/results?search_query=' + str1 + '+' + str2 + '+lyrics'
        page = requests_get(youtube_search, allow_redirects=True)
        soup = BeautifulSoup(page.content, 'html.parser')
        videoList = soup.find_all('a', class_='yt-uix-tile-link')
        vidLink = 'https://www.youtube.com' + videoList[0]['href']
        for i in range(len(videoList)):
            vidTitle = videoList[i]['title'].lower()
            vidTitle = normalize('NFKD',vidTitle).encode('ASCII', 'ignore').decode('UTF-8')
            if ('lyric' in vidTitle or 'letra' in vidTitle) and str1.replace('+',' ') in vidTitle and str2.split('+')[0] in vidTitle:
                vidLink = 'https://www.youtube.com' + videoList[i]['href']
                l3['text'] = 'Song found'
                root.update()
                break
        if i == len(videoList)-1:
            print('Song found: ' + videoList[0].get_text().encode(sys_stdout.encoding, errors='replace').decode('UTF-8'))
        else:
            print('Song found: ' + videoList[i].get_text().encode(sys_stdout.encoding, errors='replace').decode('UTF-8'))
    else:
        global videoLink
        vidLink = videoLink
        
    l3['text'] = 'Downloading...'
    first = True
    yt = YouTube(vidLink,on_progress_callback=printProgress)
    #video = yt.streams.get_by_itag(136) # mp4 720p (just video, no audio)
    audio = yt.streams.get_by_itag(140) # just audio but in mp4 (simply change extension name)
    if not audio:
        audio = yt.streams.filter(mime_type='video/mp4').first()
        if not audio:
            audio = yt.streams.first()
    # Prepare name for command shell
    specialName = songName.replace(' ', '_')
    specialName = specialName.replace('&', '')
    specialName = specialName.replace(',', '')
    specialName = specialName.replace('.', '')
    oldFile = specialName + '.mp4'
    newFile = specialName + '.mp3'
    # Keep original name for renaming afterwards
    newName = songName + '.mp3'
    # Download stream
    audio.download(path,specialName)
    progress['value'] = 100
    l3['text'] = 'Converting to mp3...'
    root.update()
    # Convert downloaded mp4 to mp3
    shellCommand = 'ffmpeg -i ' + path + oldFile + ' -vn -ar 44100 -ac 1 -b:a 192k -f mp3 ' + path + newFile
    check_output(shellCommand, shell=True)
    # Delete mp4 file
    remove(path + oldFile)
    # Set song artist meta tag
    try:
        mp3 = MP3File(path + newFile)
        mp3.artist = artistName
        mp3.save()
        rename(path + newFile, path + '../Music/' + newName)
    except:
        rename(path + newFile, path + '../Music/' + newName[:-4] + ' - ' + artistName + '.mp3')
    l3['text'] = 'Done'
    root.update()
        
path = 'C:/Users/Pablo/Desktop/'
link_received = False

# =============================================================================
# GUI
# =============================================================================
# Create a window and center it
root = tk.Tk()
# Gets the requested values of the height and widht.
windowWidth = root.winfo_reqwidth()
windowHeight = root.winfo_reqheight()
# Gets both half the screen width/height and window width/height
positionRight = int(root.winfo_screenwidth()/2 - windowWidth/2)
positionDown = int(root.winfo_screenheight()/2 - windowHeight/2)
# Positions the window in the center of the page.
root.geometry("+{}+{}".format(positionRight, positionDown))

# Place all widgets
l1 = tk.Label(root, text='Song: ')
l1.grid(row=0,column=0)
entry_song = tk.Entry(root)
entry_song.grid(row=0,column=1)
entry_song.focus()
l2 = tk.Label(root, text='Artist: ')
l2.grid(row=1,column=0)
entry_artist = tk.Entry(root)
entry_artist.grid(row=1,column=1)
btn = tk.Button(root, text='Download', command=get_data)
btn.grid(row=2,columnspan=2)
l3 = tk.Label(root, text='')
l3.grid(row=3,columnspan=2)
progress = ttk.Progressbar(root, orient="horizontal", length=100, mode="determinate", value=0)
progress.grid(row=4,columnspan=2)

root.bind('<Return>', invoke_btn)

root.mainloop()