#!/usr/bin/env python

# Tool to get exchange daily rates from MCB

# Import or build our configuration. Must be FIRST
try:
    import config	# Shared global config variables (DEBUG,...)
except:
    #print('config.py does not exist. Generating...')
    import initConfig	# Check / Update / Create config.py module
    initConfig.initConfiguration()
    
# Import generated module
try:
    import config
except:
    print('config.py initialization has failed. Exiting')
    sys.exit(1)
    
import argparse
import builtins as __builtin__
import datetime
import inspect
import json
import logging
import os
import sys
import time

import myGlobals as mg
from common.utils import myprint, module_path, get_linenumber, color
import dailyRates as mdr

# Arguments parser
def parse_argv():
    desc = 'Get daily rates information from mcb.mu server'

    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("-s", "--server",
                        action="store_true",                        
                        dest="server",
                        default=False,
                        help="run in server mode (as a Web Service)")
    parser.add_argument("-d", "--debug",
                        action="count",
                        dest="debug",
                        default=0,
                        help="print debug messages (to stdout)")
    parser.add_argument("-v", "--verbose",
                        action="store_true", dest="verbose", default=False,
                        help="provides more information")
    parser.add_argument('-f', '--file',
                        dest='logFile',
                        const='',
                        default=None,
                        action='store',
                        nargs='?',
                        metavar='LOGFILE',
                        help="write debug messages to FILE")
    parser.add_argument('-i', '--input',
                        dest='inputFile',
                        const='',
                        default=None,
                        action='store',
                        nargs='?',
                        metavar='INPUTFILE',
                        help="Use data from xlsx input file. File must exists.")
    parser.add_argument("-nc", "--nocache",
                        action="store_true",
                        dest="noCache",
                        default=False,
                        help="Don't use local cache (default=False)")
    parser.add_argument("-k", "--keepResponseFile",
                        action="store_true",
                        dest="keepResponseFile",
                        default=False,
                        help="Keep response file from MCB server (.xlsx file, default=False)")
    parser.add_argument('-D', '--delay',
                        dest='updateDelay',
                        default=1440,
                        type=int,
                        action='store',
                        nargs='?',
                        metavar='DELAY',
                        help="update interval in minutes (default=1440, e.g. 24H)")
    parser.add_argument("-H", "--history",
                        action="store_true", dest="history", default=False,
                        help="Dump history rates")
    parser.add_argument("-I", "--info",
                        action="store_true", dest="version", default=False,
                        help="print version and exit")

    parser.add_argument('dailyRatesDate',
                        action='store',
                        nargs='?',
                        metavar='DATE',
                        help='Daily Rates Date to show (dd/mm/yyyy). Default is today')

    args = parser.parse_args()
    return args


####
def import_module_by_path(path):

    name = os.path.splitext(os.path.basename(path))[0]
    if sys.version_info[0] == 2:
        import imp
        return imp.load_source(name, path)
    elif sys.version_info[:2] <= (3, 4):
        from importlib.machinery import SourceFileLoader
        return SourceFileLoader(name, path).load_module()
    else:
        import importlib.util
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod


#
# Import module. Must be called *after* parsing arguments
#
def importModule(moduleDirPath, moduleName, name):

    modulePath = os.path.join(moduleDirPath, moduleName)
    mod = import_module_by_path(modulePath)
    globals()[name] = mod


####
def main():

    args = parse_argv()

    if args.version:
        print('%s: version %s' % (sys.argv[0], mg.VERSION))
        sys.exit(0)

    config.SERVER   = args.server
    config.VERBOSE  = args.verbose
    config.NO_CACHE = args.noCache
    config.DEBUG    = args.debug
    
    if config.DEBUG:
        myprint(1,
                'config.DEBUG =', config.DEBUG,
                'config.SERVER =', config.SERVER,
                'config.VERBOSE =', config.VERBOSE,
                'config.NO_CACHE =', config.NO_CACHE)

    if args.inputFile:
        myprint(1, "Using input data from %s" % args.inputFile)
        
    if args.keepResponseFile:
        myprint(1, "Will keep response file from server")
        config.KEEPRESPONSEFILE = True
    else:
        config.KEEPRESPONSEFILE = False
        
    if args.history:
        myprint(1, "Dumping history rates")
        config.HISTORY = True
    else:
        config.HISTORY = False

    if args.logFile == None:
        #print('Using stdout')
        pass
    else:
        if args.logFile == '':
            config.LOGFILE = "myMCBDailyRates-debug.txt"
        else:
            config.LOGFILE = args.logFile
        mg.configFilePath = os.path.join(mg.moduleDirPath, config.LOGFILE)
        print('Using log file: %s' % mg.configFilePath)
        try:
            sys.stdout = open(mg.configFilePath, "w")
            sys.stderr = sys.stdout            
        except:
            print('Cannot create log file')

    if args.updateDelay:
        config.UPDATEDELAY = args.updateDelay
    else:
        config.UPDATEDELAY = 1440 # minutes

    if config.SERVER:
        import server as msas
        if config.DEBUG:
            mg.logger.info('server imported (line #%d)' % get_linenumber())

        myprint(0, 'Running in Server mode. Update interval: %d minutes (%s)' % (config.UPDATEDELAY, str(datetime.timedelta(minutes=config.UPDATEDELAY))))
        res = msas.apiServerMain()	# Never returns
        myprint(1, 'API Server exited with code %d' % res)
        sys.exit(res)

    #
    # Standalone mode
    #

    if args.inputFile:
        info = mdr.parseDailyRates(args.inputFile, None)
        myprint(2, json.dumps(info, indent=4))
        sys.exit(0)
        
    if not args.dailyRatesDate:
        dailyRatesDate = datetime.datetime.now().strftime('%d/%m/%Y')	# Today's exchange rate
    else:
        if 'init' in args.dailyRatesDate:
            initConfiguration()
            print('Config initialized. Re-run the command.')
            sys.exit(0)

        dailyRatesDate = args.dailyRatesDate
        
        # Check for a valid date
        try:
            dt = datetime.datetime.strptime(dailyRatesDate, '%d/%m/%Y')
        except:
            print('Invalid date argument %s' % dailyRatesDate)
            sys.exit(1)
        else:
            dailyRatesDate = dt.strftime('%d/%m/%Y')

    myprint(1, 'Looking for daily rates for: %s' % dailyRatesDate)
    
    if config.NO_CACHE:
        # Don't use existing cache. Read data from server (but update local cache)
        res = mdr.getDailyRatesFromMCBServer(dailyRatesDate)
        if res:
            myprint(0, 'Failed to create/update local data cache')
            sys.exit(res)
        
        if config.DEBUG:
            t = os.path.getmtime(mg.dataCachePath)
            dt = datetime.datetime.fromtimestamp(t).strftime('%Y/%m/%d %H:%M:%S')
            myprint(1, f'Cache file updated. Last modification time: {dt}')

    # Display information
    res = mdr.showDailyRatesInfo(dailyRatesDate)
    if res:
        myprint(0, 'Unable to retrieve daily rates information')
        sys.exit(1)

    if config.HISTORY:
        mdr.showHistoryRates()
        
    if args.logFile and args.logFile != '':
        sys.stdout.close()
        sys.stderr.close()

    sys.exit(0)

# Entry point    
if __name__ == "__main__":

    dt_now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    logging.basicConfig(filename='myMCBDailyRates-ws.log', level=logging.INFO)
    mg.logger = logging.getLogger(__name__)
    mg.logger.info('Running at %s. Args: %s' % (dt_now, ' '.join(sys.argv)))
    
    # Absolute pathname of directory containing this module
    mg.moduleDirPath = os.path.dirname(module_path(main))

    # Absolute pathname of data cache file
    mg.dataCachePath = os.path.join(mg.moduleDirPath, '%s' % (mg.DATA_CACHE_FILE))
    
    # Let's go
    main()
