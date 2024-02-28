#first import some modules to check if the needed modules are installed
import importlib
import subprocess

def import_and_install_module(module_name):
    try:
        importlib.import_module(module_name)
    except ImportError:
        print(f"The module {module_name} is missing. Installing it now...")
        subprocess.call(['pip', 'install', module_name])

#modules array that are required
required_modules = ["boto3", "awscli", "logging", "time", "shortuuid"]

#check and install the required modules
for module in required_modules:
    import_and_install_module(module)

#import needed modules after checking if they are present and install missing ones
import boto3
import logging
import time
import shortuuid
import os

#configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler("VeeamSupportSQSTest.log")
    ]
)
logging.info("Script Started")

#now lets check if the AWS credentials are set and if not, we'll set them
def check_aws_credentials():
    if not (os.environ.get('AWS_ACCESS_KEY_ID') and os.environ.get('AWS_SECRET_ACCESS_KEY')):
        print("AWS credentials are not set.")
        access_key = input("Enter AWS Access Key ID: ")
        secret_key = input("Enter AWS Secret Access Key: ")
        os.environ['AWS_ACCESS_KEY_ID'] = access_key
        os.environ['AWS_SECRET_ACCESS_KEY'] = secret_key
        print("AWS credentials have been set.")

#invoke function
check_aws_credentials()

#get the role to be assumed, usually the role from the account with access to the resources to be backed up
roleArn = input("Enter Your Backup Role ARN: ")
#type any name here, this is just to identify the session when we are assuming the role
sessionName = f"VeeamSupportSQSTest-{shortuuid.uuid()}"
#Get region name
regionId = input("Enter region name (example: us-east-1): ")

#start session with assumed role
session = boto3.Session()
sts = session.client("sts", region_name=regionId)
response = sts.assume_role(
    RoleArn=roleArn,
    RoleSessionName=sessionName,
    DurationSeconds=900
)
assumedRole = response['AssumedRoleUser'] #getting assumed role with session name
assumedRoleWithSession = assumedRole['Arn']
print("Assuming role "+roleArn)
time.sleep(0.5)
print("Assumed role: "+assumedRoleWithSession)
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

#getting newest AMI for the test instance
ssmClient=boto3.client('ssm', region_name=regionId)
amiName='/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-6.1-x86_64'
amiResponse=ssmClient.get_parameter(Name=amiName, WithDecryption=False)
latestAmiId=amiResponse['Parameter']['Value']
print("The following AMI will be used for this region: "+latestAmiId)


#creating a new keyPair
ec2Client = assumed_session.client('ec2', region_name=regionId)
keyName=f"VeeamSupportKey-{shortuuid.uuid()}"
newKeyPair = ec2Client.create_key_pair(KeyName=keyName)
newPrivateKey = f'{keyName}.pem'
with open(newPrivateKey, 'w') as pk_file:
    pk_file.write(newKeyPair['KeyMaterial'])
print("New keypair created. the PEM file has been downloaded to the folder where this script is being executed from. Key Name: "+newPrivateKey)
#change permissions for pem file
os.chmod(newPrivateKey, 0o400)
print('Setting read-only permissions to PEM file')
time.sleep(0.5)
print('Read-only permissions set')

#launching a new test instancesubnet-09c53671781e352d5
tempVmName = input('Enter a name for the test VM: ')
#regionId = input("Enter region name (example: us-east-1): ") it is already requested above
instanceProfile = input("Enter the instance profile ARN used by the worker: ")
subnetId = str(input('Enter subnet ID: '))
securityGroup = input('Enter Security Group ID: ')


ec2Client = assumed_session.resource('ec2', region_name=regionId)
newInstance = ec2Client.create_instances(
    BlockDeviceMappings=[
        {
            'DeviceName': '/dev/xvda',
            'Ebs': {
                'DeleteOnTermination': True,
                'VolumeSize': 8,
                'VolumeType': 'gp3'
            },
        },
    ],
    ImageId=latestAmiId, #using latest AMI from SSM parameter store
    InstanceType='t3.medium',
    SecurityGroupIds=[securityGroup],
    SubnetId = subnetId,
    MaxCount=1,
    MinCount=1,
    TagSpecifications= [
        {
            'ResourceType': 'instance',
            'Tags':[
                {
                    'Key': 'Name',
                    'Value': tempVmName
                },
            ]
        },
    ],
    UserData='''#!/bin/bash
yum  update
yum install python3-pip python3-setuptools -y
pip install boto3
cd /tmp
wget https://github.com/barellag/scripts/raw/main/sqstest.py
''',
    IamInstanceProfile = {'Arn': instanceProfile},
    KeyName = keyName #key generated from 
)

print('Gathering new instance details...')
time.sleep(3)
newInstance[0].reload()
newInstanceId = newInstance[0].id
print('Temporary instance ID: '+newInstanceId)
print('Getting Private IP...')
time.sleep(3)
newInstancePrivIp = newInstance[0].private_ip_address
time.sleep(3)
print('Temporary instance Private IP: '+newInstancePrivIp)
print('Getting Public IP...')
time.sleep(3)
newInstancePubIp = newInstance[0].public_ip_address
if newInstancePubIp is None:
    print('Public IP not present')
else:
    print('Temporary instance Public IP: '+newInstancePubIp)
    

#logging information summary
logging.info("Creating a new EC2 instance with the following configuration:")
logging.info("Image ID: " + latestAmiId)
logging.info("Instance Type: t3.medium")
logging.info("Security Group ID: " + securityGroup)
logging.info("Subnet ID: " + subnetId)
logging.info("Instance Profile: " + instanceProfile)
logging.info("SSH Key: " + newPrivateKey)

# Show where the log is printed
logging.info("Log file is located at: VeeamSupportSQSTest.log")
