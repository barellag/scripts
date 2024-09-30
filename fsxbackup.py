#SYNOPSIS
#    Test the FSx Backup

#DESCRIPTION
#   

#PREREQUISITES
#   Install boto3 module with pip install boto3

#OUTPUT
#   A log file will be saved in the same directory where the script was executed

#EXAMPLE
#   python3 fsxbackup.py
#   Executes the script and will prompt to the user to type the role ARN and the QUEUE name to be created

#NOTES
#    NAME: fsxbackup.py
#    VERSION: 1.1
#    AUTHOR: Gabriel Barella

#TROUBLESHOTING STEPS
#   In case you see the error "An error occurred (InvalidClientTokenId)", remove the credentials set to file ~/.aws/credentials.

#import needed modules
import boto3
import logging
import time
import uuid

#configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler("FSx_backup.log")
    ]
)
logging.info("Script Started")

#get the role to be assumed, usually the role from the account with access to the resources to be backed up
roleArn = input("Enter Your Backup Role ARN: ")
#type any name here, this is just to identify the session when we are assuming the role
sessionName = f"VeeamSupportFSxTest-{uuid.uuid4()}"

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

#Getting FSx ID
fsxId = input("Enter Your File System ID: ")

#Creating FSx client
client = boto3.client('fsx')
#Create FSx Backup
response = client.create_backup(
    FileSystemId=fsxId
)

logging.info("Test finished")
