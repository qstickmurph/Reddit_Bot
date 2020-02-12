from datetime import datetime
from lxml import html
import requests
import time
import json
#from unidecode import unidecode

filterFile = open("/Users/nragis/Desktop/Reddit_Bot/filter.txt", "r")
filterFileLines = filterFile.readlines()
FILTER = [line.decode("utf-8").replace("\n", "").split(": ") for line in filterFileLines]

date = datetime.today().strftime('%m-%d-%y')
NUMBER_OF_COMMENTS = 28
commentNumber = 0

#def RemoveNonAscii(text):
#    return unidecode(unicode(text, encoding = "utf-8"))

def CompileTopX(valueList, lines, x, i, depth):
    for k in range(len(valueList), x):
        valueList.append(0)
#        print "\tAppending 0 to topList"
    compare = int(float(lines[i][2].replace("k", "e3")))

#    print "\tComparing " + str(compare) + " in index: [" + str(i) + "] of depth " + str(depth)
    for k in range(0,x):
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
    
#    print "Called SearchFor(" + basePath + ", " + "tree, " + str(depth) + ")"
#    comments = tree.xpath(basePath + "/div[@class='entry unvoted']/form/div/div[contains(concat(' ', @class, ' '), ' md ')]/p/text()")
    comments = []
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

def main():
    
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
    
    
#    finalString = json.dumps(postData) + "\n\\,\n" + json.dumps(commentList)
#    
#    print "Writing raw data to //Users/nragis/Desktop/Reddit_Bot/ThreadDataRaw/" + date + "_RAW.txt"
# 
#    finalFile = open("//Users/nragis/Desktop/Reddit_Bot/ThreadDataRaw/"+date+"_RAW.txt","a+")
#    finalFile.write(finalString)
#    


print "Running collectData.py"
main()
print "collectData.py complete"
