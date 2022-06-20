# coding=utf-8
import botocore
import boto3
import time

class Aurora:
    def __init__(self, **kwargs):
        """
        Default valuabale define.
        aws_region reguired. (Defalut: Seoul)
        cluster_id (Default: )
        """
        if kwargs.get('aws_region'):
            self.aws_region = kwargs['aws_region']
        else:
            self.aws_region = "ap-northeast-2"

        self.client = boto3.client(
            'rds',
            region_name=self.aws_region
        )
        self.cluster_id = kwargs.get('cluster_id')

    def get_cluster_info(self, c_id=None):
        if c_id:
            response = self.client.describe_db_clusters(
                DBClusterIdentifier=c_id
            )
        elif self.cluster_id:
            response = self.client.describe_db_clusters(
                DBClusterIdentifier=self.cluster_id
            )
        else:
            response = self.client.describe_db_clusters()
        return response

    def get_describe_db_instances(self, id):
        return self.client.describe_db_instances( DBInstanceIdentifier=id )
    
    def get_describe_db_cluster_parameter_groups(self, param_name):
        return self.client.describe_db_cluster_parameter_groups( DBClusterParameterGroupName=param_name )
    
    def get_cluster_available_check(self):
        cluster_res = self.get_cluster_info()
        cluster_members = cluster_res["DBClusters"][0]["DBClusterMembers"]
        time.sleep(60)
        status_check = 0
        while status_check < 100:
            is_available = True
            for cluster_member in cluster_members:
                instance_id = cluster_member["DBInstanceIdentifier"]
                instance_res = self.get_describe_db_instances(instance_id)
                db_ins_status = instance_res["DBInstances"][0]["DBInstanceStatus"]
                cluster_role = "Reader"
                if cluster_member["IsClusterWriter"]:
                    cluster_role = "Writer"
                print_row = "[{0}] [{1}]".format(cluster_role, instance_id)
                print_row += " ({0})".format(db_ins_status)
                print_row += " ({0})".format(instance_res["DBInstances"][0]["DBInstanceClass"])
                print_row += " [{0}]".format(time.strftime('%c', time.localtime(time.time())))
                print(print_row)
                if db_ins_status != "available":
                    is_available = False
            if is_available:
                break
            time.sleep(30)
            status_check = status_check + 1
        return True
    
    def set_db_connections(self, **kwargs):
        db_param_id = kwargs.get("db_param_id")
        max_conn = kwargs.get("max_conn")
        max_user_conn = kwargs.get("max_user_conn")
        self.client.modify_db_parameter_group(
            DBParameterGroupName=db_param_id,
            Parameters=[
                {
                    'ParameterName': 'max_connections',
                    'ParameterValue': '{0}'.format(max_conn),
                    'ApplyMethod': 'immediate'
                },
                {
                    'ParameterName': 'max_user_connections',
                    'ParameterValue': '{0}'.format(max_user_conn),
                    'ApplyMethod': 'immediate'
                }
            ]
        )

    def set_modify_db_instance(self, id, cls):
        res = self.client.modify_db_instance(
            DBInstanceIdentifier=id,
            DBInstanceClass=cls,
            ApplyImmediately=True
        )
        print_row = "Class [{0}] ".format(res["DBInstance"]["DBInstanceClass"])
        print_row += "to [{0}] ".format(cls)
        print_row += " Status [{0}]".format(res["DBInstance"]["DBInstanceStatus"])

        print("Modify: {0}".format(print_row))
        print("Begin: [{0}]".format(time.strftime('%c', time.localtime(time.time()))))

    def set_failover_db_cluster(self, target_id):
        self.client.failover_db_cluster(
            DBClusterIdentifier=self.cluster_id,
            TargetDBInstanceIdentifier=target_id
        )
        time.sleep(30)
        status_check = 0
        while status_check < 100:
            is_break = False
            res = self.get_cluster_info()
            rows = res["DBClusters"][0]["DBClusterMembers"]
            for row in rows:
                if row["IsClusterWriter"] and row["DBInstanceIdentifier"] == target_id:
                    is_break = True
                    break

            if is_break:
                break
            status_check = status_check + 1
            time.sleep(30)
        

    @staticmethod
    def get_max_connections(db_cls):
        """
        refered from https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.DBInstanceClass.html
        """
        class_param = {
            "db.r5.large": (2000, 1995),
            "db.r5.xlarge": (3000, 2995),
            "db.r5.2xlarge": (4000, 3995),
            "db.r5.4xlarge": (5000, 4995),
            "db.r5.8xlarge": (6000, 5995),
            "db.r5.12xlarge": (7000, 6995),
            "db.r5.16xlarge": (7000, 6995),
            "db.r5.24xlarge": (10000, 9995),
            "db.r6g.large": (2000, 1995),
            "db.r6g.xlarge": (3000, 2995),
            "db.r6g.2xlarge": (4000, 3995),
            "db.r6g.4xlarge": (5000, 4995),
            "db.r6g.8xlarge": (6000, 5995),
            "db.r6g.12xlarge": (7000, 6995),
            "db.r6g.16xlarge": (7000, 6995),
            "db.r6g.24xlarge": (10000, 9995),
            "db.t3.small": (45, 40),
            "db.t3.medium": (90, 85),
            "db.t3.large": (90, 85),
            "db.t4g.medium": (90, 85),
            "db.t4g.large": (90, 85),
            "db.t4g.xlarge": (90, 85)
        }
        return class_param.get(db_cls)


class RestoreAurora(Aurora):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Restore instance class
        self.restore_class = kwargs.get('restore_class')
        self.snapshot_id = kwargs.get('snapshot_id')

        # Owner
        self.owner = kwargs.get('owner')
        if self.owner is None:
            self.owner = "soohyun"

    def get_automated_snapshots(self):
        response = self.client.describe_db_cluster_snapshots(
            DBClusterIdentifier=self.cluster_id,
            SnapshotType='automated'
        )
        return response

    def set_restore_form_last_snapshots(self):
        # Soure Cluster Infor
        db_clusters = self.get_cluster_info().get('DBClusters')[0]
        availability_zones = db_clusters.get('AvailabilityZones')
        db_subnet_group_name = db_clusters.get('DBSubnetGroup')
        maintenance_widow = db_clusters.get('PreferredMaintenanceWindow')
        kms_key_id = db_clusters.get('KmsKeyId')
        restore_port = db_clusters.get('Port')
        sh_region = self.owner
        tag_app = db_clusters.get('Engine')
        if tag_app == 'aurora':
            rds_engine_ver = '5.6.mysql_aurora.1.23.4'
        elif tag_app == 'aurora-mysql':
            rds_engine_ver = '5.7.mysql_aurora.2.10.2'
        else:
            rds_engine_ver = db_clusters.get('EngineVersion')
        tag_list = db_clusters.get('TagList')
        for tag in tag_list:
            if tag['Key'] == "sh_region":
                sh_region = tag['Value']
        # Restore cluster Identifie
        restore_hour = time.strftime('%Y%m%d%I', time.localtime(time.time()))
        restore_cluster_id = "{0}".format(self.owner)
        restore_cluster_id += "-{0}-cluster".format(sh_region)
        restore_cluster_id += "-{0}".format(restore_hour)
        # VpcSecurityGroupIds
        vpc_sg_ids = []
        for row in db_clusters.get('VpcSecurityGroups'):
            vpc_sg_ids.append(row['VpcSecurityGroupId'])
        
        restore_tags = [
            {
                'Key': 'product',
                'Value': tag_app
            },
            {
                'Key': 'app',
                'Value': tag_app
            },
            {
                'Key': 'managed_by',
                'Value': 'manually'
            },
            {
                'Key': 'sh_region',
                'Value': '{0}-{1}'.format(self.owner, sh_region)
            },
            {
                'Key': 'env',
                'Value': 'dev'
            },
            {
                'Key': 'Owner',
                'Value': self.owner
            },
            {
                'Key': 'Name',
                'Value': restore_cluster_id
            }
        ]
        restore_cluster_param = "{0}-{1}".format(self.owner, self.aws_region)
        restore_cluster_param += "-{0}-dbclusterpg".format(tag_app)
        restore_instance_param = "{0}-{1}".format(self.owner, self.aws_region)
        restore_instance_param += "-{0}-dbpg".format(tag_app)
        try:
            restore_cluster_param_info = self.get_describe_db_cluster_parameter_groups(restore_cluster_param)
        except botocore.exceptions.ClientError as e:
            # 파라미터 생성.
            soruce_pg_dict = self.get_describe_db_cluster_parameter_groups(db_clusters.get('DBClusterParameterGroup')).get('DBClusterParameterGroups')[0]
            dbpg_falily = soruce_pg_dict['DBParameterGroupFamily']
            self.client.create_db_cluster_parameter_group(
                DBClusterParameterGroupName=restore_cluster_param,
                DBParameterGroupFamily=dbpg_falily,
                Description="{0} {1}".format(self.owner, dbpg_falily),
                Tags=restore_tags
            )
            self.client.create_db_parameter_group(
                DBParameterGroupName=restore_instance_param,
                DBParameterGroupFamily=dbpg_falily,
                Description="{0} {1}".format(self.owner, dbpg_falily),
                Tags=restore_tags
            )
        
        # Restore Instance Class 가 지정되어 있지 않은 경우. Writer Instance 와 동일.
        if self.restore_class is None:
            instance_rows = db_clusters.get('DBClusterMembers')
            for instance_row in instance_rows:
                if instance_row.get('IsClusterWriter'):
                    db_instances = self.get_describe_db_instances(instance_row.get('DBInstanceIdentifier')).get('DBInstances')[0]
                    self.restore_class = db_instances.get('DBInstanceClass')
        """
        Aurora 에서 마지막으로 자동 백업된 스냅샷에서 복구에 필요한 정보를 restore_info dict 에 추가.
        """
        if self.snapshot_id is None:
            last_cluster_snapshot = self.get_automated_snapshots().get('DBClusterSnapshots')[-1]
            snapshot_id = last_cluster_snapshot.get('DBClusterSnapshotIdentifier')
            snapshot_create_time = last_cluster_snapshot.get('SnapshotCreateTime')
        else:
            snapshot_id = self.snapshot_id
            snapshot_create_time = time.strftime('%c', time.localtime(time.time()))

        # Snapshot 에서 복구 하는데 필요한 변수 확인.
        comment = "Snapshot Id:\t{0}\n".format(snapshot_id)
        comment += "CreateTime:\t{0}\n".format(snapshot_create_time)
        comment += "Restore Cluster ID:\t{0}\n".format(restore_cluster_id)
        comment += "Engine:\t{0}\t".format(tag_app)
        comment += "EngineVer.:\t{0}\n".format(rds_engine_ver)
        comment += "AZ:\t{0}\t".format(availability_zones)
        comment += "KmsKeyId:\t{0}\n".format(kms_key_id)
        print(comment)
        
        is_confirmed = input("Do you want to create a cluster?\n(Yes) : ").lower()
        if is_confirmed == "yes":
            # Cluster create
            result = self.client.restore_db_cluster_from_snapshot(
                AvailabilityZones=availability_zones,
                DBClusterIdentifier=restore_cluster_id,
                SnapshotIdentifier=snapshot_id,
                Engine=tag_app,
                EngineVersion=rds_engine_ver,
                Port=restore_port,
                DBSubnetGroupName=db_subnet_group_name,
                VpcSecurityGroupIds=vpc_sg_ids,
                Tags=restore_tags,
                KmsKeyId=kms_key_id,
                EnableIAMDatabaseAuthentication=True,
                DBClusterParameterGroupName=restore_cluster_param,
                DeletionProtection=False
            )
            result = result.get('DBCluster')
            comment = "Endpoint:\t{0}\n".format(result['Endpoint'])
            comment += "ReaderEndpoint:\t{0}\n".format(result['ReaderEndpoint'])
            print(comment)
            time.sleep(30)
            # Instance Create
            result = self.client.create_db_instance(
                DBClusterIdentifier=restore_cluster_id,
                DBInstanceIdentifier=restore_cluster_id,
                DBInstanceClass=self.restore_class,
                Engine=tag_app,
                PreferredMaintenanceWindow=maintenance_widow,
                DBParameterGroupName=restore_instance_param,
                MultiAZ=False,
                EngineVersion=rds_engine_ver,
                AutoMinorVersionUpgrade=False,
                PubliclyAccessible=False,
                Tags=restore_tags,
                EnablePerformanceInsights=False
            )
            result = result.get('DBInstance')
            db_instance_id = result.get('DBInstanceIdentifier')
            db_instance_status = result.get('DBInstanceStatus')
            comment = "Instance ID:\t{0}\t".format(db_instance_id)
            comment += "[{0}]\n".format(db_instance_status)
            print(comment)

    def get_restore_db_cluster_status(self):
        response = self.get_cluster_info(self.restore_info['restore_cluster_id'])
        return response
