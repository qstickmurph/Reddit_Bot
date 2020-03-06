from datetime import datetime
import time
from lxml import html
import requests
import re
import os
import random
import json
from pydub import AudioSegment
from shutil import copyfile
from PIL import Image, ImageDraw, ImageFont, ImageOps
import textwrap
import moviepy.editor as mpe

PATH = os.path.dirname(os.path.realpath(__file__))
DATE = datetime.today().strftime('%m-%d-%y')
NUMBER_OF_COMMENTS = 30
commentNumber = 0
fileNumber = 0

RESOLUTION = 1080
CHAR_PER_LINE = 135
TITLE_CHAR_PER_LINE = 60
LINES_PER_SCREEN = 30
FONT = "verdana"
BODY_SIZE = 24 
TITLE_SIZE = 48
HEADER_SIZE = 24
TEXT_COLOR = (215,215,215)
USER_COLOR = (80,190,253)
UPVOTE_COLOR = (126, 128, 129)

frameNumber = 0

### resetDay.py begins

def ResetDay():
    date = datetime.today().strftime('%m-%d-%y') 
    try:
        os.remove("/Users/nragis/Desktop/Reddit_Bot/PotentialThreads/" + date + "_PT.txt")
    except:
        print "Potential Threads does not exist\n"
    try:
        os.remove("/Users/nragis/Desktop/Reddit_Bot/Stats/" + date + "_Stats.txt")
    except:
        print "Stats does not exist\n"
    try:
        os.remove("/Users/nragis/Desktop/Reddit_Bot/ThreadData/" + date + "_Data.txt")
    except:
        print "Data does not exist\n"
    os.system("rm -R /Users/nragis/Desktop/Reddit_Bot/AudioFiles/" + date + " 2>NUL")

### getPotentialThreads.py begins

def GetPorentialThreads():
    date = datetime.today().strftime('%m-%d-%y')
    threadNames = []
    threadLinks = []
    askRedditBaseLink = "https://old.reddit.com/r/AskReddit/top/?sort=top&t=week"
    
    f = open("//Users/nragis/Desktop/Reddit_Bot/PotentialThreads/"+date+"_PT.txt","a+")	
    
    link = askRedditBaseLink
    for i in range(0,4):
        storageArrayNames = []
        storageArrayLinks = []
        print "\tGathering data for threads " + str(i*25) + "-" + str((i+1)*25) + " . . ."
        while(len(storageArrayNames) == 0):
            page = requests.get(link)
            tree = html.fromstring(page.content)
            storageArrayNames = tree.xpath('//a[@class="title may-blank "]/text()')
            storageArrayLinks = tree.xpath('//a[@class="title may-blank "]/@href')
        threadNames.extend(storageArrayNames)
        threadLinks.extend(storageArrayLinks)
        link = tree.xpath('//span[@class="next-button"]/a/@href')[0]

    print "\tSaving data to Reddit_Bot/PotentialThreads/"+date+"_PT.txt"	
    
    file = open("/Users/nragis/Desktop/Reddit_Bot/PreviousThreads.txt", "r")
    previousThreads = file.readlines()
    file.close()
    
    for i in range(0,100):
        threadNames[i] = threadNames[i].replace(u"\u2018", "'").replace(u"\u2019", "'").replace(u"\u201c", "\"").replace(u"\u201d", "\"")
        f.write(str(i) + "\\, " + threadNames[i] + "\\, " + threadLinks[i] + "\\, \n")
    
    f.close()

### chooseThread.py begins

def ChooseThread():
    date = datetime.today().strftime('%m-%d-%y')
    
    f = open("/Users/nragis/Desktop/Reddit_Bot/PotentialThreads/" + date + "_PT.txt", "r")
    
    fileLines = f.readlines()
    f.close()
    threadNames = []
    threadLinks = []
    index = 0
    
    
    for i in range(0, len(fileLines)):
        j = 0
        start = 0
        while (fileLines[i][j] != '\\' or fileLines[i][j+1] != ','):
            j = j + 1 
        j = j + 3
        start = j
        while (fileLines[i][j] != '\\' or fileLines[i][j+1] != ','):
            j = j + 1
        threadNames.append(fileLines[i][start:j-1])
        j = j + 3
        start = j
        while (fileLines[i][j] != '\\' or fileLines[i][j+1] != ','):
            j = j+1    
        threadLinks.append(fileLines[i][start:j-1])
    
    for i in range(0, len(fileLines)):
        print "\t" + str(i) + ") " + ''.join(threadNames[i])
    print "\t" + str(len(fileLines)) + ") Random"
    print "\tChoose a thread from above"
    validChoice = 0
    while(validChoice == 0):
        choice = int(raw_input())
        if(choice >= 0 and choice < len(fileLines)):
            validChoice = 1
            break
        elif(choice == len(fileLines)):
            validChoice = 1
            choice = random.randint(0,len(fileLines)-1)
            break
        print "\tInvalid choice"
    
    print "\tValid choice, modifying stats file . . ."
    f2 = open("/Users/nragis/Desktop/Reddit_Bot/Stats/" + date + "_Stats.txt", "a+")
    f2.write("Thread Name: " + "".join(threadNames[choice]) + "\n")
    f2.write("Link: " + "".join(threadLinks[choice]) + "\n")
    f2.close()
    
    f3 = open("/Users/nragis/Desktop/Reddit_Bot/PreviousThreads.txt", "a+")
    f3.write("".join(threadNames[choice]) + "\n")
    f3.close()
 
### collectData.py starts

def CompileTopX(valueList, lines, x, i, depth):
    for k in range(len(valueList), x):
        valueList.append(0)
#        print "\tAppending 0 to topList"
    compare = int(float(lines[i][2].replace("k", "e3")))

#    print "\tComparing " + str(compare) + " in index: [" + str(i) + "] of depth " + str(depth) for k in range(0,x):
        if compare > valueList[k]:
#            print "\tInserting " + str(compare) + " into index " + str(k)
            topList = ChangeList(valueList, k, compare)
            break
    
    if (lines[i][3] != []):
#        print "\tDelving into depth " + str(depth+1)
        topList = CompileTopX(valueList, lines[i][3], x, 0, depth+1)
    
    if i < len(lines)-1:
        CompileTopX(valueList, lines, x, i + 1, depth)
    else:
        return valueList
    return valueList[-1]
    
def ChangeList(list, index, input):    
    placeholder1 = list[index]
    list[index] = input
    index += 1
    while(index < len(list)-1):
        placeholder2 = list[index]
        list[index] = placeholder1
        placeholder1 = list[index + 1]
        list[index + 1] = placeholder2
        index +=2
    if (index == len(list)-1):
        list[index] = placeholder1
    return list 

def TrimList(list, minVal):
    for k in range(0, len(list)):
        if (int(float(list[k][2].replace('k','e3'))) < minVal) or (list[k][1] == "AutoModerator"):
            list[k] = []
        elif (list[k][3] != []):
            list[k][3] = TrimList(list[k][3], minVal)
    return list
    
def FilterData(list, filter, i, depth):
    if list[i] != []:
#        print "\tRunning unidecode on string"
#        list[i][0] = RemoveNonAscii(list[i][0])
        for f in filter:
#            if list[i][0] != list[i][0].replace(f[0], f[1]):
#                print "\tReplacing " + f[0] + " with " + f[1] + " at index " + str(i) + " and depth " + str(depth)
            list[i][0] = ''.join([ch if ord(ch) < 128 else '' for ch in list[i][0].replace(f[0], f[1])])
        if len(list[i][3]) != 0:
            list[i][3] = FilterData(list[i][3], filter, 0, depth + 1)
    for k in range(i+1, len(list)-1):
        if len(list[k]) == 4:
            list = FilterData(list, filter, k, depth)
            break
    return list

def unicodeCheck(list, i , depth):
    if list[i] != []:
        list[i][0].decode("utf-8") 
        if len(list[i][3]) != 0:
            list[i][3] = unicodeCheck(list[i][3], 0, depth + 1)
    for k in range(i+1, len(list)-1):
        if len(list[k]) == 4:
            unicodeCheck(list, k, depth)
            break
    return list

def OutputComments(commentData, outputFile, i, depth):
    global commentNumber
    if commentData[i] != []:
        outputFile.write(commentData[i][0].replace("\n", "") + "\\, " + commentData[i][1].replace("\n", "") + "\\, " + commentData[i][2].replace("\n", "") + "\\, " + str(depth) + "\\, "  + "\n")
#        outputFile.write(str(commentNumber) + ") " + commentData[i][0] + "\\, " + commentData[i][1] + "\\, " + commentData[i][2] + "\\, " + str(depth) + "\\, "  + "\n")
        commentNumber += 1
        if len(commentData[i][3]) > 0:
            OutputComments(commentData[i][3], outputFile, 0, depth + 1)
    for k in range(i+1, len(commentData)-1):
        if len(commentData[k]) == 4:
            OutputComments(commentData, outputFile, k, depth)
            break
    return

def OutputData(commentData, postData):
    outputFile = open("//Users/nragis/Desktop/Reddit_Bot/ThreadData/"+date+"_Data.txt","a+")
    outputFile.write("Thread Title: " + postData[0] + "\n")
    outputFile.write("Poster Name: " + postData[1] + "\n")
    outputFile.write("Upvote Count: " + postData[2] + "\n")
    outputFile.write("Thread Link: " + postData[3] + "\n")
    outputFile.write("\\, \n")
    
    OutputComments(commentData, outputFile, 0, 0)
    
    outputFile.close()
    return

def SearchFor(basePath, tree, depth):
    comments = []
    #    print "Called SearchFor(" + basePath + ", " + "tree, " + str(depth) + ")"
#    comments = tree.xpath(basePath + "/div[@class='entry unvoted']/form/div/div[contains(concat(' ', @class, ' '), ' md ')]/p/text()")
#    print len(tree.xpath(basePath + "/div[@class='entry unvoted']/form/div/div[contains(concat(' ', @class, ' '), ' md ')]")) 
    for i in range(1,len(tree.xpath(basePath + "/div[@class='entry unvoted']/form/div/div[contains(concat(' ', @class, ' '), ' md ')]"))):
        tempString = ""
#        print tree.xpath("(" + basePath + "/div[@class='entry unvoted'])[" + str(i) + "]/form/div/div[contains(concat(' ', @class, ' '), ' md ')]/p/text()")
        for j in tree.xpath("(" + basePath + "/div[@class='entry unvoted'])[" + str(i) + "]/form/div/div[contains(concat(' ', @class, ' '), ' md ')]/p/text()"):
            tempString += j + " "
        comments.append(tempString)
#        print tempString    
    users = tree.xpath(basePath + "/@data-author")
    upvotes = [i[0:-7] for i in tree.xpath(basePath + "/div[@class='entry unvoted']/p[@class='tagline']/span[@class='score unvoted']/text()")]
    

    finalList = []
    for i in range(0, min(min(len(comments),len(users)),len(upvotes))):
        if i < 2 or depth < 1:
#            print [comments[i], users[i], upvotes[i]]
            childPath = basePath + "[" + str(i+1) + "]/div[@class='child']/div[@class='sitetable listing']/div[contains(concat(' ', @class, ' '),' noncollapsed ')]"
            
            if(depth < 1):
                finalList.append([comments[i], users[i], upvotes[i], SearchFor(childPath, tree, depth+1)])
            else:
                finalList.append([comments[i], users[i], upvotes[i], []])
    
    return finalList

def CollectData():
    filterFile = open("/Users/nragis/Desktop/Reddit_Bot/filter.txt", "r")
    filterFileLines = filterFile.readlines()
    FILTER = [line.decode("utf-8").replace("\n", "").split(": ") for line in filterFileLines]

    print "\tReading //Users/nragis/Desktop/Reddit_Bot/Stats/"+date+"_Stats.txt . . ."

    f = open("//Users/nragis/Desktop/Reddit_Bot/Stats/"+date+"_Stats.txt","r")
    flines = f.readlines()
    postTitle = flines[0][13:]
    postLink = "https://old.reddit.com" + flines[1][6:-1] + "/?limit=500"
    f.close()

    print "\tThread Title: " + postTitle[:-1]
    
    print "\tConnecting to " + postLink + " . . ."
    
    while True:
        page = requests.get(postLink)
        tree = html.fromstring(page.content)
        if(tree.xpath("//title/text()") != ["Too Many Requests"]):
            break;
    
    print "\tGathering post data . . ."
    
    postUpvotes = tree.xpath("//div[@class='midcol unvoted']/div[@class = 'score unvoted']/text()")[0]
    postUser = tree.xpath("//div[@id='siteTable']/div/@data-author")[0]
    postData = [postTitle[:-1], postUser, postUpvotes, postLink[:-1]]


    basePath = "//div[@class='commentarea']/div[@class='sitetable nestedlisting']/div[contains(concat(' ',@class,' '), ' noncollapsed ')]"
 
    print "\tGathering comment data . . ."
    
    commentList = SearchFor(basePath, tree, 0)
#    print commentList   
   
    print "\tCompiling top " + str(NUMBER_OF_COMMENTS) + " comments . . ."
     
    minUpvotes =  CompileTopX([], commentList, NUMBER_OF_COMMENTS, 0, 0)
    
    print "\tTrimming comments . . . "

    commentList = TrimList(commentList, minUpvotes)
#    print commentList

    print "\tFiltering comments . . ."

    commentList = FilterData(commentList, FILTER, 0, 0)
#    print commentList

    print "\tChecking unicode . . ."
    unicodeCheck(commentList, 0, 0)
    
    print "\tOutputting data to //Users/nragis/Desktop/Reddit_Bot/ThreadData/" + date + "_data.txt . . ."
    OutputData(commentList, postData)
    
### textToSpeach.py begins

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

def textToSpeach():
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
    
### videoCreate.py begins

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
    
    lastCommentIndex = 5
    for i in range(5,len(lines)):
        lastCommentIndex = i
        if lines[i].replace("\n", "") == "\\, ":
            break
    

    lastFramedataIndex = lastCommentIndex + 2

    for i in range(lastCommentIndex + 2, len(lines)):
        if lines[i].replace("\n", "") == "\\, ":
            break
        lastFramedataIndex = i
    
    
    return [lines[0][14:].replace("\n", ""), lines[1][13:].replace("\n", ""), lines[2][14:].replace("\n", ""), lines[3][13:].replace("\n", ""), [lines[i].replace("\n", "") for i in range(5,lastCommentIndex)], [lines[i].replace("\n", "").replace(str(i - lastCommentIndex - 2) + ") ", "").replace("Intro) ", "").replace("Closer)", "") for i in range(lastCommentIndex + 1, lastFramedataIndex + 1)]]

def CreateCommentFrame(text, comment, totalChars, page):
    global frameNumber
    if totalChars > LINES_PER_SCREEN*CHAR_PER_LINE :
        totalChars = LINES_PER_SCREEN*CHAR_PER_LINE
    
    lineWidth = RESOLUTION/9*16/10*9
    lineHeight = (RESOLUTION/20*19)/(LINES_PER_SCREEN+1)
    yCoord = (RESOLUTION - lineHeight*int(totalChars/CHAR_PER_LINE) - 1)/2 - 80
    xCoord = (RESOLUTION/9*16 - RESOLUTION/9*16/10*9)/2

    wrappedText = textwrap.fill(text, CHAR_PER_LINE).split("\n")
    
    frame = Image.new('RGB', (RESOLUTION/9*16, RESOLUTION), color = (26,26,27))
    
    fnt = ImageFont.truetype("//Library/Fonts/verdana/verdana.ttf", min(HEADER_SIZE, lineHeight))
    d = ImageDraw.Draw(frame)

    if (page == 0):
        d.text((xCoord, yCoord), comment[1], font = fnt, fill=USER_COLOR)
        d.text((xCoord + fnt.getsize(comment[1])[0] + 10, yCoord), comment[2] + " points", font = fnt, fill=UPVOTE_COLOR)
        redditArrows = Image.open("redditArrows.png")
        frame.paste(redditArrows.resize((int((float)(HEADER_SIZE+BODY_SIZE+20)/108.0*47.0),HEADER_SIZE+BODY_SIZE+20)),(xCoord - 44, yCoord))
    
        barHeight = lineHeight * (int)(totalChars/CHAR_PER_LINE + 2) - (HEADER_SIZE+BODY_SIZE+20)
        d.rectangle(((xCoord - 44 - 2 + int((float)(HEADER_SIZE+BODY_SIZE+20)/108.0*47.0/2.0), yCoord + HEADER_SIZE+BODY_SIZE+25), (xCoord - 44 + 2 + int((float)(HEADER_SIZE+BODY_SIZE+20)/108.0*47.0/2.0), yCoord + HEADER_SIZE+BODY_SIZE+25 + barHeight)), fill=(52,53,54))
    else:
        barHeight = HEADER_SIZE + TEXT_SIZE*len(wrappedText)
        d.rectangle(((xCoord - 44 - 2 + int((float)(HEADER_SIZE+BODY_SIZE+20)/108.0*47.0/2.0), yCoord), (xCoord - 44 + 2 + int((float)(HEADER_SIZE+BODY_SIZE+20)/108.0*47.0/2.0), yCoord + barHeight)), fill=(52,53,54))

    yCoord += fnt.getsize(comment[1])[1] + 8

    fnt = ImageFont.truetype("//Library/Fonts/verdana/verdana.ttf", min(BODY_SIZE, lineHeight))
    
    for line in wrappedText:
        d.text((xCoord, yCoord), line, font = fnt, fill=TEXT_COLOR)
        yCoord += lineHeight
    
    frame.save("//Users/nragis/Desktop/Reddit_Bot/Frames/frame" + str(frameNumber)  + ".jpg", "JPEG")

def CreateCommentFrame(text, page, lines):
    global frameNumber
#    print text    
    commentData = text.split("\\, ")
    
    if lines > LINES_PER_SCREEN:
        lines = LINES_PER_SCREEN
    
    commentData = [[commentData[4*k + 3], commentData[4*k], commentData[4*k + 1], commentData[4*k + 2]] for k in range(0, len(commentData)/4)]
    wrappedText = [textwrap.fill(commentData[i][0], CHAR_PER_LINE).split("\n") for i in range(0,len(commentData)/4)]
    
    for i in range(0,page*LINES_PER_SCREEN):
        for line in wrappedText[i]:
            if len(commentData[0][0]) != 0:
                commentData[0][0] = commentData[0][0][len(line):]
            else:
                commentData = commentData[4:]
        
    wrappedText = None
    
    lineWidth = RESOLUTION/9*16/10*9
    lineHeight = (RESOLUTION/20*19)/(LINES_PER_SCREEN)
    yCoord = (RESOLUTION - lineHeight*(lines))/2 - 30
    xCoord = (RESOLUTION/9*16 - RESOLUTION/9*16/10*9)/2
    
    frame = Image.new('RGB', (RESOLUTION/9*16, RESOLUTION), color = (26,26,27))
    
    fnt = ImageFont.truetype("//Library/Fonts/verdana/verdana.ttf", min(HEADER_SIZE, lineHeight))
    d = ImageDraw.Draw(frame)
#    print len(commentData)
    for comment in commentData:
        
        xCoord = (RESOLUTION/9*16 - RESOLUTION/9*16/10*9)/2 + 40 * int(comment[3])
        wrappedText = textwrap.fill(comment[0], CHAR_PER_LINE).split("\n")
        
        
        d.text((xCoord, yCoord), comment[1], font = fnt, fill=USER_COLOR)
        d.text((xCoord + fnt.getsize(comment[1])[0] + 10, yCoord), comment[2] + " points", font = fnt, fill=UPVOTE_COLOR)
        redditArrows = Image.open("redditArrows.png")
        frame.paste(redditArrows.resize((int((float)(HEADER_SIZE+BODY_SIZE+20)/108.0*47.0),HEADER_SIZE+BODY_SIZE+20)),(xCoord - 44, yCoord))
        
        barHeight = max((lineHeight)*(len(wrappedText) + 1) - (HEADER_SIZE+BODY_SIZE+20), 0)
#        barHeight = 100
        d.rectangle(((xCoord - 44 - 2 + (int((float)(HEADER_SIZE+BODY_SIZE+20)/108.0*47.0))/2, yCoord + HEADER_SIZE+BODY_SIZE+20), (xCoord - 44 + 2 + (int((float)(HEADER_SIZE+BODY_SIZE+20)/108.0*47.0))/2, yCoord + HEADER_SIZE+BODY_SIZE + 20 + barHeight)), fill=(52,53,54))
        
#        else:
#            barHeight = lineHeight * (int)(totalChars/CHAR_PER_LINE + 2)
#            d.rectangle(((xCoord - 44 - 2 + int((float)(HEADER_SIZE+BODY_SIZE+20)/108.0*47.0/2.0), yCoord), (xCoord - 44 + 2 + int((float)(HEADER_SIZE+BODY_SIZE+20)/108.0*47.0/2.0), yCoord + barHeight)), fill=(52,53,54))
    
        yCoord += fnt.getsize(comment[1])[1] + 8
    
        fnt = ImageFont.truetype("//Library/Fonts/verdana/verdana.ttf", min(BODY_SIZE, lineHeight))
    
        for line in wrappedText:
            d.text((xCoord, yCoord), line, font = fnt, fill=TEXT_COLOR)
            yCoord += lineHeight
        
    
    frame.save("//Users/nragis/Desktop/Reddit_Bot/Frames/frame" + str(frameNumber)  + ".jpg", "JPEG")

def CreateCommentSegment(commentData, frameData, shortPauseLength, longPauseLength, seperatorClip):
    global frameNumber
    page = 0
    fullClip = seperatorClip.set_duration(0.001)
    displayText = ""
    
    lines = 0
    for comment in commentData:
        lines += 1
        lines += int(len(textwrap.fill(comment[0],CHAR_PER_LINE).split("\n")))
        if commentData.index(comment) >= len(commentData) - 1:
            break
        if commentData[commentData.index(comment)+1][3] == "0":
            break
#    print "\t\t\t\tLINES: " + str(lines)
    i = 0
    while 1 == 1:
        displayText += commentData[i][1] + "\\, " + commentData[i][2] + "\\, " + commentData[i][3] + "\\, "
        sentenceList = SeperateSentences(commentData[i][0])
        for sentence in sentenceList:
            displayText += sentence[:-1] + sentence[-1:].replace(" ", "") + "."
            if len(displayText + sentence + ".") < (LINES_PER_SCREEN*CHAR_PER_LINE):
                page = page
            else:
                page += 1
#            print "\t\t\t\t\tRunning CreateCommentFrame() on ", displayText, " || page=" + str(page)
#            print displayText
            
            CreateCommentFrame(displayText, page, lines)
            
            segment = mpe.ImageClip("//Users/nragis/Desktop/Reddit_Bot/Frames/frame" + str(frameNumber) + ".jpg").set_duration(((float)(frameData[frameNumber + 1]) + shortPauseLength)/1000.0)
#            print "\t\t\t\t\tSegment " + str(frameNumber) + " Length: " + str(segment.duration), float(frameData[frameNumber + 1])/1000.0 + .2
            os.remove("Frames/frame" + str(frameNumber) + ".jpg")
            fullClip = mpe.concatenate_videoclips([fullClip, segment])
            frameNumber += 1
            
        displayText += "\\, " 
        
        if i + 1 >= len(commentData):
            break
        if commentData[i+1][3] == "0":
            break
        
        fullClip = mpe.concatenate_videoclips([fullClip, segment.set_duration(longPauseLength/1000.0)])
        i += 1
    return fullClip 

def VideoCreate():
    global frameNumber
    
    print "\tReading data from /Users/nragis/Desktop/Reddit_Bot/ThreadData/" + date + "_Data.txt"

    data = ReadData()
    
    commentData = [line.split("\\, ") for line in data[4]]
    frameData = data[5]
    
    print "\tCreating video segments . . ."
    print "\t\tCreating intro video segment . . ."

    xCoord = RESOLUTION*16/9/10
    yCoord = int(RESOLUTION/3) - 40
    wrappedTitle = textwrap.fill(data[0], TITLE_CHAR_PER_LINE).split("\n")

    introFrame = Image.new('RGB', (RESOLUTION/9*16, RESOLUTION), color = (26,26,27))

    fnt = ImageFont.truetype("//Library/Fonts/verdana/verdana.ttf", HEADER_SIZE)
    fntb = ImageFont.truetype("//Library/Fonts/verdana/verdana.ttf", HEADER_SIZE)
    d = ImageDraw.Draw(introFrame)
    
    redditLogo = Image.open("askRedditIcon.png");
    
    introFrame.paste((redditLogo.resize((TITLE_SIZE,TITLE_SIZE))), (xCoord,yCoord)) 
    d.text((xCoord + TITLE_SIZE + 8, yCoord + TITLE_SIZE/4), "r/AskReddit", font = fnt, fill=TEXT_COLOR)
    
    d.text((xCoord + TITLE_SIZE + 8 + fnt.getsize("r/AskReddit")[0] + 8, yCoord + TITLE_SIZE/4), "Posted by u/", font = fnt, fill=UPVOTE_COLOR)
    d.text((xCoord + TITLE_SIZE + 8 + fnt.getsize("r/AskReddit")[0] + fnt.getsize("Posted by u/")[0] + 8, yCoord + TITLE_SIZE/4), data[1], font = fnt, fill=USER_COLOR)

    #draw platinum, gold, silver
    singleArrow = Image.open("singleArrow.png")
    introFrame.paste((singleArrow.resize((TITLE_SIZE, TITLE_SIZE))), (xCoord - TITLE_SIZE - 25, yCoord))
    d.text((xCoord - TITLE_SIZE/2 - 25 - fntb.getsize(data[2])[0]/2, yCoord + TITLE_SIZE + 10), data[2], font=fntb, fill='white')
    singleArrow = ImageOps.flip(singleArrow)
    introFrame.paste((singleArrow.resize((TITLE_SIZE, TITLE_SIZE))), (xCoord - TITLE_SIZE - 25, yCoord + 2*TITLE_SIZE + 10))

    fntb = ImageFont.truetype("//Library/Fonts/verdana/verdana.ttf", TITLE_SIZE)
    
    yCoord += TITLE_SIZE + 20

    for line in wrappedTitle:
        d.text((xCoord, yCoord), line, font = fntb, fill=TEXT_COLOR)
        yCoord += TITLE_SIZE + 8

    introFrame.save("//Users/nragis/Desktop/Reddit_Bot/Frames/introFrame.jpg", "JPEG")
    
    
    shortPauseLength = 100
    longPauseLength = 800
    seperatorLength = 800
    longPauseImage = Image.new('RGB', (RESOLUTION/9*16, RESOLUTION), color = (26,26,27))
    longPauseImage.save("//Users/nragis/Desktop/Reddit_Bot/Frames/longPauseImage.jpg", "JPEG")
    longPauseClip = mpe.ImageClip("//Users/nragis/Desktop/Reddit_Bot/Frames/longPauseImage.jpg").set_duration(longPauseLength/1000.0)
    
    seperatorImage = longPauseImage
    seperatorImage.save("//Users/nragis/Desktop/Reddit_Bot/Frames/seperatorImage.jpg", "JPEG")
    seperatorClip = mpe.ImageClip("//Users/nragis/Desktop/Reddit_Bot/Frames/seperatorImage.jpg").set_duration(seperatorLength/1000.0)
    
    finalClip = mpe.ImageClip("//Users/nragis/Desktop/Reddit_Bot/Frames/introFrame.jpg").set_duration((float)(frameData[0])/1000.0 - 0.1 + shortPauseLength/1000.0*2)
    
    finalClip = mpe.concatenate_videoclips([finalClip, seperatorClip])

    print "\t\tCreating comment video segments . . ."
    for i in range(0, len(commentData)):
        if commentData[i][3] == '0':
            print "\t\t\tCreating segments for comment " + str(i) + " and it's children"
            commentClip = CreateCommentSegment(commentData[i:], frameData, shortPauseLength, longPauseLength, seperatorClip)
            finalClip = mpe.concatenate_videoclips([finalClip, commentClip, seperatorClip])
#        if i%25 == 24:
#            finalClip.write_videofile("partialVideo.mp4", fps=24, verbose=False, logger=None)
#            finalClip = mpe.VideoFileClip("partialVideo.mp4")
#            os.remove("partialVideo.mp4")
    
    print "\t\tCreating closer video segment . . ."
    
    blank = Image.new('RGB', (RESOLUTION/9*16, RESOLUTION), color = (26,26,27))
    blank.save("//Users/nragis/Desktop/Reddit_Bot/Frames/closerFrame.jpg", "JPEG")

    closerSegment = mpe.ImageClip("//Users/nragis/Desktop/Reddit_Bot/Frames/closerFrame.jpg").set_duration(((float)(frameData[-1]) + 3*longPauseLength)/1000.0)
    finalClip = mpe.concatenate_videoclips([finalClip, closerSegment])

    os.remove("Frames/introFrame.jpg")
    os.remove("Frames/closerFrame.jpg")
    print "\tAdding audio to video and creating completedVideo" + date + ".mp4 in CompleteVideos"
    
#    song = mpe.AudioFileClip("//Users/nragis/Desktop/Reddit_Bot/Songs/song" + str(random.randint(0,6)) + ".mp3")
    song = mpe.AudioFileClip("//Users/nragis/Desktop/Reddit_Bot/Songs/song6.mp3")
    while song.duration < finalClip.duration:
        song = mpe.concatenate_audioclips([song, song])
    
    song = song.volumex(.1)
    audio_background = mpe.AudioFileClip("//Users/nragis/Desktop/Reddit_Bot/AudioFiles/" + date + "/finalAudio.mp3")
    print "Final video duration: " + str(finalClip.duration)
    print "Final audio duration: " + str(audio_background.duration)
    audio_background = mpe.AudioFileClip("//Users/nragis/Desktop/Reddit_Bot/AudioFiles/" + date + "/finalAudio.mp3").set_duration(finalClip.duration)
    audio_background = audio_background.volumex(0.6)
    audio_background = mpe.CompositeAudioClip([audio_background, song.set_duration(finalClip.duration)])
    finalVideo = finalClip.set_audio(audio_background)

    print finalVideo.duration, audio_background.duration
    finalVideo.write_videofile("CompleteVideos/" + date + ".mp4", fps=24, temp_audiofile='temp-audio.m4a', remove_temp=True, codec="libx264", audio_codec="aac", preset='ultrafast',   threads=4)
    
def main():

