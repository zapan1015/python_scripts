# coding=utf-8
from Aurora.Mysql import RestoreAurora


"""
AWS Regions
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
Instance Class
https://docs.aws.amazon.com/ko_kr/AmazonRDS/latest/AuroraUserGuide/Concepts.DBInstanceClass.html
"""


if __name__ == "__main__":
    aurora = RestoreAurora(
        aws_region='ap-southeast-1',
        cluster_id='',
        restore_class="db.r5.large",
    )
    aurora.set_restore_form_last_snapshots()
