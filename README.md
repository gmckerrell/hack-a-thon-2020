# hack-a-thon-2020
![Hello World](https://github.com/gmckerrell/hack-a-thon-2020/workflows/Hello%20World/badge.svg)
[DNS Plot for "covid"](graphs/Y292aWQK/index.html)

## Requirements

* install whois binary: `sudo apt install whois`
* install python2 requirements: `sudo pip install -r hnrd-requirements-python2.txt --proxy=http://www-proxy.megqa.nai.com:3128` (skip the if you are running outside the corporate network)

(I tried this with python3 but that failed on installing "set" which doesn't install when behind the proxy)

## Run get_dns.py

...

## Run hnrd to process collected file

```
HTTPS_PROXY=$https_proxy HTTP_PROXY=$http_proxy python hnrd.py -n -f $DOWNLOADDIR/newly-registered-domains-2020-05-11.txt -s bananas
```

With $DOWNLOADDIR set appropriately

(skip the proxy stuff if you are not on VPN)
