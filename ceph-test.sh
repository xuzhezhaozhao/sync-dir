#! /bin/bash

set -e

thread=1024
runtime=60
mods=( "write" "seq" "rand" )

for (( block=4*1024; block<=4*1024*1024; block=block*2 ))
do
for mod in ${mods[@]}
do
for i in `seq 4 11`
do
let bk=block/1024
prefix=ceph_bench${i}_${mod}_thread${thread}_block${bk}_runtime${runtime}
{
    ssh node${i} "rados bench -p bench${i} ${runtime} ${mod} -b ${block} -t ${thread} --no-cleanup > ${prefix}.out 2>${prefix}.err" && echo "${prefix} done!"
} &
echo "${prefix} started"
done
wait
done
done
