#!/bin/bash
# script to graph results files
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

results=$indir/$searchhash
[[ -e $results ]] || { echo "No results available!" >&2 ; exit 1 ; }
mydir=$(dirname $(readlink -f $0))

mkdir -p $outdir/$searchhash
python3 $mydir/generate_graph.py $results $outdir/$searchhash 640 480
