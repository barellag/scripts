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

    

from azure.storage.blob import BlobServiceClient

# Initialize the connection parameters
connection_string = ""  # Replace with your actual connection string
container_name = "container_name"  # Replace with your container name
folder_prefix = "prefix/example/here/"  # Replace with the folder path you want to delete files from

# Create a blob service client
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# Create a container client
container_client = blob_service_client.get_container_client(container_name)

# List and delete blobs within the specified prefix
deleted_blob_count = 0
print("Deleting blobs...")
blobs_to_delete = container_client.list_blobs(name_starts_with=folder_prefix)

for blob in blobs_to_delete:
    print(f"Deleting blob: {blob.name}")
    container_client.delete_blob(blob.name)
    deleted_blob_count += 1

print(f"Deleted {deleted_blob_count} blobs from the folder '{folder_prefix}'")