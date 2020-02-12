import os
from shutil import copyfile
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageOps
import textwrap
import moviepy.editor as mpe
import random

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

date = datetime.today().strftime('%m-%d-%y')
frameNumber = 0

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
    
    
    
    

def main():
    
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
            
            
            

    """
*    for comment in commentData:
*        page = 0
*        sentenceList = SeperateSentences(comment[0])
*        displayText = ""
*        print "\t\t\tCreating " + str(len(sentenceList)) + " segments out of comment " + str(commentData.index(comment))
*        for sentence in sentenceList:
*            if len(displayText + sentence + ".") < (LINES_PER_SCREEN*CHAR_PER_LINE):
*                displayText += sentence[:-1] + sentence[-1:].replace(" ", "") + "."
*            else:
*                displayText = sentence[:-1] + sentence[-1:].replace(" ", "") + "."
*                page += 1
*            CreateCommentFrame(displayText, comment, len(comment[0]), page)
*            segment = mpe.ImageClip("//Users/nragis/Desktop/Reddit_Bot/Frames/frame" + str(frameNumber) + ".jpg").set_duration(((float)(frameData[frameNumber + 1]) + shortPauseLength)/1000.0)
*            finalClip = mpe.concatenate_videoclips([finalClip, segment])
*            os.remove("Frames/frame" + str(frameNumber) + ".jpg")
*            frameNumber += 1 
*        if (comment[3] == '0'):
*            finalClip = mpe.concatenate_videoclips([finalClip, seperatorClip])
*        else:
*            finalClip = mpe.concatenate_videoclips([finalClip, longPauseClip])
    """
    
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
    

print "Running videoCreate.py"
main()
print "videoCreate.py complete"
