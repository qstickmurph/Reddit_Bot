from datetime import datetime
import os
import random

def main():
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
       
print "Running chooseThread.py" 
main()
print "chooseThread.py completed"
