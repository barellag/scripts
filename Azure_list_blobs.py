from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta


# Set environment variables for DefaultAzureCredential
tenant_id = 'ba07baab-431b-49ed-add7-cbc3542f5140'
client_id = 'e18bcf9c-67ed-4d26-9d4d-86b2535a26dd'


credential = ClientSecretCredential(
    tenant_id=tenant_id,
    client_id=client_id,
    client_secret=client_secret
)

blob_service_client = BlobServiceClient(
    account_url="https://barellastg1.blob.core.windows.net",
    credential=credential
)

# Create a SAS token (the application itself has permissions to do this)
sas_token = generate_blob_sas(
    account_name="barellastg1",
    container_name="barellacnt1",
    blob_name = "Veeam/Backup/cool1/Clients/{83c15758-8a81-49d8-b2d1-5f08110e0bd0}/aaa22a7f-9b33-4f30-8ea3-d18f90beaab1/Metadata/Checkpoint",
    account_key="",  # Best practice: fetch the key securely as needed or use user delegation SAS
    permission=BlobSasPermissions(read=True),
    expiry=datetime.utcnow() + timedelta(hours=1)
)

account_url="https://barellastg1.blob.core.windows.net"
container_name="barellacnt1"
blob_name = "Veeam/Backup/cool1/Clients/{83c15758-8a81-49d8-b2d1-5f08110e0bd0}/aaa22a7f-9b33-4f30-8ea3-d18f90beaab1/Metadata/Checkpoint"
blob_service_client = BlobServiceClient(account_url=account_url, credential=sas_token)

# Get a client representing the specified blob within the container
blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

# Get a client representing the specified container
container_client = blob_service_client.get_container_client(container_name)

# Specify the container name and (optional) folder prefix
folder_prefix = "Veeam/Backup/cool1/Clients/{83c15758-8a81-49d8-b2d1-5f08110e0bd0}/aaa22a7f-9b33-4f30-8ea3-d18f90beaab1/Metadata/Checkpoint/"  # Make sure to end the prefix with a '/'


# List the blobs in the container or folder
blobs_list = container_client.list_blobs(name_starts_with=folder_prefix)
# Print out the list of blob names
for blob in blobs_list:
    print(blob.name)

# If you want a more detailed view of each blob, you can print out blob properties
# For example:
for blob in blobs_list:
    print(f"Name: {blob.name}")
    print(f" - Blob Size: {blob.size} bytes")
    print(f" - Content type: {blob.content_settings.content_type}")
    print(f" - Last modified: {blob.last_modified}")
    print(f" - Snapshot: {blob.snapshot}")
    print("----------")
