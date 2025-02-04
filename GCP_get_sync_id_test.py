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

    # First step: submit credentials
    response = requests.post(private_token_url, data=payload, headers=headers, verify=False)

    if response.status_code == 202:
        print("MFA Authentication started...")
        # Check if MFA is required by the API response
        token_info = response.json()
        if token_info.get('description') == 'mfa required':
            # Extract MFA token if provided as part of challenge
            mfa_token = token_info.get('mfa_token', '')

            # Prompt user for MFA code
            mfa_code = input("Enter your MFA code: ")

            # Prepare payload for MFA submission
            mfa_payload = {
                "grant_type": "mfa",
                "mfa_token": mfa_token,
                "mfa_code": mfa_code
            }

            # Submit MFA details
            mfa_response = requests.post(private_token_url, data=mfa_payload, headers=headers, verify=False)

            if mfa_response.status_code == 200:
                # MFA auth successful, retrieve final token
                final_token_info = mfa_response.json()
                token = final_token_info.get('access_token')
                print("Authenticated successfully with MFA!")
                authenticated = True
            else:
                print("Failed MFA authentication. Please try again.")
                print("Status Code:", mfa_response.status_code)
                print("Response:", mfa_response.text)
        
        else:
            print("Authenticated successfully!")
            token = token_info.get('access_token')
            authenticated = True

    elif response.status_code == 200:
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



data = response.json()
print(json.dumps(data, indent=4))
with open("response_initial.json", "w") as file:
    json.dump(data, file, indent=4)

#repeating the request with problematic ID:

endpoint_url2 = request_url+"v1/collection/synchronizationItems?fromUsn=80601752&creationTimeUtc=2024-04-24T19%3A19%3A04&pageSize=2048&synchronizationId=8d8f824c-46ff-4829-8e4d-ade729e65869&includeTombstones=true"

headers = {
    "x-api-version": "1.0-rev4",
    "Authorization": "bearer "+token
}
response = requests.get(endpoint_url2, headers=headers, verify=False)

data = response.json()
print(json.dumps(data, indent=4))
with open("response_with_id.json", "w") as file:
    json.dump(data, file, indent=4)
