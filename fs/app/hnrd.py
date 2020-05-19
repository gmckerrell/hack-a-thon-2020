from __future__ import print_function

import concurrent.futures
import dns.resolver
import whois
import time
import zipfile
import os, os.path
import re
import argparse
import sys
import requests
import re
from colorama import init
from termcolor import colored
from bs4 import BeautifulSoup
import warnings
import json
import Levenshtein
import tldextract
import base64
import datetime

try:
  # python 2: 'unicode' is built-in
  unicode
except  NameError:
  unicode=str

try:
    from sets import Set as set
except ModuleNotFoundError:
    pass

init()

warnings.filterwarnings("ignore")

def DNS_Records(domain):

    RES={}
    MX=[]
    NS=[]
    A=[]
    AAAA=[]
    SOA=[]
    CNAME=[]

    resolver = dns.resolver.Resolver()
    resolver.timeout = 1
    resolver.lifetime = 1

    rrtypes=['A','MX','NS','AAAA','SOA']
    for r in rrtypes:
        try:
            Aanswer=resolver.query(domain,r)
            for answer in Aanswer:
                if r=='A':
                    A.append(answer.address)
                    RES.update({r:A})
                if r=='MX':
                    MX.append(answer.exchange.to_text()[:-1])
                    RES.update({r:MX})
                if r=='NS':
                    NS.append(answer.target.to_text()[:-1])
                    RES.update({r:NS})
                if r=='AAAA':
                    AAAA.append(answer.address)
                    RES.update({r:AAAA})
                if r=='SOA':
                    SOA.append(answer.mname.to_text()[:-1])
                    RES.update({r:SOA})
        except dns.resolver.NXDOMAIN:
            pass
        except dns.resolver.NoAnswer:
            pass
        except dns.name.EmptyLabel:
            pass
        except dns.resolver.NoNameservers:
            pass
        except dns.resolver.Timeout:
            pass
        except dns.exception.DNSException:
            pass
    return RES

def get_DNS_record_results():
    global IPs
    global ALLRESULTS
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(DOMAINS)) as executor:
            future_to_domain={executor.submit(DNS_Records, domain):domain for domain in DOMAINS}
            for future in concurrent.futures.as_completed(future_to_domain):
                dom=future_to_domain[future]
                ALLRESULTS[dom]["SOA"]=""
                try:
                    DNSAdata = future.result()
                    for k,v in DNSAdata.items():
                        if k == "SOA":
                            ALLRESULTS[dom]["SOA"] = v[0]
                        for ip in v:
                            aa=re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",ip)
                            if aa:
                                ALLRESULTS[dom]["IP"]=ip
                                IPs.append(ip)
                except Exception as exc:
                    print(('%r generated an exception: %s' % (dom, exc)),file=sys.stderr)
    except ValueError:
        pass
    return IPs

def diff_dates(date1, date2):
    return abs((date2-date1).days)

def whois_domain(domain_name):
    import time
    import datetime
    RES={}

    try:
        w_res=whois.whois(domain_name)
        name=w_res.name
        creation_date=w_res.creation_date
        emails=w_res.emails
        registrar=w_res.registrar
        updated_date=w_res.updated_date
        expiration_date=w_res.expiration_date

        if isinstance(creation_date, datetime.datetime) or isinstance(expiration_date, datetime.datetime) or  isinstance(updated_date, datetime.datetime):
            current_date=datetime.datetime.now()
            res=diff_dates(current_date,creation_date)
            RES.update({"creation_date":creation_date, \
                "creation_date_diff":res,\
                "emails":emails,\
                "name":name,\
                "registrar":registrar,\
                "updated_date":updated_date,\
                "expiration_date":expiration_date})

        elif isinstance(creation_date, list) or isinstance(expiration_date, list) or  isinstance(updated_date, list):
            creation_date=w_res.creation_date[0]
            updated_date=w_res.updated_date[0]
            expiration_date=w_res.expiration_date[0]
            current_date=datetime.datetime.now()
            res=diff_dates(current_date,creation_date)

            RES.update({"creation_date":creation_date, \
                "creation_date_diff":res,\
                "emails":emails,\
                "name":name,\
                "registrar":registrar,\
                "updated_date":updated_date,\
                "expiration_date":expiration_date})

        time.sleep(2)
    except TypeError:
        pass
    except whois.parser.PywhoisError:
        print(colored("No match for domain: {}.".format(domain_name),'red'),file=sys.stderr)
    except AttributeError:
        pass
    return RES

def IP2CIDR(ip):
    from ipwhois.net import Net
    from ipwhois.asn import IPASN

    net = Net(ip)
    obj = IPASN(net)
    results = obj.lookup()
    return results

def get_IP2CIDR():
    global ALLRESULTS
    global IP2DOMAIN
    global IPs
    ipresults={}
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(IPs)) as executor:
            future_to_ip2asn={executor.submit(IP2CIDR, ip):ip for ip in IPs}
            for future in concurrent.futures.as_completed(future_to_ip2asn):
                ipaddress=future_to_ip2asn[future]
                try:
                    data = future.result()
                    for k,v in data.items():
                                                if k == "asn_country_code":
                                                    ipresults[ipaddress]=v
                except Exception as exc:
                    print(('%r generated an exception: %s' % (ipaddress, exc)),file=sys.stderr)

            for d in ALLRESULTS:
                    if ("IP" in ALLRESULTS[d]) and (ALLRESULTS[d]["IP"] in ipresults):
                        ALLRESULTS[d]["CountryCode"] = ipresults[ALLRESULTS[d]["IP"]]

    except ValueError:
        pass

def get_WHOIS_results(today):
    global NAMES
    global ALLRESULTS
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(DOMAINS)) as executor:
            future_to_whois_domain={executor.submit(whois_domain, domain):domain for domain in DOMAINS}
            for future in concurrent.futures.as_completed(future_to_whois_domain):
                dwhois=future_to_whois_domain[future]
                ALLRESULTS[dwhois]["Created"]=today
                try:
                    whois_data = future.result()
                    if whois_data:
                        for k,v in whois_data.items():
                            if 'creation_date' in k:
                                ALLRESULTS[dwhois]["Created"]=whois_data.get('creation_date').strftime("%Y-%m-%d")

                except Exception as exc:
                    print(('%r generated an exception: %s' % (dwhois, exc)),file=sys.stderr)
    except ValueError:
        pass
    return NAMES

def EmailDomainBigData(name):
    url = "http://domainbigdata.com/name/{}".format(name)
    session = requests.Session()
    session.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:42.0) Gecko/20100101 Firefox/42.0'
    email_query = session.get(url)
    email_soup = BeautifulSoup(email_query.text,"html5lib")
    emailbigdata = email_soup.find("table",{"class":"t1"})
    return emailbigdata

def get_EmailDomainBigData():
    CreatedDomains=[]
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(NAMES)) as executor:
            future_to_rev_whois_domain={executor.submit(EmailDomainBigData, name): name for name in set(NAMES)}
            for future in concurrent.futures.as_completed(future_to_rev_whois_domain):
                namedomaininfo=future_to_rev_whois_domain[future]
                try:
                    rev_whois_data = future.result()
                    print("  \_", colored(namedomaininfo,'cyan'))
                    CreatedDomains[:] = []
                    if rev_whois_data is not None:
                        for row in rev_whois_data.findAll("tr"):
                            if row:
                                cells = row.findAll("td")
                                if len(cells) == 3:
                                    CreatedDomains.append(colored(cells[0].find(text=True)))

                        print("    \_", colored(str(len(CreatedDomains)-1) + " domain(s) have been created in the past",'yellow'))
                    else:
                        print("    \_", colored(str(len(CreatedDomains)) + " domain(s) have been created in the past",'yellow'))
                except Exception as exc:
                    print(('%r generated an exception: %s' % (namedomaininfo, exc)),file=sys.stderr)
    except ValueError:
        pass

def crt(domain):
    parameters = {'q': '%.{}'.format(domain), 'output':'json'}
    headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:52.0) Gecko/20100101 Firefox/52.0','content-type': 'application/json'}
    response = requests.get("https://crt.sh/?",params=parameters, headers=headers)
    content=response.content.decode('utf-8')
    data = json.loads("[{}]".format(content.replace('}{', '},{')))
    return data

def getcrt():
    global ALLRESULTS
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(NAMES)) as executor:
            future_to_crt={executor.submit(crt, domain):domain for domain in DOMAINS}
            for future in concurrent.futures.as_completed(future_to_crt):
                d=future_to_crt[future]
                ALLRESULTS[d]["Certificates"]=1
                try:
                    crtdata=future.result()
                    if len(crtdata)>0:
                        ALLRESULTS[d]["Certificates"]=0
                except Exception as exc:
                    pass
    except ValueError:
        pass

def VTDomainReport(domain):
        parameters = {'domain': domain, 'apikey': 'f76bdbc3755b5bafd4a18436bebf6a47d0aae6d2b4284f118077aa0dbdbd76a4'}
        headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:52.0) Gecko/20100101 Firefox/52.0'}
        response = requests.get('https://www.virustotal.com/vtapi/v2/domain/report', params=parameters,headers=headers)
        response_dict = response.json()
        return response_dict

def getVTDomainReport():
    global ALLRESULTS
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(DOMAINS)) as executor:
            future_to_vt={executor.submit(VTDomainReport, domain):domain for domain in DOMAINS}
            for future in concurrent.futures.as_completed(future_to_vt):
                d=future_to_vt[future]
                try:
                    ALLRESULTS[d]["VirusTotal"]=0
                    vtdata = future.result()
                    if vtdata['response_code']==1:
                        if 'detected_urls' in vtdata:
                            if len(vtdata['detected_urls'])>0:
                                ALLRESULTS[d]["VirusTotal"]+=1
                        if 'detected_downloaded_samples' in vtdata:
                            if len(vtdata['detected_downloaded_samples'])>0:
                                ALLRESULTS[d]["VirusTotal"]+=1
                        if 'detected_communicating_samples' in vtdata:
                            if len(vtdata['detected_communicating_samples'])>0:
                                ALLRESULTS[d]["VirusTotal"]+=1
                        if 'categories' in vtdata:
                            if len(vtdata['categories'])>0:
                                ALLRESULTS[d]["VirusTotal"]+=1
                        if 'subdomains' in vtdata:
                            if len(vtdata['subdomains'])>0:
                                ALLRESULTS[d]["VirusTotal"]+=1
                        if 'resolutions' in vtdata:
                            if len(vtdata['resolutions'])>0:
                                ALLRESULTS[d]["VirusTotal"]+=1
                except Exception as exc:
                    ALLRESULTS[d]["VirusTotal"]+=1
    except ValueError:
        pass

def quad9(domain):
    resolver = dns.resolver.Resolver()
    resolver.nameservers = ['9.9.9.9']
    resolver.timeout = 1
    resolver.lifetime = 1

    try:
        Aanswers = resolver.query(domain, 'A')
    except dns.resolver.NXDOMAIN:
        return "Blocked"
    except dns.resolver.NoAnswer:
        pass
    except dns.name.EmptyLabel:
        pass
    except dns.resolver.NoNameservers:
        pass
    except dns.resolver.Timeout:
        pass
    except dns.exception.DNSException:
        pass

def get_quad9_results():
    global ALLRESULTS
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(DOMAINS)) as executor:
            future_to_quad9={executor.submit(quad9, domain):domain for domain in DOMAINS}
            for future in concurrent.futures.as_completed(future_to_quad9):
                quad9_domain=future_to_quad9[future]
                ALLRESULTS[quad9_domain]["quad9"]=0
                try:
                    QUAD9NXDOMAIN = future.result()
                    if QUAD9NXDOMAIN is not None:
                        ALLRESULTS[quad9_domain]["quad9"]=1
                    else:
                        ALLRESULTS[quad9_domain]["quad9"]=1
                except Exception as exc:
                    print(('%r generated an exception: %s' % (quad9_domain, exc)),file=sys.stderr)
    except ValueError:
        pass

def shannon_entropy(domain):
    import math


    stList = list(domain)
    alphabet = list(set(domain)) # list of symbols in the string
    freqList = []

    for symbol in alphabet:
        ctr = 0
        for sym in stList:
            if sym == symbol:
                ctr += 1
        freqList.append(float(ctr) / len(stList))

    # Shannon entropy
    ent = 0.0
    for freq in freqList:
        ent = ent + freq * math.log(freq, 2)
    ent = -ent
    return ent

def donwnload_nrd(d):
    if not os.path.isfile(d+".zip"):
        b64 = base64.b64encode((d+".zip").encode('ascii'))
        nrd_zip = 'https://whoisds.com//whois-database/newly-registered-domains/{}/nrd'.format(b64.decode('ascii'))
        try:
            resp = requests.get(nrd_zip,stream=True)

            print("Downloading File {} - Size {}...".format(d+'.zip',resp.headers['Content-length']))
            if resp.headers['Content-length']:
                with open(d+".zip", 'wb') as f:
                    for data in resp.iter_content(chunk_size=1024):
                        f.write(data)
                try:
                    zip = zipfile.ZipFile(d+".zip")
                    zip.extractall()
                    os.rename("domain-names.txt",d+".txt")
                except:
                    print("File is not a zip file.")
                    sys.exit()
        except:
            print("File {}.zip does not exist on the remote server.".format(d))
            sys.exit()

def bitsquatting(search_word):
    out = []
    masks = [1, 2, 4, 8, 16, 32, 64, 128]

    for i in range(0, len(search_word)):
        c = search_word[i]
        for j in range(0, len(masks)):
            b = chr(ord(c) ^ masks[j])
            o = ord(b)
            if (o >= 48 and o <= 57) or (o >= 97 and o <= 122) or o == 45:
                out.append(search_word[:i] + b + search_word[i+1:])
    return out

def hyphenation(search_word):
    out=[]
    for i in range(1, len(search_word)):
        out.append(search_word[:i] + '-' + search_word[i:])
    return out

def subdomain(search_word):
    out=[]
    for i in range(1, len(search_word)):
        if search_word[i] not in ['-', '.'] and search_word[i-1] not in ['-', '.']:
            out.append(search_word[:i] + '.' + search_word[i:])
    return out

if __name__ == '__main__':
    DOMAINS=[]
    IPs=[]
    ALLRESULTS={}
    IP2DOMAIN={}
    NAMES=[]
    parser = argparse.ArgumentParser(prog="hnrd.py",description='hunting newly registered domains')
    parser.add_argument("-n", action="store_true", dest='nodownload', help="skip download just use date arg as existing file")
    parser.add_argument("-f", action="store", dest='date', help="date [format: year-month-date]",required=True)
    parser.add_argument("-s", action="store", dest='search',help="search a keyword",required=True)
    parser.add_argument("-v", action="version",version="%(prog)s v1.0")
    args = parser.parse_args()

    if (args.nodownload != True):
        regexd=re.compile('[\d]{4}-[\d]{2}-[\d]{2}$')
        matchObj=re.match(regexd,args.date)
        if matchObj:
            donwnload_nrd(args.date)
        else:
            print("Not a correct input (example: 2010-10-10)")
            sys.exit()

    try:
        f = zipfile.ZipFile(args.date,'r').open("domain-names.txt","r")
    except Exception as e:
        print("No such file or directory domain-names.txt found")
        sys.exit()

    # work out the date in the filename
    # then subtract 1 day
    # failing that, assume today
    regexd=re.compile('.*([\d]{4})-([\d]{2})-([\d]{2})\.zip$')
    matchObj=re.match(regexd,args.date)
    if matchObj:
        filedate=datetime.datetime(int(matchObj.group(1)),int(matchObj.group(2)),int(matchObj.group(3)),0,0)
    else:
        filedate=datetime.datetime.now()
    # the file date is actually a day after the registration
    filedate = filedate - datetime.timedelta(1)
    today=filedate.strftime('%Y-%m-%d')

    bitsquatting_search=bitsquatting(args.search)
    hyphenation_search=hyphenation(args.search)
    subdomain_search=subdomain(args.search)
    search_all=bitsquatting_search+hyphenation_search+subdomain_search
    search_all.append(args.search)

    d2={}
    RE_list=[re.compile(search) for search in search_all]
    for r in f:
        row = unicode(r, "utf-8").strip("\r\n") # convert bytes into string
        for RE in RE_list:
            match = RE.match(row)
            if match:
                d2[row]=row

    for domain in d2.keys():
        DOMAINS.append(domain)

    for domain in DOMAINS:
        ALLRESULTS[domain]={}
        ALLRESULTS[domain]["CountryCode"]="?"

    start = time.time()

    print("[*]-Retrieving DNS Record(s) Information",file=sys.stderr)
    get_DNS_record_results()

    print("[*]-Retrieving IP2ASN Information",file=sys.stderr)
    get_IP2CIDR()

    print("[*]-Retrieving WHOIS Information",file=sys.stderr)
    get_WHOIS_results(today)

    #print("[*]-Retrieving Reverse WHOIS (by Name) Information [Source https://domainbigdata.com]",file=sys.stderr)
    #get_EmailDomainBigData()

    print("[*]-Retrieving Certficates [Source https://crt.sh]",file=sys.stderr)
    getcrt()

    print("[*]-Retrieving VirusTotal Information",file=sys.stderr)
    getVTDomainReport()

    print("[*]-Check domains against QUAD9 service",file=sys.stderr)
    get_quad9_results()

    print("[*]-Calculate Shannon Entropy Information",file=sys.stderr)
    for domain in DOMAINS:
        ALLRESULTS[domain]["shannon"]=100*shannon_entropy(domain)

    print("[*]-Calculate Levenshtein Ratio",file=sys.stderr)
    for domain in DOMAINS:
        ext_domain=tldextract.TLDExtract(cache_file=False)(domain)
        LevWord1=ext_domain.domain
        LevWord2=args.search
        ALLRESULTS[domain]["levenshtein"]=100*Levenshtein.ratio(LevWord1, LevWord2)

    #print("#domain,created,country,soa,vt,quad9,shannon,lev")
    for d in DOMAINS:
        print("%s,%s,%s,%s,%d,%d,%d,%d"%(d,ALLRESULTS[d]["Created"],ALLRESULTS[d]["CountryCode"],ALLRESULTS[d]["SOA"],ALLRESULTS[d]["VirusTotal"],ALLRESULTS[d]["quad9"],ALLRESULTS[d]["shannon"],ALLRESULTS[d]["levenshtein"]))

