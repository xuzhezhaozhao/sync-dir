#! /bin/bash

set -e

#threads=( 1 2 4 8 16 32 64 128 256 )
threads=( 1024 )
#mods=( "write" "seq" "rand" )
mods=( "write" )
runtime=1000
for thread in ${threads[@]}
do
    for (( block=4*1024; block<=4*1024; block=block*2 ))
    do
        for mod in ${mods[@]}
        do
            for i in `seq 4 11`
            do
                let bk=block/1024
                prefix=ceph_bench${i}_${mod}_thread${thread}_block${bk}_runtime${runtime}
                {
                    ssh node${i} "rados bench -p bench${i} ${runtime} ${mod} -b ${block} -t ${thread}  --no-cleanup > ${prefix}.out 2>${prefix}.err"  && sudo echo 3 | sudo tee /proc/sys/vm/drop_caches && sudo sync &&  echo -e `date`  "\n" "${prefix} done!"
                } &
                echo `date`
                echo "${prefix} started"
            done
            wait
            sleep 2
        done
    done
done

