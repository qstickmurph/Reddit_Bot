from datetime import datetime
import os
from lxml import html
import requests
import re

def main():
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


print "Running getPotentialThreads.py"	
main()	
print "getPotentialThreads.py completed"
	
