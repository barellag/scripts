import requests
import getpass

#authentication for private endpoints

appliance_ip = input("Enter your appliance IP or hostname: ")

request_url = "https://"+appliance_ip+"/api/"
private_token_url = request_url+"oauth2/token"
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

# Extracting the token from response
if response.status_code == 200:
    print("Token retrieved successfully!")
    token_info = response.json()  # Parse JSON response
    #print(token_info)  # This will print the entire JSON response including the token
    token = token_info.get('access_token')  # Accessing the token directly
    print("Access Token:", token)
else:
    print("Failed to retrieve token")
    print("Status Code:", response.status_code)
    print("Response:", response.text)

