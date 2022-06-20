#!/bin/sh

DUMPBIN=$(which mysqldump)
USERID=""
USERPW=""
RDSHOST=""
RDSPORT="3306"
DUMPDB=""
DUMPTBL="zapan_mcl_rests"

${DUMPBIN} --user=${USERID} \
--host=${RDSHOST} \
--set-gtid-purged=OFF \
--opt \
--single-transaction \
--order-by-primary \
--skip-comments \
--hex-blob \
--databases ${DUMPDB} \
--tables ${DUMPTBL} \
--password=${USERPW} \
| /bin/gzip >> ./mygroup_aurora56_20211202.sql.gz
