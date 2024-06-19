#Collecting logs
import requests
import getpass
import urllib3
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

#Collect logs
#how many days?
#days = input('How many days of logs? ')
url_logs = appliance+'/api/v6/system/logs'

days = input("how many days of logs? ")
query = {
  "ExportLogsType": "LastDays",
  "Days": days,
}

headers_token = {"Authorization": "Bearer "+token}

response = requests.get(url_logs, headers=headers_token, params=query, verify=False)

if response.status_code == 200:
    # Save the response content to a file
    with open('logs.zip', 'wb') as file:
        file.write(response.content)
    print("Logs downloaded successfully and saved as logs.zip")
else:
    print("Failed to download logs")
    print("Status Code:", response.status_code)
    print("Response:", response.text)