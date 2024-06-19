#import modules
import winrm
import getpass

#collect variables
port = input("Enter port number: ")
passwd = getpass.getpass("Enter the Password: ")
winrm_host = "https://localhost:"+port+"/wsman"
winrm_user = "veeam_restore_user"
winrm_pass = passwd

# Set up the WinRM session
session = winrm.Session(
    winrm_host,
    auth=(winrm_user, winrm_pass),
    server_cert_validation='ignore',
    transport='ntlm'
)

# Create a test directory using powershell
ps_command = "New-Item -ItemType Directory -Path C:\Temp_Veeam_test"

# Execute the PowerShell command
result = session.run_ps(ps_command)
print("Directory created successfully")