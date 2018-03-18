import boto3
import os

AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_CONFIG_REGION = 'eu-central-1'

cluster_name = 'api-portal'

# https://boto3.readthedocs.io/en/latest/reference/services/iam.html
iam_client = boto3.client('iam', aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=AWS_CONFIG_REGION)
# https://boto3.readthedocs.io/en/latest/reference/services/ecs.html
ecs_client = boto3.client('ecs', aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=AWS_CONFIG_REGION)

def get_cluster():
  response = ecs_client.describe_clusters(
    clusters=[
        cluster_name,
    ]
  )
  return response


cluster = get_cluster()
if len(cluster['clusters']):
  print('Cluster does not exist.')
else:
  print('ECS Cluster ->' + cluster['clusters'][0]['clusterName'])