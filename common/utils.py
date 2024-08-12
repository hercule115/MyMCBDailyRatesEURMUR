import builtins as __builtin__
from csv import reader
from datetime import datetime
import inspect
import json
import os
import sys
import requests
import time
import unicodedata

import myGlobals as mg
import config

####
class color:
    PURPLE    = '\033[95m'
    CYAN      = '\033[96m'
    DARKCYAN  = '\033[36m'
    BLUE      = '\033[94m'
    GREEN     = '\033[92m'
    YELLOW    = '\033[93m'
    RED       = '\033[91m'
    BOLD      = '\033[1m'
    UNDERLINE = '\033[4m'
    END       = '\033[0m'


####        
def module_path(local_function):

    ''' returns the module path without the use of __file__.  
    Requires a function defined locally in the module.
    from http://stackoverflow.com/questions/729583/getting-file-path-of-imported-module'''
    return os.path.abspath(inspect.getsourcefile(local_function))


def myprint(level, *args, **kwargs):

    """My custom print() function."""
    # Adding new arguments to the print function signature 
    # is probably a bad idea.
    # Instead consider testing if custom argument keywords
    # are present in kwargs

    if level <= config.DEBUG:
        __builtin__.print('%s%s()%s:' % (color.BOLD, inspect.stack()[1][3], color.END), *args, **kwargs)


# Bubble sort function to sort a list of tuples
# Sort criteria (1st field of each tuple) is a time representation in the form "%H:%M"
def bubbleSort(elements):

    swapped = False
    # Looping from size of array from last index[-1] to index[0]
    for n in range(len(elements)-1, 0, -1):
        for i in range(n):
            if time.strptime(elements[i][0], "%H:%M") > time.strptime(elements[i+1][0], "%H:%M"):
                swapped = True
                # swapping data if the element is less than next element in the array
                elements[i], elements[i + 1] = elements[i + 1], elements[i]
        if not swapped:
            # exiting the function if we didn't make a single swap
            # meaning that the array is already sorted.
            return
        # reset swap flag
        swapped = False


# Leave the last 'l' characters of 'text' unmasked
def masked(text, l):

    nl=-(l)
    return text[nl:].rjust(len(text), "#")


####
def dumpListToFile(fname, aList):

    # open file in write mode
    with open(fname, 'w') as fp:
        for item in aList:
            # write each item on a new line
            fp.write("%s\n" % item)
        print('Done')


def dumpListOfListToFile(fname, aList):

    e = list()
    # open file in write mode
    with open(fname, 'w') as fp:
        for item in aList:
            #print(item,type(item))
            e.clear()
            for ele in item:
                e.append(unicodedata.normalize("NFKD", ele))
                
            # write each item on a new line
            fp.write("%s\n" % e)
        #print('Done')

        
def dumpToFile(fname, plainText):

    myprint(1, 'Creating/Updating %s, length %d' % (fname, len(plainText)))
    try:
        out = open(fname, 'wb')
        out.write(plainText)
        out.close()
    except IOError as e:
        msg = "I/O error: Creating %s: %s" % (fname, "({0}): {1}".format(e.errno, e.strerror))
        myprint(1,msg)
        return -1
    return 0


####
def dumpJsonToFile(fname, textDict):

    myprint(1,'Creating/Updating %s' % fname)
    myprint(1,'Dict text length: %d, Plain text length: %d' % (len(textDict), len(str(textDict))))
    #myprint(1,textDict) 
    try:
        out = open(fname, 'w')
        out.write(json.dumps(textDict, ensure_ascii=False))
        out.close()
    except IOError as e:
        msg = "I/O error: Creating %s: %s" % (fname, "({0}): {1}".format(e.errno, e.strerror))
        myprint(1,msg)
        return -1
    return 0


####
def humanBytes(size):

    power = float(2**10)     # 2**10 = 1024
    n = 0
    power_labels = {0 : 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size > power:
        size = float(size / power)
        n += 1
    return '%s %s' % (('%.2f' % size).rstrip('0').rstrip('.'), power_labels[n])


####
def isFileOlderThanXMinutes(file, minutes=1): 

    fileTime = os.path.getmtime(file) 
    # Check against minutes parameter
    return ((time.time() - fileTime) > (minutes *  60))


####
def get_linenumber():

    cf = inspect.currentframe()
    return cf.f_back.f_lineno


####
def findBetween(s, first, last):

    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""


####
def sleepUntil(sleep_until):

    # Adds current date to the string sleep_until.
    sleep_until = time.strftime("%m/%d/%Y " + sleep_until, time.localtime())
    # Current time in seconds from the epoch time.
    now_epoch = time.time()
    # Sleep_until time in seconds from the epoch time.
    alarm_epoch = time.mktime(time.strptime(sleep_until, "%m/%d/%Y %I:%M%p"))

    #If we are already past the alarm time today.
    if now_epoch > alarm_epoch:
        # Adds a day worth of seconds to the alarm_epoch, hence setting it to next day instead.
        alarm_epoch = alarm_epoch + 86400
        myprint(1, 'Alarm time is behind, sleeping until tomorrow: {}...'.format(alarm_epoch))

    dt = datetime.fromtimestamp(alarm_epoch).strftime('%Y/%m/%d %H:%M:%S')        
    myprint(1, 'Sleeping for: %d seconds (%s)' % (alarm_epoch - now_epoch, dt))

    # Sleeps until the next time the time is the set time, whether it's today or tomorrow.
    time.sleep(alarm_epoch - now_epoch)


####
def diff_month(d1, d2):

    return (d1.year - d2.year) * 12 + d1.month - d2.month
