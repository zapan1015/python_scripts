# coding=utf-8
import boto3


"""
전체 RDS의 Instance Class 확인.
av exec --session-ttl=1h --assume-role-ttl=1h infra-dataeng-prod
cd rds/dataeng-prod/
"""
aws_regions = (
    ('US East', 'Ohio', 'us-east-2'),
    ('US East', 'N. Virginia', 'us-east-1'),
    ('US West', 'N. California', 'us-west-1'),
    ('US West', 'Oregon', 'us-west-2'),
    ('Africa', 'Cape Town', 'af-south-1'),
    ('Asia Pacific', 'Hong Kong', 'ap-east-1'),
    ('Asia Pacific', 'Mumbai', 'ap-south-1'),
    ('Asia Pacific', 'Osaka', 'ap-northeast-3'),
    ('Asia Pacific', 'Seoul', 'ap-northeast-2'),
    ('Asia Pacific', 'Singapore', 'ap-southeast-1'),
    ('Asia Pacific', 'Sydney', 'ap-southeast-2'),
    ('Asia Pacific', 'Tokyo', 'ap-northeast-1'),
    ('Canada', 'Central', 'ca-central-1'),
    ('China', 'Beijing', 'cn-north-1'),
    ('China', 'Ningxia', 'cn-northwest-1'),
    ('Europe', 'Frankfurt', 'eu-central-1'),
    ('Europe', 'Ireland', 'eu-west-1'),
    ('Europe', 'London', 'eu-west-2'),
    ('Europe', 'Milan', 'eu-south-1'),
    ('Europe', 'Paris', 'eu-west-3'),
    ('Europe', 'Stockholm', 'eu-north-1'),
    ('Middle East', 'Bahrain', 'me-south-1'),
    ('South America', 'São Paulo', 'sa-east-1'),
)

"""
AWS Region 별로 client 를 생성해서 확인.
"""
aws_account = "dataeng-prod (012481551608)"
contents = ""
for aws_region in aws_regions:
    aws_oceans_name = aws_region[0]
    aws_region_name = aws_region[1]
    aws_region_code = aws_region[2]
    # RDS Client
    rds_client = boto3.client(
        'rds',
        region_name=aws_region_code
    )
    # Aurora Cluster
    db_clusters = []
    try:
        clusters_res = rds_client.describe_db_clusters()
    except Exception as e:
        pass
    else:
        db_clusters = clusters_res.get("DBClusters")

    if db_clusters:
        for db_cluster in db_clusters:
            contents = "{0}\t".format(aws_oceans_name)
            contents += "({0})\t".format(aws_region_name)
            contents += "({0})\t".format(aws_region_code)
            contents += "{0}\t\n".format(db_cluster['DBClusterIdentifier'])

            db_instances = db_cluster.get("DBClusterMembers")
            if db_instances:
                for db_ins in db_instances:
                    db_ins_id=db_ins.get("DBInstanceIdentifier")
                    is_writer = db_ins.get("IsClusterWriter")
                    cluster_param_status = db_ins.get("DBClusterParameterGroupStatus")
                    if db_ins_id:
                        db_ins_res = rds_client.describe_db_instances(
                            DBInstanceIdentifier=db_ins_id
                        )
                        # print(db_ins_res)
                        db_ins_row = db_ins_res.get("DBInstances")[0]
                        instance_id = db_ins_row.get("DBInstanceIdentifier")
                        instance_class = db_ins_row.get("DBInstanceClass")
                        instance_engine = db_ins_row.get("Engine")
                        instance_status = db_ins_row.get("DBInstanceStatus")
                        contents += "\t{0}\t".format(instance_id)
                        if is_writer:
                            contents += "Writer\t"
                        else:
                            contents += "Reader\t"
                        contents += "{0}\t".format(instance_class)
                        contents += "{0}\t\n".format(instance_engine)

                        if is_writer == False and instance_engine == "aurora-postgresql" and instance_status == "available":
                            modify_p = "{0}\t".format(aws_region_code)
                            modify_p += "{0}\t".format(instance_id)
                            modify_p += "{0}\t".format(instance_engine)
                            modify_p += "{0}\t".format(instance_class)
                            
                            modi_res = rds_client.modify_db_instance(
                                DBInstanceIdentifier=instance_id,
                                ApplyImmediately=True,
                                DBInstanceClass="db.t4g.medium"
                            )
                            ret_ins = modi_res.get("DBInstance")
                            modify_p += "\n>>{0}\t".format(ret_ins.get("DBInstanceClass"))

                            print(modify_p)

            # print(contents)
