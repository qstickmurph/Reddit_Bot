import os
from datetime import datetime
import time

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
