
import importlib
import subprocess
import logging

# Logging configuration
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to capture all levels of logs
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("calculating_blobs.log"),  # Log file to store logs
        logging.StreamHandler()  # Output logs to console
    ]
)


def import_and_install_module(module_name):
    try:
        importlib.import_module(module_name)
        logging.info(f"Module {module_name} is already installed.")
    except ImportError:
        print(f"The module {module_name} is missing. Installing it now...")
        subprocess.call(['python3', '-m', 'pip', 'install', module_name])
        logging.info(f"Installation complete for module {module_name}.")

# modules array that are required
required_modules = ["collections", "azure.storage.blob"]

# check and install the required modules
for module in required_modules:
    import_and_install_module(module)

from azure.storage.blob import BlobServiceClient
from collections import defaultdict



# Initialize the connection parameters
connection_string = ""  # Replace with your connection string
container_name = ""  # Replace with your container name
prefix = "Veeam/Backup/backup/Clients/{83c15758-8a81-49d8-b2d1-5f08110e0bd0}/"  # Path prefix

# Create blob service client
try:
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    logging.info("Connected to BlobServiceClient successfully")
except Exception as e:
    logging.error(f"Failed to connect to BlobDServiceClient: {e}.")
# Initialize a dictionary to sum the sizes of blobs within each folder
folder_sizes = defaultdict(int)

# List blobs under the specified prefix and calculate total sizes
try:
    container_client = blob_service_client.get_container_client(container_name)
    for blob in container_client.list_blobs(name_starts_with=prefix):
        logging.debug(f"Processing blob: {blob.name}, size: {blob.size} bytes.")
        # Split the blob name to get the first-level folder name after the prefix
        relative_path = blob.name[len(prefix):]  # Get the part after the prefix
        first_folder = relative_path.split('/')[0]  # Get the first part of the relative path
        if first_folder:
            folder_sizes[first_folder] += blob.size
except Exception as e:
    logging.error(f"Error while listing blobs: {e}.")

    # Define the path for the output file
output_file_path = "folder_sizes.txt"

# Open the file in write mode
try:
    with open(output_file_path, "w") as file:
        # Display and write the results
        for folder, size in folder_sizes.items():
            size_in_mb = round(size / (1024 * 1024), 2)  # Convert bytes to MB
            output_line = f"{folder}: {size_in_mb} MB\n"
            print(output_line.strip())  # Print each line to console
            logging.info(output_line.strip()) #log each line
            file.write(output_line)     # Write each line to the file
    
    logging.info(f"Output has been saved to {output_file_path}.")

except Exception as e:
    logging.error(f"Failed to write to file { output_file_path}: {e}.")
