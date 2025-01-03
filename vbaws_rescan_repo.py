#import module to supress warning
import urllib3
from urllib3.exceptions import InsecureRequestWarning

# Suppress InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

#import modules
import requests
import getpass
import time
import json

# Endpoint URL
appliance = "https://"+input("Enter hostname or IP Address of the appliance and restAPI port (example 127.0.0.1:11005): ")
url = appliance+"/api/v1/token"
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
    'Content-Type': 'application/x-www-form-urlencoded',
    "x-api-version": "1.5-rev0"
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

#GET repo ID

url = appliance+"/api/v1/repositories"


headerstoken = {
  "x-api-version": "1.5-rev0",
  "Authorization": "Bearer "+token
}

response = requests.get(url, headers=headerstoken, verify=False)

data = response.json()
print(json.dumps(data, indent=4))

#RESCAN REPO
repositoryId = input("Enter the repository ID: ")
url = appliance+"/api/v1/repositories/"+repositoryId+"/rescan"


headerstoken = {
  "x-api-version": "1.5-rev0",
  "Authorization": "Bearer "+token
}

response = requests.post(url, headers=headerstoken, verify=False)

data = response.json()
print(json.dumps(data, indent=4))

'''
#GET bottlenecks overview page

url = appliance+"/api/v1/overview/userStatus"

#headers with authorization token
headerstoken = {
  "x-api-version": "1.5-rev0",
  "Authorization": "Bearer "+token
}

response = requests.get(url, headers=headerstoken, verify=False)

data = response.json()
print(json.dumps(data, indent=4))
print("User status information OK.")

#get bottlenecks

url = appliance+"/api/v1/overview/bottlenecks"

response = requests.get(url, headers=headerstoken, verify=False)

data = response.json()
print(json.dumps(data, indent=4))
print("Bottleneck information OK.")

#get statistics
url = appliance+"/api/v1/statistics/summary"

response = requests.get(url, headers=headerstoken, verify=False)

data = response.json()
print(json.dumps(data, indent=4))
print("Statistics information OK.")

#get policies
url = appliance+"/api/v1/virtualMachines/policies"

response = requests.get(url, headers=headerstoken, verify=False)

data = response.json()
print(json.dumps(data, indent=4))
print("Policies retrieved successfully")
'''
