from datetime import datetime
import requests
import time
import os
import random
from pydub import AudioSegment

date = datetime.today().strftime('%m-%d-%y')
fileNumber = 0

def CreateAudioFile(sentence, voice):
    global fileNumber
    os.system("say -v " + voice + ' \"' + sentence.replace('\"', ",") + '\" -o AudioFiles/' + date + "/" + "ttsSegment" + str(fileNumber) + ".aiff")
    os.system("ffmpeg -i /Users/nragis/Desktop/Reddit_Bot/AudioFiles/" + date + "/ttsSegment" + str(fileNumber)  + ".aiff -f mp3 -acodec libmp3lame -ab 192000 -ar 44100 /Users/nragis/Desktop/Reddit_Bot/AudioFiles/" + date  +  "/ttsSegment" + str(fileNumber)  + ".mp3 2>NUL")    
    os.system("rm /Users/nragis/Desktop/Reddit_Bot/AudioFiles/" + date + "/ttsSegment" + str(fileNumber) + ".aiff 2>NUL")

def SeperateSentences(line):
    lines = line.split(".")
    i = 0
    while i < len(lines): 
        empty = 1
        for ch in lines[i]:
            if (ch != ' ' and ch != "." and ch != "\n" and ch !=")" and ch != "(" and ch != '\"' and ch != "\'"):
                empty = 0
        if empty == 1:
            del lines[i]
        else:
            i += 1

    return lines


def ReadData():
    file = open("/Users/nragis/Desktop/Reddit_Bot/ThreadData/" + date + "_Data.txt", "r")
    
    lines = file.readlines()
    
    return [lines[0][14:].replace("\n", ""), lines[1][13:].replace("\n", ""), lines[2][14:].replace("\n", ""), lines[3][13:].replace("\n", ""), [lines[i].replace(str(i-5) + ") ", "") for i in range(5,len(lines))]]

def main():
    global fileNumber
    print "\tGetting voices.txt . . ."
    
    voiceFile = open("/Users/nragis/Desktop/Reddit_Bot/voices.txt", "r")
    voices = [ i.replace("\n", "") for i in voiceFile.readlines()]
    voiceFile.close()    

    for i in range(0, len(voices)):
        print "\t" + str(i) + ") " + voices[i]
    print "\t" + str(len(voices)) + ") Random"
    print "\tChoose an above voice"
    awn = input()
    if awn >= 0 and awn < len(voices):
        voice = voices[awn]
    else: 
        voice = voices[random.randint(0, len(voices)-1)]
    
    print "\tReading data from /Users/nragis/Desktop/Reddit_Bot/ThreadData/" + date + "_Data.txt"
    
    fullData = ReadData()
    
    os.system("mkdir AudioFiles/" + date + " 2>NUL")
    
    writeData = open("/Users/nragis/Desktop/Reddit_Bot/ThreadData/" + date + "_Data.txt", "a")
    writeData.write("\\, \n")
    
    commentData = [line.split("\\, ") for line in fullData[4]]
    
    print "\tCreating Audio Files . . ."
    
    nullAudio = AudioSegment.silent(duration=10)
    shortPause = AudioSegment.silent(duration=100)
    longPause = AudioSegment.silent(duration=800)
    separatorNoise = AudioSegment.from_mp3("separatorNoise.mp3")[:800] - 1

    finalAudio = nullAudio
    
    print "\t\tCreating intro audio . . ."    

    introAudio = "Pocket Reddit presents, ,r slash ask reddit. " + fullData[0]
    CreateAudioFile(introAudio, voice)
    segmentAudio = AudioSegment.from_mp3("AudioFiles/" + date  + "/ttsSegment" + str(fileNumber) + ".mp3")
    writeData.write("Intro) " + str(len(segmentAudio)) + "\n")
    finalAudio = finalAudio + segmentAudio + shortPause + separatorNoise
    os.remove("AudioFiles/" + date  + "/ttsSegment" + str(fileNumber) + ".mp3")

    print "\t\tCreating comment audio . . ."

    for comment in commentData:
        sentenceList = SeperateSentences(comment[0])
        print "\t\t\tCreating audio files out of " + str(len(sentenceList))  + " segments of comment " + str(commentData.index(comment)) + " and appending them to finalAudio.mp3"
        for sentence in sentenceList:
            global fileNumber
            if sentence != "":
#                print "\t\tCreating segment audio #" + str(fileNumber) + " and appending it to the end of finalAudio"
                CreateAudioFile(sentence, voice)
                segmentAudio = AudioSegment.from_mp3("AudioFiles/" + date  + "/ttsSegment" + str(fileNumber) + ".mp3")
                writeData.write(str(fileNumber) + ") " + str(len(segmentAudio)) + "\n")
                finalAudio = finalAudio + shortPause + segmentAudio
                os.remove("AudioFiles/" + date  + "/ttsSegment" + str(fileNumber) + ".mp3")
                fileNumber += 1
        if commentData.index(comment) + 1 < len(commentData):
            if commentData[commentData.index(comment) + 1][3] == '0':
                finalAudio = finalAudio + separatorNoise
            else:
                finalAudio = finalAudio + longPause
        else:
            finalAudio = finalAudio + longPause
    
#        if commentData.index(comment)%5 == 4:
#            finalAudio.export("AudioFiles/" +  date  + "/finalAudio.mp3", format="mp3", bitrate="192k")
#            finalAudio = AudioSegment.from_mp3("AudioFiles/" + date  + "/finalAudio.mp3") 
#            finalAudio = finalAudio + 1
#            os.remove("AudioFiles/" + date + "/finalAudio.mp3")        
    
    print "\t\tCreating outro audio . . ."
    
    outroAudio = "Thank you for watching and check the link in the description to see how this video was made!"
    CreateAudioFile(outroAudio, voice)
    segmentAudio = AudioSegment.from_mp3("AudioFiles/" + date  + "/ttsSegment" + str(fileNumber) + ".mp3")
    writeData.write("Closer) " + str(len(segmentAudio)) + "\n")
    finalAudio = finalAudio + segmentAudio + longPause + longPause + longPause + longPause + longPause
    os.remove("AudioFiles/" + date  + "/ttsSegment" + str(fileNumber) + ".mp3")
    
    finalAudio.export("AudioFiles/" + date  + "/finalAudio.mp3", format="mp3", bitrate="192k")
    
    print "\tfinalAudio.mp3 finished being constructed"
    
    
    

print "Running textToSpeech.py"
main()
print "textToSpeech.py completed"
