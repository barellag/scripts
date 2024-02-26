#SYNOPSIS
#    Test the communication with SQS endpoint by creating a new queue and sending a message to that queue.

#DESCRIPTION
#   This Python script automates the SQS communication test from the Worker VMs to the AWS service. It helps with all the manual step
#   we need to do to perform this test such as, assuming proper role, create a new queue, send a message to this queue and delete
#   the resources used on this test

#PREREQUISITES
#   Install boto3 module with pip install boto3

#OUTPUT
#   A log file will be saved in the same directory where the script was executed

#EXAMPLE
#   python3 sqstest.py
#   Executes the script and will prompt to the user to type the role ARN and the QUEUE name to be created

#NOTES
#    NAME: sqstest.py
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
        logging.FileHandler("VeeamSupportSQSTest.log")
    ]
)
logging.info("Script Started")

#get the role to be assumed, usually the role from the account with access to the resources to be backed up
roleArn = input("Enter Your Backup Role ARN: ")
#type any name here, this is just to identify the session when we are assuming the role
sessionName = f"VeeamSupportSQSTest-{uuid.uuid4()}"

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

#creating a new SQS queue
print("Let's test the SQS communication, first we will create a SQS queue")
queueName=input("Type any queue name to be created: ")
regionId = input("Enter region name (example: us-east-1): ")
sqsClient = assumed_session.client("sqs",region_name=regionId)
sqsCreateQueues = sqsClient.create_queue(
    QueueName=queueName,
)

# Save the Queue URL to a variable
queueUrl = sqsCreateQueues['QueueUrl']
print("This is your new queue URL: "+queueUrl)
time.sleep(0.5)

#Send a message to the new queue
sqsSendMessage = sqsClient.send_message(
    QueueUrl=queueUrl,
    MessageBody='This is a test message from Veeam Support'
)
sendMessageOutput = sqsSendMessage['MessageId']
if sendMessageOutput is not None:
    print("Your message has been sent, Message ID: "+sendMessageOutput)
    time.sleep(0.5)
else:
    print("Check your permissions")

#delete resorces created for the test
while True:
    toDelete = input("Do you want to remove the resources created for this test? (Y/N)")
    if toDelete.lower() == "y":
        sqsDeleteResources = sqsClient.delete_queue(
        QueueUrl=queueUrl
    )
        print("Queue "+queueName+" has been deleted")
        print("Removing credentials...")
        time.sleep(1)
        access_key_id = None
        secret_access_key = None
        session_token = None
        print("Credentials removed")
        print("Keep in mind you will need to terminate this test instance manually!!!")
        break

    if toDelete.lower()=="n":
        print("Test queue and credentials kept.")
        break
    else:
        print("Invalid input. Please enter Y or N")

logging.info("Test finished")
