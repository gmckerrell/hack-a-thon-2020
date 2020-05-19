#!/bin/bash
# script to run hnrd across newer log files
# STDIN line separated search strings
# p1=output directory
# p2=input directory
set -ex
[[ -n $1 ]] || { echo "Output directory not specified" >&2 ; exit 1 ; }
[[ -n $2 ]] || { echo "Input directory not specified" >&2 ; exit 1 ; }

outdir="$1"
indir="$2"
readme=$outdir/README.md
mydir=$(dirname $(readlink -f $0))

echo "# CSV files with DNS data" > $readme
while read; do
    searchhash=$(base64 -w 0 <<<"$REPLY")

    results=$outdir/$searchhash
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
    echo "- [`$REPLY`]($searchhash)" >> $readme
done
