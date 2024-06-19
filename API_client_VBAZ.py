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

#GET-VM URL
GETVMURL = appliance+"/api/v6/virtualMachines"

# Headers can include content type or other necessary items
headers_token = {
    "Authorization": "Bearer "+token
}
# Send the GET request
response = requests.get(GETVMURL, headers=headers_token, verify=False)
data = response.json()
#print (data)

#POST VM Rescan
posturl  = appliance+"/api/v6/virtualMachines/rescan"

# Headers can include content type or other necessary items
response = requests.post(posturl, headers=headers_token, verify=False)

data = response.json()
operationID = data['id']
print("Operation ID: "+operationID)

#wait a couple seconds
print("Checking rescan status...")
time.sleep(2)
print("Please wait...")
time.sleep(2)
print("Checking status...")
time.sleep(2)

#Check Status
getStatusURL  = appliance+"/api/v6/operations/"+operationID

response = requests.get(getStatusURL, verify=False, headers=headers_token)

data = response.json()
while data['status'] == 'Running':
    time.sleep(5)
    print("Still scanning, please wait...")
    response = requests.get(getStatusURL, verify=False, headers=headers_token)
    data = response.json()
else:
    #print(data)
    print("Rescan complete!!!")

#export data
print("Exporting data...")
getExportURL  = appliance+"/api/v6/virtualMachines/export"

response = requests.post(getExportURL, headers=headers_token, verify=False)

dataexport = response.json()
print(json.dumps(dataexport, indent=4))