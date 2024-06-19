#first import modules to check if the needed modules are installed, if needed install them with pip install module_name
#example
#pip install azure-mgmt-resource azure-identity

import importlib
import subprocess

def import_and_install_module(module_name):
    try:
        importlib.import_module(module_name)
    except ImportError:
        print(f"The module {module_name} is missing. Installing it now...")
        subprocess.call(['python3', '-m', 'pip', 'install', module_name])

#modules array that are required
required_modules = ["json","azure-mgmt-resource","azure-identity"]

#check and install the required modules
for module in required_modules:
    import_and_install_module(module)

from azure.mgmt.resource import ResourceManagementClient
from azure.identity import DefaultAzureCredential
import shlex
import json

#login
def az_login():
    try:
        # Run the 'az login' command
        subprocess.run(['az', 'login'], check=True)
        print("Azure login successful.")
    except subprocess.CalledProcessError as e:
        print(f"Error during Azure login: {e}")

az_login()

#setting variables
credential = DefaultAzureCredential()
subscription_id = input("Enter Subscription ID: ")
resourceGroup =  input("Enter VBAz resource group name: ")
VBAzTagValue = input("enter the value of Veeam backup appliance ID tag: ") #Check the ID of the tag from resources created by appliance
VBAzTag = "Veeam backup appliance ID : "+VBAzTagValue
blobDnsZone = "privatelink.blob.core.windows.net"
queueDnsZone = "privatelink.queue.core.windows.net"
resource_client = ResourceManagementClient(credential, subscription_id)
vnet_names = input("Enter VNet name: ")

# Filters resources by tag
vb_az_tag_filter = "tagName eq 'Veeam backup appliance ID' and tagValue eq '" + VBAzTagValue + "'"
tagged_resources = resource_client.resources.list(filter=vb_az_tag_filter)

#list of private endpoints and NICs with VBAz tag
private_endpoints = []
network_interfaces = []
for resource in tagged_resources:
    if 'privateEndpoints' in resource.type:
        private_endpoints.append(resource)
    elif 'networkInterfaces' in resource.type:
        network_interfaces.append(resource)

# Function to run Azure CLI command
def run_az_cli_command(command):
    process = subprocess.run(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return process.stdout

dns_zones = run_az_cli_command('az network private-dns zone list --resource-group ' + resourceGroup)
dns_zones = json.loads(dns_zones)
zone_names = [zone['name'] for zone in dns_zones]

#get private endpoints IDs
privateEndpointIds = [pe.id for pe in private_endpoints]
#get NIC ids
NICendpointsIDs = [nic.id for nic in network_interfaces]

#listing NICs
def az_network_nic(nic_ids):
    try:
        # Split the list of IDs into individual arguments for the subprocess call
        args = ['az', 'network', 'nic', 'show', '--ids'] + nic_ids
        # Run the 'az network' command with the list of arguments
        result = subprocess.run(args, capture_output=True, text=True, check=True)
        # Parse and process the output JSON if needed
        nics_info = json.loads(result.stdout)
        # Process the output here...
        #print(nics_info)

    except subprocess.CalledProcessError as e:
        print(f"Error during fetching NICs: {e}")
        print(e.stderr)

# Call the function with the list of NIC IDs
az_network_nic(NICendpointsIDs)

#listing private endpoints
print("Getting Private Endpoint info....")
print("")

def az_network_private_endpoint_fqdns(pe_ids):
    fqdns = []  # List to hold FQDNs

    try:
        # Iterate over each private endpoint ID and make a separate CLI call
        for pe_id in pe_ids:
            args = ['az', 'network', 'private-endpoint', 'show', '--id', pe_id, '--output', 'json']
            result = subprocess.run(args, capture_output=True, text=True, check=True)
            pe_info = json.loads(result.stdout)
            # Extracting FQDNs from 'customDnsConfigs' of the private endpoint
            custom_dns_configs = pe_info.get('customDnsConfigs', [])
            fqdns.extend([dns_config['fqdn'] for dns_config in custom_dns_configs if 'fqdn' in dns_config])

    except subprocess.CalledProcessError as e:
        print(f"Error during fetching private endpoints: {e}")
        print(e.stderr)

    return fqdns

# Call the function with the list of private endpoint IDs
private_endpoints_fqdns = az_network_private_endpoint_fqdns(privateEndpointIds)
print('Private Endpoints FQDNs:', private_endpoints_fqdns)

#Get IpAddress
def az_network_private_endpoint_ipaddr(pe_ipaddr):
    ipAddr = []  # List to hold IP Addresses

    try:
        # Iterate over each private endpoint ID and make a separate CLI call
        for pe_id in pe_ipaddr:
            args = ['az', 'network', 'private-endpoint', 'show', '--id', pe_id, '--output', 'json']
            result = subprocess.run(args, capture_output=True, text=True, check=True)
            pe_info = json.loads(result.stdout)
            # Extracting FQDNs from 'customDnsConfigs' of the private endpoint
            custom_dns_configs = pe_info.get('customDnsConfigs', [])
            ipAddr.extend([dns_config['ipAddresses'] for dns_config in custom_dns_configs if 'ipAddresses' in dns_config])

    except subprocess.CalledProcessError as e:
        print(f"Error during fetching private endpoints: {e}")
        print(e.stderr)

    return ipAddr

# Call the function with the list of private endpoint IDs
private_endpoints_ipAddr = az_network_private_endpoint_ipaddr(privateEndpointIds)
print('Private Endpoints ipAddresses:', private_endpoints_ipAddr)

#checking if DNS zones exist
def check_and_create_private_dns_zones(resource_group, blob_dns_zone, queue_dns_zone):
    # Check if the blob DNS zone exists
    blob_dns_zone_exists = _az_private_dns_zone_exists(resource_group, blob_dns_zone)
    if not blob_dns_zone_exists:
        print(f"Creating DNS Zone: {blob_dns_zone}")
        _az_create_private_dns_zone(resource_group, blob_dns_zone)
    
    # Check if the queue DNS zone exists
    queue_dns_zone_exists = _az_private_dns_zone_exists(resource_group, queue_dns_zone)
    if not queue_dns_zone_exists:
        print(f"Creating DNS Zone: {queue_dns_zone}")
        _az_create_private_dns_zone(resource_group, queue_dns_zone)


def _az_private_dns_zone_exists(resource_group, dns_zone_name):
    # Run the Azure CLI command to check for the DNS zone's existence
    result = subprocess.run(
        ['az', 'network', 'private-dns', 'zone', 'show', '--resource-group', resource_group, '--name', dns_zone_name],
        capture_output=True, text=True
    )
    # If the DNS zone does not exist, the command will fail and return a non-zero code
    return result.returncode == 0

def _az_create_private_dns_zone(resource_group, dns_zone_name):
    # Run the Azure CLI command to create the DNS zone
    create_result = subprocess.run(
        ['az', 'network', 'private-dns', 'zone', 'create', '--resource-group', resource_group, '--name', dns_zone_name],
        capture_output=True, text=True, check=True
    )
    # Print the output if needed
    print(create_result.stdout)
    # Return the created DNS zone details as JSON
    return json.loads(create_result.stdout)

# Usage
resourceGroup = resourceGroup
blobDnsZone = "privatelink.blob.core.windows.net"
queueDnsZone = "privatelink.queue.core.windows.net" 

# Call the function to check and create DNS zones if necessary
check_and_create_private_dns_zones(resourceGroup, blobDnsZone, queueDnsZone)

#check if link exists
def az_private_dns_vnet_link_exists(resource_group, dns_zone_name, link_name):
    try:
        subprocess.run([
            'az', 'network', 'private-dns', 'link', 'vnet', 'show',
            '--name', link_name,
            '--resource-group', resource_group,
            '--zone-name', dns_zone_name
        ], check=True, stdout=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        # If the command failed, the link does not exist
        return False

def link_vnet_to_dns_zone(resource_group, dns_zone_name, vnet_names):
    link_name = f'dnslink-{vnet_names}'
    # Check if the DNS zone link already exists
    if az_private_dns_vnet_link_exists(resource_group, dns_zone_name, link_name):
        print(f'DNS zone link "{link_name}" already exists in zone "{dns_zone_name}". Skipping creation.')
    else:
        print(f'Creating DNS zone link "{link_name}" in zone "{dns_zone_name}".')
        subprocess.run([
            'az', 'network', 'private-dns', 'link', 'vnet', 'create',
            '--resource-group', resource_group,
            '--zone-name', dns_zone_name,
            '--name', link_name,
            '--virtual-network', vnet_names,
            '--registration-enabled', 'false'
        ], check=True)

# Add VNET to private DNS zone for QUEUE
link_vnet_to_dns_zone(resourceGroup, queueDnsZone, vnet_names)
# Add VNET to private DNS zone for BLOB
link_vnet_to_dns_zone(resourceGroup, blobDnsZone, vnet_names)


def remove_existing_a_record(resource_group, dns_zone_name, record_set_name, ipaddr):
    # List all A records in the DNS zone to find if the IP address is already used
    all_records_result = subprocess.run(
        ['az', 'network', 'private-dns', 'record-set', 'a', 'list',
         '--resource-group', resource_group,
         '--zone-name', dns_zone_name],
        stdout=subprocess.PIPE,
        check=True,
        text=True
    )
    
    all_records = json.loads(all_records_result.stdout)

    for record in all_records:
        for a_record in record.get('aRecords', []):
            if a_record['ipv4Address'] == ipaddr:
                # Identify the A record containing the IP and remove it
                subprocess.run([
                    'az', 'network', 'private-dns', 'record-set', 'a', 'remove-record',
                    '--resource-group', resource_group,
                    '--zone-name', dns_zone_name,
                    '--record-set-name', record['name'],
                    '--ipv4-address', ipaddr
                ], check=True)
                print(f"Removed existing A record with IP {ipaddr} from {dns_zone_name}")

def create_a_record(resource_group, dns_zone_name, record_set_name, ipaddr):
    if isinstance(ipaddr, list):
        # If ipaddr is a list, we remove records and create a new one for each IP
        for ip in ipaddr:
            remove_existing_a_record(resource_group, dns_zone_name, record_set_name, ip)
            subprocess.run([
                'az', 'network', 'private-dns', 'record-set', 'a', 'add-record',
                '--resource-group', resource_group,
                '--zone-name', dns_zone_name,
                '--record-set-name', record_set_name,
                '--ipv4-address', ip
            ], check=True)
            print(f"Added A record: {record_set_name} with IP {ip} to {dns_zone_name}")
    else:
        # If ipaddr is a single IP address string
        remove_existing_a_record(resource_group, dns_zone_name, record_set_name, ipaddr)
        subprocess.run([
            'az', 'network', 'private-dns', 'record-set', 'a', 'add-record',
            '--resource-group', resource_group,
            '--zone-name', dns_zone_name,
            '--record-set-name', record_set_name,
            '--ipv4-address', ipaddr
        ], check=True)
        print(f"Added A record: {record_set_name} with IP {ipaddr} to {dns_zone_name}")



# Function to create A records for the private endpoints
def create_private_dns_a_records(resource_group, blob_dns_zone_name, queue_dns_zone_name, fqdns, ipaddrs):
    for fqdn, ipaddr in zip(fqdns, ipaddrs):
        # Determine the DNS zone based on the FQDN
        if ".blob.core.windows.net" in fqdn:
            dns_zone_name = blob_dns_zone_name
        elif ".queue.core.windows.net" in fqdn:
            dns_zone_name = queue_dns_zone_name
        elif ".blob.storage.azure.net" in fqdn:
            dns_zone_name = blob_dns_zone_name
        else:
            print(f"Unknown service for FQDN {fqdn}")
            continue
        
        record_set_name = fqdn.split('.')[0]
        create_a_record(resource_group, dns_zone_name, record_set_name, ipaddr)

# Call the function to create A records
create_private_dns_a_records(resourceGroup, blobDnsZone, queueDnsZone, private_endpoints_fqdns, private_endpoints_ipAddr)

print("Script executed successfully...")
