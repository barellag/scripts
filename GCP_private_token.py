import requests
import getpass
import json


#authentication for private endpoints

appliance_ip = input("Enter your appliance IP or hostname: ")

request_url = "https://"+appliance_ip+"/api/"
private_token_url = request_url+"oauth2/token"


# Initialize a variable to control the loop
authenticated = False

# Start the loop for user authentication
while not authenticated:
    username = input("Enter the username: ")
    password = getpass.getpass("Enter Password: ")

    payload = {
        "grant_type": "password",
        "username": username,
        "password": password,
        "use_short_term_refresh": "false",
        "rememberMe": "true"
    }

    headers = {
        "x-api-version": "1.0-rev4",
    }

    response = requests.post(private_token_url, data=payload, headers=headers, verify=False)

    # Check response status to determine if authentication is successful
    if response.status_code == 200:
        print("Token retrieved successfully!")
        token_info = response.json()  # Parse JSON response
        token = token_info.get('access_token')  # Retrieve the token
        authenticated = True  # Set the flag to exit the loop
    else:
        print("Failed to retrieve token. Please check your credentials and try again.")
        print("Status Code:", response.status_code)
        print("Response:", response.text)

#Calling Synchronization ID

endpoint_url = request_url+"v1/collection/synchronizationItems?fromUsn=0&creationTimeUtc=2024-04-24T19%3A19%3A04&pageSize=2048&includeTombstones=true"

headers = {
    "x-api-version": "1.0-rev4",
    "Authorization": "bearer "+token
}
response = requests.get(endpoint_url, headers=headers, verify=False)

