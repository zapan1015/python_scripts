# 클러스터 파라밑터
aws rds describe-db-cluster-parameters \
--region ap-northeast-2 \
--db-cluster-parameter-group-name nexon-aurora-dbclusterparametergroup-hust5rewdc9s \
--query 'Parameters[] | [?IsModifiable == `true`]' \
> ./nexon-cluster-param.json

# DB 파라미터
key_buffer_size=33554432
bulk_insert_buffer_size=33554432
# 600M
innodb_log_file_size = 629145600
innodb_log_files_in_group = 2
innodb_sync_array_size=16

aws rds describe-db-parameters \
--region ap-northeast-2 \
--db-parameter-group-name vt-db-param \
--query 'Parameters[] | [?IsModifiable == `true`]' \
> vt-db-param.json

## 파라미터 수정.
# 1GB = 1073741824
aws rds modify-db-cluster-parameter-group \
--db-cluster-parameter-group-name vt-cluster-param \
--generate-cli-skeleton input > ./modi-cluster-param.json

aws rds modify-db-cluster-parameter-group \
--db-cluster-parameter-group-name vt-cluster-param \
--cli-input-json file://modi-cluster-param.json

## Stops an Amazon RDS DB instance.
aws rds stop-db-cluster \
--region ap-southeast-1 \
--db-cluster-identifier soohyun-ap-5-infr-5073-cluster \
| jq '.DBCluster |.[0].Status'

aws rds describe-db-clusters \
--region ap-southeast-1 \
--db-cluster-identifier soohyun-ap-5-infr-5073-cluster \
| jq '.DBClusters |.[0].Status'

## Engine 확인.
aws rds describe-db-engine-versions --engine aurora --query '*[].[EngineVersion]' --output text --region ap-northeast-2

## DB Instance 추가.
aws rds create-db-instance \
--generate-cli-skeleton input > ./vt_shard01.json

aws rds create-db-instance \
--cli-input-json file://vt_shard01.json

aws rds describe-db-instances \
--region us-west-2 \
--db-instance-identifier sb-rds-us-1-aurora-cron-replica-02

aws rds create-db-instance \
--region us-west-2 \
--db-instance-identifier sb-rds-us-1-aurora-cron-replica-03 \
--db-cluster-identifier us-1-aurora-auroracluster-1ibef14elb3sn \
--db-instance-class "db.t3.medium" \
--engine "aurora" \
--availability-zone "us-west-2b" \
--db-parameter-group-name "us-1-aurora-dbparametergroup-t3" \
--no-auto-minor-version-upgrade \
--no-publicly-accessible \
--tags "Key=datadog_enabled,Value=true" "Key=us-1,Value=true" "Key=product,Value=mesg" "Key=sendbird_region,Value=us-1" "Key=creator,Value=soohyun"

aws rds list-tags-for-resource \
--region us-west-2 \
--resource-name arn:aws:rds:us-west-2:391396433657:db:soohyun-us-1-cluster

aws rds add-tags-to-resource \
--region ap-northeast-2 \
--resource-name arn:aws:rds:ap-northeast-2:391396433657:db:sb-desk-woowa-aurora-instance-04 \
--tags "Key=app,Value=aurora" "Key=product,Value=desk" "Key=managed_by,Value=manually" "Key=sendbird_region,Value=woowa" "Key=detail,Value=common" "Key=env,Value=prod" "Key=billing,Value=woowa" "Key=woowa,Value=True" "Key=datadog_enabled,Value=True"

aws rds remove-tags-from-resource \
--region us-west-2 \
--resource-name arn:aws:rds:us-west-2:391396433657:db:soohyun-us-1-cluster \
--tag-keys "datadog_enabled" "us-1" "product" "sendbird_region"

## Aurora cluster 
aws rds describe-db-clusters \
--db-cluster-identifier sb-ap-2-rds-cluster \
| jq '.DBClusters |.[0].VpcSecurityGroups'

aws rds modify-db-cluster \
--db-cluster-identifier sb-ap-2-rds-cluster \
--vpc-security-group-ids "sg-0f955fc3cc6388bbb" "sg-0bf01963" "sg-07ae9850beeab9050" \
--apply-immediately 

## Deploy EC2 Stop / Start
/usr/local/bin/aws ec2 stop-instances \
--instance-ids i-0ae2da9cac7da4447

/usr/local/bin/aws ec2 start-instances \
--instance-ids i-0ae2da9cac7da4447

## Test RDS Cluster 변경.
aws rds modify-db-cluster \
--region us-west-2 \
--db-cluster-identifier soohyun-doordash-cluster-2021061701 \
--master-user-password "" \
--backup-retention-period 1 \
--no-deletion-protection \
--apply-immediately 
