Bastion instance ID


product = "dk"
app     = "aurora"
env     = "prod"
managed_by      = "manually"
owner = "soohyun.park"

# https://docs.aws.amazon.com/ko_kr/AWSEC2/latest/UserGuide/ebs-using-volumes.html
/dev/sdf6

# Volume attach
lsblk
/dev/nvme1n1
sudo file -s /dev/nvme1n1

sudo mkfs -t xfs /dev/nvme1n1
sudo mkdir ./rds_backup
sudo mount /dev/nvme1n1 /home/soohyun-park/rds_backup

# RDS
DB cluster ID


# 바이너리 로그를 보관 기간
# https://docs.aws.amazon.com/ko_kr/AmazonRDS/latest/UserGuide/mysql_rds_set_configuration.html
CALL mysql.rds_set_configuration('binlog retention hours', 168);
CALL mysql.rds_show_configuration;


# EKS configure
aws eks update-kubeconfig \
--region ${dk_ww} \
--name dkww-eks-cluster --kubeconfig ~/.kube/dkww_kubeconfig.yaml

# Aurora snapshot

# Aurora 1.x snapshot 5 min
rds describe-db-clusters \
--region ${dk_ww} \
--db-cluster-identifier "sb-dk-ww-aurora-auroracluster" > ~/Documents/GitHub/soohyun/dk/ww/dk-ww-cluster.json

rds create-db-cluster-snapshot \
--region ${dk_ww} \
--db-cluster-snapshot-identifier "dkww-prod-snapshot-22042712" \
--db-cluster-identifier "sb-dk-ww-aurora-auroracluster" \
--tags "Key=product,Value=dk" "Key=app,Value=aurora" "Key=env,Value=dev" "Key=managed_by,Value=manually" "Key=sendbird_region,Value=ww" "Key=owner,Value=soohyun.park"

# Aurora 1.x KMS Key change creation
rds restore-db-cluster-from-snapshot \
--region ${dk_ww} \
--availability-zones "ap-northeast-2c" \
--db-cluster-identifier "soohyun-dkww-22042712" \
--snapshot-identifier "arn:aws:rds:ap-northeast-2:-:cluster-snapshot:dkww-prod-snapshot-22042712" \
--engine "aurora" \
--db-subnet-group-name "dk-ww-aurora-dbsubnetgroup" \
--vpc-security-group-ids "sg-09735e8ed1c20b739" \
--tags "Key=product,Value=dk" "Key=app,Value=aurora" "Key=env,Value=dev" "Key=managed_by,Value=manually" "Key=sendbird_region,Value=ww" "Key=owner,Value=soohyun.park" \
--kms-key-id "arn:aws:kms:ap-northeast-2:-:key/0fa287eb-895c-4a6a-8d21-c01c78b89bd5" \
--db-cluster-parameter-group-name "default.aurora5.6" \
--no-enable-iam-database-authentication \
--no-deletion-protection

rds create-db-instance \
--region ${dk_ww} \
--db-instance-identifier "soohyun-dkww-22042712" \
--db-cluster-identifier "soohyun-dkww-22042712" \
--db-instance-class "db.r5.large" \
--engine "aurora" \
--availability-zone "ap-northeast-2c" \
--db-parameter-group-name "default.aurora5.6" \
--no-auto-minor-version-upgrade \
--no-publicly-accessible \
--tags "Key=product,Value=dk" "Key=app,Value=aurora" "Key=env,Value=dev" "Key=managed_by,Value=manually" "Key=sendbird_region,Value=ww" "Key=owner,Value=soohyun.park"

# 생성 상태 확인.
# https://devdocs.io/jq/
# https://www.44bits.io/ko/post/cli_json_processor_jq_basic_syntax
rds describe-db-instances \
--region ${dk_ww} \
--db-instance-identifier "soohyun-dkww-22042712" \
| jq '.DBInstances[0].DBInstanceStatus'

rds modify-db-cluster \
--region ${dk_ww} \
--db-cluster-identifier "soohyun-dkww-22042712" \
--master-user-password "ITZY_Sorry_Not_Sorry" \
--backup-retention-period 1 \
--no-deletion-protection \
--apply-immediately

# Aurora 2.x snapshot
rds create-db-cluster-snapshot \
--region ${dk_ww} \
--db-cluster-snapshot-identifier "dkww-prod-snapshot-22042712" \
--db-cluster-identifier "soohyun-dkww-22042712" \
--tags "Key=product,Value=dk" "Key=app,Value=aurora" "Key=env,Value=dev" "Key=managed_by,Value=manually" "Key=sendbird_region,Value=ww" "Key=owner,Value=soohyun.park"

# RDS endpoint
soohyun-dkww-22042712.crfo31yfjl5s.us-west-2.rds.amazonaws.com

# connect 확인
/usr/bin/mysql -A --prompt="(\u) [\d]> " \
--user=root \
--host=dkww-aurora-common-auroracluster.cluster-ceslrqyjo8is.ap-northeast-2.rds.amazonaws.com \
--port=3306 \
--password

-- DB Drop
DROP DATABASE IF EXISTS soda;
DROP DATABASE IF EXISTS tmp;

# --databases ${DUMPDB} \

#!/bin/sh

DUMPBIN=$(which mysqldump)
USERID=""
USERPW=""
RDSHOST=""
RDSPORT="3306"
DUMPDB="sbdk"
BACKUP_DT=`date +%Y-%m-%d`

${DUMPBIN} --user=${USERID} \
--host=${RDSHOST} \
--port=${RDSPORT} \
--set-gtid-purged=OFF \
--opt \
--single-transaction \
--order-by-primary \
--skip-comments \
--flush-privileges \
--hex-blob \
--max-allowed-packet=1000M \
--databases ${DUMPDB} \
--password=${USERPW} \
> ./${DUMPDB}_${BACKUP_DT}.sql

rds create-db-cluster-snapshot \
--region ${dk_ww} \
--db-cluster-snapshot-identifier "dkww-prod-snapshot-22042712" \
--db-cluster-identifier "soohyun-dkww-22042712" \
--tags "Key=product,Value=dk" "Key=app,Value=aurora" "Key=env,Value=dev" "Key=managed_by,Value=manually" "Key=sendbird_region,Value=ww" "Key=owner,Value=soohyun.park"



#
rds create-db-cluster-snapshot \
--region ${dk_ww} \
--db-cluster-snapshot-identifier "dkww-prod-snapshot-22042716" \
--db-cluster-identifier "dkww-aurora-common-auroracluster" \
--tags "Key=product,Value=dk" "Key=app,Value=aurora" "Key=env,Value=dev" "Key=managed_by,Value=manually" "Key=sendbird_region,Value=ww" "Key=owner,Value=soohyun.park"

rds modify-db-cluster \
--region ${dk_ww} \
--db-cluster-identifier "sb-dk-ww-aurora-auroracluster" \
--port 63306 \
--apply-immediately

rds delete-db-instance --region ${dk_ww} \
--db-instance-identifier "sb-dk-us-1-aurora-read-replica-1" \
--no-skip-final-snapshot \
--no-delete-automated-backups

/usr/bin/mysql -A --prompt="(\u) [\d]> " \
--user=root \
--host=dkww-aurora-common-auroracluster.cluster-cvphwvyw7ppy.ap-southeast-1.rds.amazonaws.com \
--port=3306 \
--password

/usr/bin/mysql -A --prompt="(\u) [\d]> " \
--user=sbdk \
--host=dkww-aurora-common-auroracluster.cluster-cvphwvyw7ppy.ap-southeast-1.rds.amazonaws.com \
--port=3306 \
--password

# Binlog position
rds describe-events \
--region ${dk_ww}
Binlog position from crash recovery is mysql-bin-changelog.003505 95571704

# mysql-bin-changelog.001504 75241
CALL mysql.rds_set_external_master (
'sb-dk-ww-aurora-auroracluster.cluster-ctu0yusry3fd.ap-northeast-2.rds.amazonaws.com',
3306,
'',
'',
'mysql-bin-changelog.003505',
95571704,
0);

CALL mysql.rds_start_replication;

CALL mysql.rds_stop_replication;

CALL mysql.rds_reset_external_master;

SHOW MASTER STATUS\G
SHOW SLAVE STATUS\G

상태 체크
watch -d -n 5 'sh old_rds.sh'
watch -d -n 5 'sh new_rds.sh'

watch -d -n 5 'nslookup db-writer.sbdk.internal'

#!/bin/sh

MYBIN=$(which mysql)
MYUSER=""
MYPWD=""
MYPORT=3306
MYHOST=""
QUERY=$(cat slave.sql)

${MYBIN}  -A \
--user=${MYUSER} \
--host=${MYHOST} \
--port=${MYPORT} \
--password=${MYPWD} \
--execute="${QUERY}"

# master.sql
SHOW MASTER STATUS;
SELECT
(SELECT id FROM sbdk.main_event ORDER BY id DESC LIMIT 1) AS event_id,
(SELECT id FROM sbdk.main_chatmessage ORDER BY id DESC LIMIT 1) AS mesg_id,
(SELECT id FROM sbdk.main_ticket ORDER BY id DESC LIMIT 1) AS ticket_id
;

# slave.sql
SELECT 'main_event' AS tbl_name, COUNT(*) AS total_cnt, MAX(id) AS max_id FROM sbdk.main_event
UNION SELECT 'main_chatmessage' AS tbl_name, COUNT(*) AS total_cnt, MAX(id) AS max_id FROM sbdk.main_chatmessage
UNION SELECT 'main_ticket' AS tbl_name, COUNT(*) AS total_cnt, MAX(id) AS max_id FROM sbdk.main_ticket
;

main_event
main_chatmessage
main_ticket

# Amazon EBS 볼륨 삭제
https://docs.aws.amazon.com/ko_kr/AWSEC2/latest/UserGuide/ebs-detaching-volume.html
https://docs.aws.amazon.com/ko_kr/AWSEC2/latest/UserGuide/ebs-deleting-volume.html

