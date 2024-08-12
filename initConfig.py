#!/usr/bin/env python

import builtins as __builtin__
import inspect
import os
import sys
import time
import argparse
import getpass

import base64
import authinfo

import myGlobals as mg

def _checkModule(fields):
    for f in fields:
        ftype = f[0]
        if ftype == 'a': # Auth parameter
            fname = f[1][0]
        else:
            fname = f[1]

        try:
            a = getattr(config, "%s" % fname)
            if a == '':
                print('Invalid config.py file (attribute %s is nil)' % fname)
                return -1
            continue
        except:
            print('Invalid config.py file (Missing attribute %s)' % fname)
            return -1
    return 0
        
def _createDict(fields, opt=True):
    d = dict()
    for f in fields:
        ftype = f[0]
        fname = f[1]
        
        if ftype == 'a':
            v = getAuthParms(f, opt)	# Auth parameters
            d[fname[0]] = v
        else:
            v = getParm(f, opt)		# Other parameters
            d[fname] = v
    return d

# Encode Auth parameters
def getAuthParms(field, opt): #('a',['NOIP_AUTH', ('s','NOIP_USERNAME'), ('p','NOIP_PASSWORD')])
    type    = field[0]  # 'a'
    params  = field[1]  # ['NOIP_AUTH', ('s','NOIP_USERNAME'), ('p','NOIP_PASSWORD')]

    username = getParm(params[1], opt) # ('s','NOIP_USERNAME')
    password = getParm(params[2], opt) # ('p','NOIP_PASSWORD')
    
    auth = authinfo.ApiAuth(username, password)
    return "'{}'".format(auth.base64Key.decode('utf-8'))

def getParm(field, opt): # ('b','DEBUG', 'True')
    ftype   = field[0]  #'b'
    fname   = field[1]  #'DEBUG'
    
    if ftype == 'b':
        v = input('%s (True/False): ' % fname)
        if opt:
            default = field[2]  #'True'
            if v != '':
                while v!='False' and v!='True':
                    v = input('%s (True/False): ' % fname)
            else:
                v = default.lower() in ['true', '1', 't', 'y', 'yes']
        else: # Mandatory. Can't be null
            while not v or (v!='False' and v!='True'):
                v = input('%s (True/False): ' % fname)
        #d[fname]=v
        return v

    elif ftype == 'p':
        v = getpass.getpass(prompt='%s: ' % fname)
        if not opt:
            while not v:
                v = getpass.getpass(prompt='%s (string): ' % fname)
        return "'{}'".format(v)
                
    elif ftype == 's':
        v = input('%s (string): ' % fname)
        if not opt:
            while not v:
                v = input('%s: ' % fname)
        return "'{}'".format(v)
            
    elif ftype == 'd':
        v = input('%s (decimal): ' % fname)
        while not v.isnumeric():
            v = input('%s (decimal): ' % fname)
        if not opt:
            while not v:
                v = input('%s: ' % fname)
                while not v.isnumeric():
                    v = input('%s (decimal): ' % fname)
        return v
    
def createConfig(mandatoryFields, optionalFields):
    print('** Setting mandatory attributes **')
    m = _createDict(fields=mandatoryFields, opt=False)
    print('** Setting optional attributes **')
    o = _createDict(fields=optionalFields, opt=True)

    #print(m)
    #print(o)
    
    # Create config.py with collected information
    try:
        with open('config.py', 'w') as configFile:
            configFile.write('# Mandatory parameters\n')
            for k,v in m.items():
                configFile.write("%s = %s\n" % (k,v))

            configFile.write('\n')
            
            configFile.write('# Optional parameters (may be null)\n')
            for k,v in o.items():
                configFile.write("%s = %s\n" % (k,v))
                
    except IOError as e:
        msg = "I/O error: Creating %s: %s" % ('config.py', "({0}): {1}".format(e.errno, e.strerror))
        print(msg)
        sys.exit(1)

def initConfig(mandatoryFields, optionalFields, force):
    if force:
        createConfig(mandatoryFields, optionalFields)
        return
    
    try:
        import config
        globals()['config'] = config
    except:
        print('Import config module has failed. Creating config.py')
        createConfig(mandatoryFields, optionalFields)
    else:
        #return
        if config.VERBOSE:
            print('Checking existing config.py')
            ret = _checkModule(fields=mandatoryFields)
            if ret < 0:
                createConfig(mandatoryFields, optionalFields)

#
# Create configuration file config.py
#
def initConfiguration():
    # Create config.py with Mandatory/Optional fields
    print('Creating config.py with Mandatory/Optional fields')
    
    initConfig(mg.mandatoryFields, mg.optionalFields, True)
    return 0


# Entry point    
if __name__ == "__main__":
    mandatoryFields = [('a',['SOSH_AUTH', ('s','SOSH_USERNAME'), ('p','SOSH_PASSWORD')])]

    optionalFields  = [('b','VERBOSE', 'True'),
                       ('d','DEBUG', 0),
                       ('s','LOGFILE')]
    
    initConfig(mandatoryFields, optionalFields, True)
