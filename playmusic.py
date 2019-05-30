#!/usr/bin/env python
import os
import time

def play_happy():
    os.system("open songs/happy.mp3")

def play_sad():
    os.system("open songs/sad.mp3")

def play_anger():
    os.system("open songs/anger.mp3")

def play_fear():
    os.system("open songs/fear.mp3")
    
def play_neutral():
    os.system("open songs/neutral.mp3")

def change_music(emotion, previous_emotion):
    if (previous_emotion == emotion):
        pass # do nothing since same emotion
    elif (emotion == 'neutral'):
        play_neutral()
    elif (emotion == 'happy'):
        play_happy()
    elif (emotion == 'angry'):
        play_anger()
    elif (emotion == 'fear'):
        play_fear()
    elif (emotion == 'surprise'):
        play_anger()
    elif (emotion == 'disgust'):
        play_anger()
    else:
        play_neutral()

if __name__ == "__main__":
    file = "song.mp3"
    os.system("open " + file)
    print("It's playing!")
    time.sleep(10)
    print("keep it going...")
    time.sleep(10)
    print("eh. next.")
    os.system("open " + "song2.m4a")
