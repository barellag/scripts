from azure.identity import DefaultAzureCredential
import os

tenant_id = 'ba07baab-431b-49ed-add7-cbc3542f5140'
client_id = 'e18bcf9c-67ed-4d26-9d4d-86b2535a26dd'

# Set environment variables for DefaultAzureCredential
os.environ['AZURE_TENANT_ID'] = tenant_id
os.environ['AZURE_CLIENT_ID'] = client_id
os.environ['AZURE_CLIENT_SECRET'] = 

# Create a credential object
credential = DefaultAzureCredential()
print(credential)

# Now you can use this credential to authenticate clients that will interact with Azure resources.