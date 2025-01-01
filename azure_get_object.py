import importlib
import subprocess

def import_and_install_module(module_name):
    try:
        importlib.import_module(module_name)
    except ImportError:
        print(f"The module {module_name} is missing. Installing it now...")
        subprocess.call(['python3', '-m', 'pip', 'install', module_name])

#modules array that are required
required_modules = ["azure.storage.blob","concurrent.futures"]

#check and install the required modules
for module in required_modules:
    import_and_install_module(module)

import time
from azure.storage.blob import BlobServiceClient
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging


# Logging configuration
logging.basicConfig(
    level=logging.INFO,  # Set the logging level
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format
    handlers=[
        logging.FileHandler("blob_download.log"),  # Log to this file
        logging.StreamHandler()  # Also print to console
    ]
)



# Replace with your actual connection string
connection_string = ""
container_name = ""
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
            logging.info("Immutability Policy:")
            logging.info(f"  Expiry Time: {expiration_date}")
            logging.info(f"  Policy Mode: {policy_mode}")
        else:
            logging.info("No immutability policy set.")
        return len(blob_data)  # Ensure returning the size, not the content
    except Exception as e:
        logging.error(f"Error downloading blob {blob_name}: {e}")
        return None
    

# Simulate parallel requests
def simulate_parallel_load(blob_name, num_requests):
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = {executor.submit(download_blob, blob_name): i for i in range(num_requests)}
        
        for future in as_completed(futures):
            request_id = futures[future]
            try:
                result = future.result()
                logging.info(f"Request {request_id + 1} completed with blob size: {result} bytes")
            except Exception as e:
                logging.info(f"Request {request_id + 1} generated an exception: {e}")

simulate_parallel_load(blob_name, 100)

