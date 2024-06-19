#import modules
import winrm
import getpass

#collect variables
port = "Paste_the_port_between_these_quotes" #replace with the port number
passwd = "Paste_the_password_between_these_quotes" #replace with the password generated on GCP
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
ps_command = "New-Item -ItemType Directory -Path C:\\Temp_Veeam_test"

# Execute the PowerShell command
result = session.run_ps(ps_command)


ps_command_dir = "Get-ChildItem -Path C:\\"
result_dir = session.run_ps(ps_command_dir)
print(result_dir)
print("Directory created successfully")