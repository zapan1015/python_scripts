# coding=utf-8
from Aurora.Mysql import Aurora


"""
watch -d -n 5 'python ./rds_status.py'
"""

if __name__ == "__main__":
    aurora = Aurora(
        aws_region='us-east-1',
        cluster_id='',
    )

    print("____________________")
    cluster_res = aurora.get_cluster_info()
    cluster_row = cluster_res.get('DBClusters')[0]
    cluster_members = cluster_row.get('DBClusterMembers')
    cluster_status = cluster_row.get('Status')
    print("Cluster [{0}] Status [{1}]".format(aurora.cluster_id, cluster_status))
    for cluster_member in cluster_members:
        response = aurora.get_describe_db_instances(cluster_member["DBInstanceIdentifier"])
        instance_row = response.get('DBInstances')[0]
        instance_id = instance_row.get('DBInstanceIdentifier')
        instance_status = instance_row.get('DBInstanceStatus')
        instance_class = instance_row.get('DBInstanceClass')
        
        cluster_role = "Reader"
        if cluster_member["IsClusterWriter"]:
            cluster_role = "Writer"
        print_row = "{0}: [{1}] ".format(cluster_role, instance_id)
        print_row += "DBInstanceStatus [{0}] ".format(instance_status)
        print_row += "DBInstanceClass [{0}".format(instance_class)
        print_row += "]"

        print(print_row)
    print("____________________")
