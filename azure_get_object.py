import importlib
import subprocess

def import_and_install_module(module_name):
    try:
        importlib.import_module(module_name)
    except ImportError:
        print(f"The module {module_name} is missing. Installing it now...")
        subprocess.call(['python3', '-m', 'pip', 'install', module_name])

#modules array that are required
required_modules = ["azure.storage.blob"]

#check and install the required modules
for module in required_modules:
    import_and_install_module(module)

import time
from azure.storage.blob import BlobServiceClient

# Replace with your actual connection string
connection_string = "" #enter the connection string from storage account
container_name = "" #enter the container name
blob_name = ""

blob_service_client = BlobServiceClient.from_connection_string(connection_string)
container_client = blob_service_client.get_container_client(container_name)



def download_blob(blob_name):
    try:
        blob_client = container_client.get_blob_client(blob_name)
        blob_data = blob_client.download_blob().readall()
        properties = blob_client.get_blob_properties()
        immutability_policy = properties.get('immutability_policy')
        legal_hold = properties.get('has_legal_hold')
        if immutability_policy:
            expiration_date = immutability_policy.get('expiry_time')
            policy_mode = immutability_policy.get('policy_mode', 'N/A')
            print("Immutability Policy:")
            print(f"  Expiry Time: {expiration_date}")
            print(f"  Policy Mode: {policy_mode}")
        else:
            print("No immutability policy set.")
        return blob_data
    except Exception as e:
        print(f"Error downloading blob {blob_name}: {e}")
        return None


# Simulate multiple requests
def simulate_load(blob_name, num_requests):
    for i in range(num_requests):
        print(f"Request {i+1}")
        data = download_blob(blob_name)
        if data is not None:
            print(f"Downloaded blob size: {len(data)} bytes")
        time.sleep(0.0)  # Add a delay to mimic a more real-world scenario

simulate_load(blob_name, 100)
