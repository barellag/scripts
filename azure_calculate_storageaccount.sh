# Define variables
storageAccountName="Enter SA name"
resourceGroupName="ENTER_RG_NAME_HERE"
containerName="Enter Container Name"
basePath="Veeam/Backup/backup/Clients/{83c15758-8a81-49d8-b2d1-5f08110e0bd0}"

# Start AZ session
az login

# Obtain account key
accountKey=$(az storage account keys list -g $resourceGroupName -n $storageAccountName --query "[0].value" -o tsv)

# List blobs with their sizes and paths
az storage blob list --account-name $storageAccountName --account-key $accountKey --container-name $containerName --prefix $basePath/ --query "[].{name:name, size:properties.contentLength}" -o json |
jq -r '.[] | "\(.name) \(.size)"' | 
awk -v prefixPath="$basePath/" '
{
    # Extract relative path by removing the base path from the blob name
    path = substr($1, length(prefixPath) + 1)  # Start right after basePath including slash
    # Split path to get immediate directory under basePath
    split(path, parts, "/")

    if (length(parts) > 0 && parts[1] != "") {
        size[parts[1]] += $2  # Accumulate sizes under the first directory after basePath
    }
}
END {
    # Output all directories, including those with small total sizes
    for (dir in size) {
        printf "%s%s: %.2f MB\n", prefixPath, dir, size[dir] / (1024*1024)
    }
}' > output.json