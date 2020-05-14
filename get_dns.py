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

if len(sys.argv) == 3:
    sqlite_path = str(sys.argv[1])
    downloaded_path = str(sys.argv[2])

def main(argv):
    sqlite_path = ''
    downloaded_path = ''
    try:
        opts, args = getopt.getopt(argv,"hs:d:")
    except getopt.GetoptError:
        print 'get_dns.py -s <sqlite_path> -d <dowloaded_file_path>'
        sys.exit(2)
    for opt, arg in opts:
        print arg
        if opt == '-h':
            print 'get_dns.py -s <sqlite_path> -d <dowloaded_file_path>'
            sys.exit()
        elif opt == ("-d"):
            downloaded_path = arg
        elif opt == ("-s"):
            sqlite_path = arg
    print 'sqlite path is ', sqlite_path
    print 'downloaded file path is ', downloaded_path

if __name__ == "__main__":
   main(sys.argv[1:])
