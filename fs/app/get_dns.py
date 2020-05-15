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

from __future__ import print_function
import sys, getopt
from datetime import datetime, timedelta
import base64
import requests

def main(argv):
    downloaded_file_path = ''
    # default the date to download to yesterday which will be the most recent
    date=datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')
    try:
        opts, args = getopt.getopt(argv,"hd:D:")
    except getopt.GetoptError:
        print ('get_dns.py -d <dowloaded_file_path> [-D YYYY-MM-DD]')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('get_dns.py -d <dowloaded_file_path> [-D YYYY-MM-DD]')
            sys.exit()
        elif opt == ("-d"):
            downloaded_file_path = arg
        elif opt == "-D":
            date = arg

    print ('downloaded file path is ', downloaded_file_path)

    download(downloaded_file_path,date)

    print ("DOWNLOADED")

def download(downloaded_file_path,d):
    
    outfile=downloaded_file_path + "/newly-registered-domains-"+d+".zip"
    print(outfile)

    b64 = base64.b64encode((d+".zip").encode('ascii'))
    nrd_zip = 'https://whoisds.com//whois-database/newly-registered-domains/{}/nrd'.format(b64.decode('ascii'))
    try:
        resp = requests.get(nrd_zip,stream=True)

        print("Downloading File {} - Size {}...".format(d+'.zip',resp.headers['Content-length']))
        if resp.headers['Content-length']:
            with open(outfile, 'wb') as f:
                for data in resp.iter_content(chunk_size=1024):
                    f.write(data)
    except Exception as exc:
        print(('exception: %s' % (exc)),file=sys.stderr)
        print("File {}.zip does not exist on the remote server.".format(d))
        sys.exit()

if __name__ == "__main__":
    main(sys.argv[1:])
