# coding=utf-8
import boto3


"""
전체 RDS의 Subnet 확인.
aws-vault exec --session-ttl=1h --assume-role-ttl=1h dataeng-prod
cd rds/dataeng-prod/
"""
def get_describe_db_clusters(**kwargs):
    res = kwargs['client'].describe_db_clusters(
        DBClusterIdentifier=kwargs['id']
    )
    return res


def get_describe_db_instances(**kwargs):
    c = kwargs['client']
    instance_id = kwargs['id']
    res = c.describe_db_instances(
        DBInstanceIdentifier=instance_id
    )
    return res

"""
('N. Virginia', 'us-east-1'),
('Ohio', 'us-east-2'),
('N. California', 'us-west-1'),
('Oregon', 'us-west-2'),
('Cape Town', 'af-south-1'),
('Hong Kong', 'ap-east-1'),
('Mumbai', 'ap-south-1'),
('Osaka', 'ap-northeast-3'),
('Seoul', 'ap-northeast-2'),
('Singapore', 'ap-southeast-1'),
('Sydney', 'ap-southeast-2'),
('Tokyo', 'ap-northeast-1'),
('Central', 'ca-central-1'),
('Frankfurt', 'eu-central-1'),
('Ireland', 'eu-west-1'),
('London', 'eu-west-2'),
('Milan', 'eu-south-1'),
('Paris', 'eu-west-3'),
('Stockholm', 'eu-north-1'),
('Bahrain', 'me-south-1'),
('São Paulo', 'sa-east-1'),
"""
aws_regions = (
    ('N. Virginia', 'us-east-1'),
    ('Mumbai', 'ap-south-1'),
    ('Osaka', 'ap-northeast-3'),
    ('Seoul', 'ap-northeast-2'),
    ('Singapore', 'ap-southeast-1'),
    ('Sydney', 'ap-southeast-2'),
    ('Tokyo', 'ap-northeast-1'),
    ('Central', 'ca-central-1'),
    ('Frankfurt', 'eu-central-1'),
    ('São Paulo', 'sa-east-1'),
)

"""
AWS Region 별로 client 를 생성해서 확인.
"""
aws_account = "dataeng-prod (012481551608)"
print_row = ""
for aws_region in aws_regions:
    client = boto3.client(
        'rds',
        region_name=aws_region[1]
    )
    ec2_client = boto3.client(
        'ec2',
        region_name=aws_region[1]
    )
    response = client.describe_db_clusters()
    db_clusters = response.get("DBClusters")
    aws_reg = "{0} ({1})".format(aws_region[0], aws_region[1])
    if db_clusters:
        for db_cluster in db_clusters:
            print_row = "{0}\t".format(aws_account)
            print_row += "{0}\t".format(aws_reg)
            print_row += "{0}\t".format(db_cluster['DBClusterIdentifier'])
            # print_row += "{0}\t".format(db_cluster['DBSubnetGroup'])

            # Instance 의 PubliclyAccessible 확인.
            is_public_access = False
            db_instances = db_cluster.get("DBClusterMembers")
            for row in db_instances:
                res = get_describe_db_instances(client=client, id=row["DBInstanceIdentifier"])
                if res["DBInstances"][0]["PubliclyAccessible"]:
                    is_public_access = True
            print_row += "{0}\t".format(is_public_access)

            response = client.describe_db_subnet_groups(
                DBSubnetGroupName=db_cluster['DBSubnetGroup']
            )
            subnets = response['DBSubnetGroups'][0]['Subnets']

            subnet_ids = []
            for subnet in subnets:
                subnet_ids.append(subnet['SubnetIdentifier'])

            if len(subnet_ids) > 0:
                response = ec2_client.describe_subnets(
                    SubnetIds=subnet_ids
                )
                response = ec2_client.describe_route_tables(
                    Filters=[
                        {
                            'Name': 'association.subnet-id',
                            'Values': subnet_ids
                        },
                    ]
                )
                route_rows = response['RouteTables']
                for route_row in route_rows:
                    route_associations = route_row['Associations']
                    routes = route_row['Routes']

                # Internet gateways 포함 여부 확인.
                is_igw = False
                for row in routes:
                    cidr_block = row.get("DestinationCidrBlock")
                    gateway_id = row.get("GatewayId")
                    if cidr_block == "0.0.0.0/0":
                        is_igw = True
                    # IPv6
                    ipv6_cidr_block = row.get("DestinationIpv6CidrBlock")
                    if ipv6_cidr_block == "::/0":
                        is_igw = True

                if is_igw:
                    print_row += "True\t"
                else:
                    print_row += "False\t"
            print(print_row)

