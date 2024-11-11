import boto3
import logging
import time
import uuid

#configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler("RemovingS3Objects.log")
    ]
)
logging.info("Script Started")

#get the role to be assumed, usually the role from the account with access to the resources to be backed up
roleArn = "" #enter role ARN
#type any name here, this is just to identify the session when we are assuming the role
sessionName = f"VeeamS3DeleteObject-{uuid.uuid4()}"

#start session with assumed role
session = boto3.Session()
sts = session.client("sts")
response = sts.assume_role(
    RoleArn=roleArn,
    RoleSessionName=sessionName,
    DurationSeconds=900
)
print("Assuming role...")
time.sleep(0.5)

#save creds to variables
credentials = response['Credentials']
access_key_id = credentials['AccessKeyId']
secret_access_key = credentials['SecretAccessKey']
session_token = credentials['SessionToken']

print("Starting session...")
time.sleep(0.5)

#setting temp credentials
assumed_session = boto3.Session(
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_access_key,
    aws_session_token=session_token
)

bucket = "" #Enter bucket name
prefix = "testing_folder_to_delete/subfolder1/subfolder2" #Enter the path, replacing the example I left
s3_client = assumed_session.client('s3')
object_response_paginator = s3_client.get_paginator('list_object_versions')

delete_marker_list = []
version_list = []


for object_response_itr in object_response_paginator.paginate(Bucket=bucket, Prefix=prefix):
    if 'DeleteMarkers' in object_response_itr:
        for delete_marker in object_response_itr['DeleteMarkers']:
            delete_marker_list.append({'Key': delete_marker['Key'], 'VersionId': delete_marker['VersionId']})

    if 'Versions' in object_response_itr:
        for version in object_response_itr['Versions']:
            version_list.append({'Key': version['Key'], 'VersionId': version['VersionId']})



for i in range(0, len(delete_marker_list), 1000):
    response = s3_client.delete_objects(
        Bucket=bucket,
        Delete={
            'Objects': delete_marker_list[i:i+1000],
            'Quiet': True
        }
    )
    if response.get('Errors'):
        logging.error(f"Errors encountered during deletion: {response['Errors']}")
    else:
        logging.info(f"Deleted delete markers batch {i//1000 + 1}.")
    print(response)

for i in range(0, len(version_list), 1000):
    response = s3_client.delete_objects(
        Bucket=bucket,
        Delete={
            'Objects': version_list[i:i+1000],
            'Quiet': True
        }
    )
    if response.get('Errors'):
        logging.error(f"Errors encountered during deletion: {response['Errors']}")
    else:
        logging.info(f"Deleted versions batch {i//1000 + 1}.")
    print(response)