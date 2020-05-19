#!/bin/bash
# script to graph results files
# p1=file with line separate list of searches
# p2=output directory
# p3=input directory
set -ex
[[ -n $1 ]] || { echo "Searches flile not specified" >&2 ; exit 1 ; }
[[ -n $2 ]] || { echo "Output directory not specified" >&2 ; exit 1 ; }
[[ -n $3 ]] || { echo "Input directory not specified" >&2 ; exit 1 ; }

searchesfile="$1"
outdir="$2"
indir="$3"
mydir=$(dirname $(readlink -f $0))
readme=$outdir/README.md
{
    echo "# Graph plots for DNS registrations over time"
} > $readme

{
while read; do
    searchhash=$(base64 -w 0 <<<"$REPLY")

    results=$indir/$searchhash
    [[ -e $results ]] || { echo "No results available!" >&2 ; exit 1 ; }

    mkdir -p $outdir/$searchhash
    python3 $mydir/generate_graph.py $results $outdir/$searchhash "$REPLY"
    echo "- [\`$REPLY\`]($searchhash/index.html)"
done
} < $searchesfile
