import requests
import getpass
import time
import urllib3
import json
from urllib3.exceptions import InsecureRequestWarning

# Suppress InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

# Endpoint URL
appliance = "https://"+input("Enter hostname or IP Address of the appliance: ")
url = appliance+"/api/oauth2/token"
# Your client credentials and other required data
username = input("Enter Username: ")
password = getpass.getpass("Enter Password: ")
data = {
    'username': username,
    'password': password,
    'grant_type': 'Password'  # common for server-to-server communication
}

# Headers can include content type or other necessary items
headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
}

# Send the POST request
response = requests.post(url, data=data, headers=headers, verify=False)

# Extracting the token from response
if response.status_code == 200:
    print("Token retrieved successfully!")
    token_info = response.json()  # Parse JSON response
    #print(token_info)  # This will print the entire JSON response including the token
    token = token_info.get('access_token')  # Accessing the token directly
    #print("Access Token:", token)
else:
    print("Failed to retrieve token")
    print("Status Code:", response.status_code)
    print("Response:", response.text)

#Change workers configuration
region_id = "eastus"
url = appliance+"/api/v7/workers/networkConfiguration/" + region_id

payload = {
  "subnet": "AZUE1T-VNET-INF",
  "virtualNetworkResourceId": "/subscriptions/6875112e-6a42-480e-8cd0-974a259f1c96/resourcegroups/network/providers/microsoft.network/virtualnetworks/azue1t-vnet",
  "regionId": "eastus",
  "networkSecurityGroupId": "/subscriptions/6875112e-6a42-480e-8cd0-974a259f1c96/resourcegroups/veeam-unstable-resources/providers/microsoft.network/networksecuritygroups/veeam-unstable-nsg",
  "forbidPublicIp": True,
  "tenantId": "9dd5717a-43d5-46ae-a419-bf4bea01cc72",
  "subscriptionId": "6875112e-6a42-480e-8cd0-974a259f1c96",
  "resourceGroup": "veeam-unstable-resources"
}

headers = {
  "Content-Type": "application/json",
  "Authorization": "bearer " + token
}

response = requests.put(url, json=payload, headers=headers, verify=False)

if (response.status_code == 204):
  print("success")
else:
  data = response.json()
  print(data)



#Get workers network config in general:
url = appliance+"/api/v7/workers/networkConfiguration/eastus"

headers = {"Authorization": "bearer " + token}

response = requests.get(url, headers=headers, verify=False)

data = response.json()
print("Getting Worker regions...")
time.sleep(1)
print(json.dumps(data, indent=4))