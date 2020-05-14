#!/bin/bash
# script to run hnrd across newer log files
# p1=search string
# p2=output directory
# p3=input directory

[[ -n $1 ]] || { echo "Search string not specified" >&2 ; exit 1 ; }
[[ -n $2 ]] || { echo "Output directory not specified" >&2 ; exit 1 ; }
[[ -n $3 ]] || { echo "Input directory not specified" >&2 ; exit 1 ; }

search="$1"
outdir="$2"
indir="$3"

searchhash=$(base64 -w 0 <<<"$search")

results=$outdir/$searchhash
if [[ -e $results ]] ; then
    findargs="-and -newer $results"
fi

mydir=$(dirname $(readlink -f $0))

# find the new domain files which are newer
find $indir -type f $findargs | while read f ; do
    # for each newer file, crawl the results
    python ${mydir}/hnrd.py -n -f "$f" -s "$search"
done >>$results

# TODO push $results to github preserving timestamp
