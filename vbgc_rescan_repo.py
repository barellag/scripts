#Collecting logs
import requests
import getpass
import urllib3
import time
from urllib3.exceptions import InsecureRequestWarning

# Suppress InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

# Endpoint URL
appliance = "https://"+input("Enter hostname or IP Address of the appliance: ")+":13140"
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

#Rescan repository
repository_id = input("Enter the repository id: ")

url = appliance+"/api/v1/repositories/" + repository_id + "/rescan"

headers = {
  "x-api-version": "1.3-rev0",
  "Authorization": "Bearer "+token
}

response = requests.post(url, headers=headers, verify=False)

data = response.json()
#print(data)
#save session to variable
session_id = data['sessionIds'][0]
print(session_id)

#get session results
url = appliance+"/api/v1/sessions/" + session_id

headers = {
  "x-api-version": "1.3-rev0",
  "Authorization": "Bearer "+token
}

while True:
    response = requests.get(url, headers=headers, verify=False)

    data = response.json()
    if data['state'] == 'Success':
        print("Rescan succeeded")
        break
    elif data['state'] == 'Running':
        print("Please wait, rescan in progress...")
        time.sleep(5)  # wait for 5 seconds before the next check
    else:
        print("Rescan failed with state: ", data['state'])
        break