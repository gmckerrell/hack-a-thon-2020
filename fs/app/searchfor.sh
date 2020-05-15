#!/bin/bash
# script to run hnrd across newer log files
# p1=search string
# p2=output directory
# p3=input directory
set -ex
[[ -n $1 ]] || { echo "Search string not specified" >&2 ; exit 1 ; }
[[ -n $2 ]] || { echo "Output directory not specified" >&2 ; exit 1 ; }
[[ -n $3 ]] || { echo "Input directory not specified" >&2 ; exit 1 ; }

search="$1"
outdir="$2"
indir="$3"

searchhash=$(base64 -w 0 <<<"$search")

results=$outdir/$searchhash
if [[ -e $results ]] ; then
    findargs="grep -v -F -f $results.processed"
else
    findargs=cat
fi

mydir=$(dirname $(readlink -f $0))

# find the new domain files which we have not seen before
find $indir -type f | $findargs | sort | while read f ; do
    # for each newer file, crawl the results
    python ${mydir}/hnrd.py -n -f "$f" -s "$search"
    echo "$f" >>$results.processed
done >>$results

# TODO push $results and $results.processed back to repo
