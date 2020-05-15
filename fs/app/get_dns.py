#!/usr/bin/python3
# update db with latest dns registrations
# p1=path to sqlite
# p2=path to cached downloaded file

# get_dns.py -s <sqlite_path> -d <dowloaded_file_path>

# 1. calculate download URL
# curl https://whoisds.com//whois-database/newly-registered-domains/MjAyMC0wNS0xMC56aXA=/nrd
# $ base64 -d <<<MjAyMC0wNS0xMC56aXA=
# 2020-05-10.zip
# 2. download zip
# 3. unzip
# 4. un-idn
# 5. write to db

import sys, getopt
from datetime import datetime, timedelta
import hnrd

def main(argv):
    dowloaded_file_path = ''
    try:
        opts, args = getopt.getopt(argv,"hd:")
    except getopt.GetoptError:
        print ('get_dns.py -d <dowloaded_file_path>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('get_dns.py -d <dowloaded_file_path>')
            sys.exit()
        elif opt == ("-d"):
            dowloaded_file_path = arg

    print ('downloaded file path is ', dowloaded_file_path)

    download(dowloaded_file_path)

    print ("DOWNLOADED")

def download(dowloaded_file_path):
    yesterday = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')
    
    try:
        hnrd.donwnload_nrd(yesterday)
    except:
        print("Not a correct input (example: 2010-10-10)")
        sys.exit()


if __name__ == "__main__":
    main(sys.argv[1:])
