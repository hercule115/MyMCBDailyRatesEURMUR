# MyMCBDailyRatesEURMUR
Get MCB Daily Rates for EURO/MUR

Get daily rates for Euro currency from **MCB Server**

The goal of this tool is to retrieve the daily rates information provided by https://www.mcb.mu.

Results are provided as a JSON entity containing the following information:

- Date,
- Currency code (EUR),
- Buying rate for TT,
- Buying rate for TC/DD,
- Buying rate for NOTES,
- Selling rate for TT,
- Selling rate for TC/DD,
- Selling rate for NOTES,

2 modes are available:
- Local/Standalone mode: You run the tool locally on the system where the tool is installed. If no date is provided on the command line, today's date is used.  
- Remote mode: You retrieve the information over the network using the URL: http://server:5005/mymcbdailyrates/api/v1.0/dailyrates/[mmddyy].  
  If the date is not provided, today's date is used. 

## Examples:

### Stand-alone mode

    python myMCBDailyRates.py -h
    usage: myMCBDailyRates.py [-h] [-s] [-d] [-v] [-f [LOGFILE]] [-i [INPUTFILE]] [-nc] [-D [DELAY]] [-I] [DATE]

    Get daily rates information from mcb.mu server

    positional arguments:
      DATE                  Daily Rates Date to show (dd/mm/yyyy). Default is today

    optional arguments:
      -h, --help            show this help message and exit
      -s, --server          run in server mode (as a Web Service)
      -d, --debug           print debug messages (to stdout)
      -v, --verbose         provides more information
      -f [LOGFILE], --file [LOGFILE]
                            write debug messages to FILE
      -i [INPUTFILE], --input [INPUTFILE]
                            Use data from xlsx input file. File must exists.
      -nc, --nocache        Don't use local cache (default=False)
      -D [DELAY], --delay [DELAY]
                            update interval in minutes (default=1440, e.g. 24H)
      -I, --info            print version and exit


    python myMCBDailyRates.py -v
    Daily Rates for : Mon 26 Dec, 2022 
    Currency code: EUR
    Buying TT      : 45.6  
    Buying TC/DD   : 45.49 
    Buying NOTES   : 45.16 
    Selling TT     : 46.97 
    Selling TC/DD  : 46.97 
    Selling NOTES  : 46.97 

