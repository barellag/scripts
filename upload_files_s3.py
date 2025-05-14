import boto3
import os
import logging
from datetime import datetime

# Set your AWS credentials and region
aws_access_key_id = ''
aws_secret_access_key = ''
region_name = 'us-east-1'

# Set your S3 bucket name and folder
bucket_name = ''
folder_path = 'folder/'

# Create a logger
logger = logging.getLogger('S3Uploader')
logger.setLevel(logging.INFO)

# Create a file handler and set the formatter
log_file_path = 's3_upload_log.txt'
file_handler = logging.FileHandler(log_file_path)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)

# Function to upload a file to S3
def upload_file(file_path, custom_data):
    file_key = folder_path + os.path.basename(file_path)
    
    # You can modify the metadata as needed
    metadata = {'custom-data': custom_data}
    
    # Create an S3 client
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name)
    
    try:
        s3.upload_file(file_path, bucket_name, file_key, ExtraArgs={'Metadata': metadata})
        logger.info("File uploaded to S3: %s with custom data: %s", file_key, custom_data)
    except Exception as e:
        logger.error("Error uploading file %s to S3: %s", file_path, str(e))

# List all files in the directory
directory_path = '/tmp/script/randomfiles'
custom_data = 'testing_upload_veeam'

files = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]

# Upload each file to S3 with custom data
for file in files:
    upload_file(file, custom_data)

