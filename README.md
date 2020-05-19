# hack-a-thon-2020
## "GitHub Actions" and "Current Event DNS Registrations" 

### Defining search terms
The repository contains a [`searches.txt`](searches.txt) file which is a line delimited file of search terms.
A github action is uses this to aquire, process and plot [DNS registrations over time](https://gmckerrell.github.io/hack-a-thon-2020/graphs/)

Editing this file will cause more terms to be used in the analysis.

### Processing pipeline
![Download, Process and Plot DNS data](https://github.com/gmckerrell/hack-a-thon-2020/workflows/Download,%20Process%20and%20Plot%20DNS%20data/badge.svg)

[`dns-hackathon.yml`](https://github.com/gmckerrell/hack-a-thon-2020/blob/master/.github/workflows/dns-hackathon.yml)
defines the processing pipeline.

#### Results

[Show action](https://github.com/gmckerrell/hack-a-thon-2020/actions?query=workflow%3A%22Download%2C+Process+and+Plot+DNS+data%22)

This repository hosts some github actions which run in a Python-3 docker container.

- periodically download the currently registered DNS names.
  - Using [https://whoisds.com](https://whoisds.com) to get daily values for registered DNS names.
- analyses and gathers data on DNS names that match a search pattern
  - Based on [https://github.com/gfek/Hunting-New-Registered-Domains](https://github.com/gfek/Hunting-New-Registered-Domains) to extract data about each name.
- plots the data over time
  - Using [https://plotly.com/python/](https://plotly.com/python/)
- details are cached in the github repostitory to maintain a historic record.
  - Github pages provides the hosting.

### Results
- [Raw CSV data for DNS registrations](https://gmckerrell.github.io/hack-a-thon-2020/results/)
