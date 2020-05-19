#!/bin/bash
# script to run hnrd across newer log files
# p1=file containing line separated search strings
# p2=output directory
# p2=input directory
set -ex
[[ -n $1 ]] || { echo "Search string file not specified" >&2 ; exit 1 ; }
[[ -n $2 ]] || { echo "Output directory not specified" >&2 ; exit 1 ; }
[[ -n $3 ]] || { echo "Input directory not specified" >&2 ; exit 1 ; }

searchfile="$1"
outdir="$2"
indir="$3"
readme=$outdir/README.md
mydir=$(dirname $(readlink -f $0))

{
    echo "# Analysed DNS data" 
    echo "## Columns"
    echo "\`domain, registeredDate, country, DNShost, virusTotal, quad9, shannon, levenshtein\`"
    echo "## CSV Files"
} > $readme
{
  while read; do
    searchhash=$(base64 -w 0 <<<"$REPLY")

    results=$outdir/${searchhash}.csv
    if [[ -e $results.processed ]] ; then
        findargs="grep -v -F -f $results.processed"
    else
        findargs=cat
    fi

    # find the new domain files which we have not seen before
    find $indir -type f | $findargs | sort | while read f ; do
        # for each newer file, crawl the results
        python ${mydir}/hnrd.py -n -f "$f" -s "$REPLY"
        echo "$f" >>$results.processed
    done >>$results
    echo "- [\`$REPLY\`](${searchhash}.csv)" >> $readme
  done
} < $searchfile
