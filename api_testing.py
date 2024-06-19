#first import some modules to check if the needed modules are installed
import importlib
import subprocess

def import_and_install_module(module_name):
    try:
        importlib.import_module(module_name)
    except ImportError:
        print(f"The module {module_name} is missing. Installing it now...")
        subprocess.call(['pip', 'install', module_name])

#modules array that are required
required_modules = ["maskpass", "requests"]

#check and install the required modules
for module in required_modules:
    import_and_install_module(module)

import requests
import maskpass
import urllib3

#Disable_Warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#getting appliance's credentials
veeamUserName = input("Enter username: ")
VeeamUserPwd = maskpass.askpass(prompt="Enter your password: ", mask="*")

#getting appliance's IP and API port
veeamBackupAWSServer = "127.0.0.1" #input("Enter hostname or ip: ")
veeamBackupAWSPort = "11005" #input("Enter API port: ")
apiVersion = "1.5-rev0"
apiUrl = "https://"+veeamBackupAWSServer+":"+veeamBackupAWSPort+"/"+"api/v1/"


#get-ApiToken
print("Getting API token...")
url = apiUrl+"token"

payload = {
    "grant_type": "password",
    "username": veeamUserName,
    "password": VeeamUserPwd,
}
headers = {
  "Content-Type": "application/x-www-form-urlencoded",
  "x-api-version": apiVersion
}

response = requests.post(url, data=payload, headers=headers, verify=False)
data = response.json()
#save token to variable
access_token = data["access_token"]
accessToken = "bearer "+access_token

#Getting IAMRoleID
url = apiUrl+"accounts/amazon"
query = {
    "SearchPattern": input("Enter IAM Role name: ")
}
headers = {
  "x-api-version": "1.5-rev0",
  "Authorization": accessToken
}
response = requests.get(url, headers=headers, params=query, verify=False)
data = response.json()
#print(data)
iamRoleId = data["results"][0]["id"]
awsAccountId = data["results"][0]["awsAccountId"]

#get AWS regions
url = apiUrl+"cloudInfrastructure/regions"

query = {
  "SearchPattern": input("Enter region name: "),
}

headers = {
  "x-api-version": "1.5-rev0",
  "Authorization": accessToken
}

response = requests.get(url, headers=headers, params=query, verify=False)
data = response.json()
regionId = data["results"][0]["id"]
regionName = data["results"][0]["name"]


#Add amazon connection
url = apiUrl+"amazonConnections"

payload = {
  "authenticationSpecification": {
    "authenticationType": "CloudAccount",
    "IAMRoleId": iamRoleId
  },
  "regionId": regionId
}

headers = {
  "Content-Type": "application/json",
  "x-api-version": "1.5-rev0",
  "Authorization": accessToken
}

response = requests.post(url, json=payload, headers=headers, verify=False)

data = response.json()
amazonConnectionId = data["id"]

#Scan AZs
amazon_connection_id = amazonConnectionId
url = apiUrl + "amazonConnections/" + amazon_connection_id + "/availabilityZones"

headers = {
  "x-api-version": "1.5-rev0",
  "Authorization": accessToken
}

response = requests.get(url, headers=headers, verify=False)

data = response.json()

#Scan AWS regions
url = apiUrl+"cloudInfrastructure/regions/" + regionId

headers = {
  "x-api-version": "1.5-rev0",
  "Authorization": accessToken
}

response = requests.get(url, headers=headers, verify=False)

data = response.json()

#get AZs for a region
whichAz = input("Enter the AZ you want to use (a, b, c, etc): ")
region_id = regionId
regionAndAz = regionName+whichAz
url = apiUrl+"cloudInfrastructure/regions/" + region_id + "/zones"

query = {
    "SearchPattern": regionAndAz
}

headers = {
  "x-api-version": "1.5-rev0",
  "Authorization": accessToken
}

response = requests.get(url, headers=headers, params=query, verify=False)

data = response.json()
azId = data["results"][0]["id"]

#workers in prod
url = apiUrl+"workers/networkConfiguration/production"

payload = {
  "awsAccountId": awsAccountId,
  "IAMRoleId": iamRoleId,
  "availableZoneId": azId,
  "cloudNetworkId": input("Enter VPC ID: "),
  "cloudSubnetworkId": input("Enter subnet ID: "),
  "cloudSecurityGroupId": input("Enter Security Group ID: ")
}

headers = {
  "Content-Type": "application/json",
  "x-api-version": "1.5-rev0",
  "Authorization": accessToken
}

response = requests.post(url, json=payload, headers=headers, verify=False)

data = response.json()
print("Worker configuration created for region "+regionName+" on account "+awsAccountId+".")