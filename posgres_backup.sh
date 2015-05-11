#!/bin/bash

date=`date +"%Y%m%d_%H%M%N"`
filename="/home/user/backups/${hostname}_${1}_${date}.sql"
echo $filename

/usr/bin/docker exec $1 /usr/bin/pg_dumpall -U postgres > $filename
gzip $filename
