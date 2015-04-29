#!/bin/sh

host=`/usr/bin/docker inspect --format '{{ .NetworkSettings.IPAddress }}' $1`
date=`date +"%Y%m%d_%H%M%N"`
filename="/home/user/backups/${hostname}_${1}_${date}.sql"
echo $filename

/usr/bin/docker exec $1 /usr/bin/pg_dumpall -U pg -h $host > $filename
gzip $filename
