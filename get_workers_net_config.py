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

#Get workers network config in general:
url = appliance+"/api/v7/workers/networkConfiguration"

headers = {"Authorization": "bearer " + token}

response = requests.get(url, headers=headers, verify=False)

data = response.json()
print("Getting Worker regions...")
time.sleep(1)
print(json.dumps(data, indent=4))


#Get workers network config for specific region:
url = appliance+"/api/v7/workers/networkConfiguration"
regionId = input("Enter region ID (Example: eastus): ")
query = {
  "RegionId": regionId,
  "Offset": "0",
  "Limit": "-1"
}

headers = {"Authorization": "bearer " + token}

response = requests.get(url, headers=headers, params=query, verify=False)

data = response.json()
print("Getting specific worker region...")
time.sleep(1)
print(json.dumps(data, indent=4))
