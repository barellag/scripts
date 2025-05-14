using System;
using System.Threading.Tasks;
using Azure;
using Azure.Core;
using Azure.Identity;
using Azure.ResourceManager;
using Azure.ResourceManager.Resources;
using Azure.ResourceManager.Compute;
using Azure.ResourceManager.Compute.Models;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Logging.Console; // Ensure this is included

public class Program
{
    public static async Task Main(string[] args)
    {
        // Set up logging
        using var loggerFactory = LoggerFactory.Create(builder =>
        {
            builder
                .AddConsole() // Requires Microsoft.Extensions.Logging.Console package
                .SetMinimumLevel(LogLevel.Information); // Set the minimum log level
        });
        ILogger logger = loggerFactory.CreateLogger<Program>();

        logger.LogInformation("Starting Azure snapshot creation process.");

        try
        {
            // 1. Authenticate
            var credential = new DefaultAzureCredential();
            var armClient = new ArmClient(credential);

            // 2. Parameters
            Console.Write("Enter Subscription ID: ");
            string subscriptionId = Console.ReadLine();

            Console.Write("Enter Resource Group Name: ");
            string resourceGroupName = Console.ReadLine();

            Console.Write("Enter Snapshot Name: ");
            string snapshotName = Console.ReadLine();

            Console.Write("Enter Disk Name: ");
            string diskName = Console.ReadLine();
            string sourceDiskResource =
                $"/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Compute/disks/{diskName}";

            logger.LogInformation("Parameters set: SubscriptionId={SubscriptionId}, ResourceGroupName={ResourceGroupName}, SnapshotName={SnapshotName}", subscriptionId, resourceGroupName, snapshotName);

            // 3a) Build the RG’s ARM ID
            var rgId = new ResourceIdentifier(
                $"/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}"
            );

            // 3b) Get the ResourceGroupResource for that exact ID
            var resourceGroup = armClient.GetResourceGroupResource(rgId);

            logger.LogInformation("Resource Group '{ResourceGroupName}' found, proceeding to snapshot creation.", resourceGroupName);

            // 4. Build the snapshot payload
            var snapshotData = new SnapshotData(AzureLocation.WestUS)
            {
                CreationData = new DiskCreationData(DiskCreateOption.Copy)
                {
                    SourceResourceId = new ResourceIdentifier(sourceDiskResource)
                },
                Sku = new SnapshotSku
                {
                    Name = SnapshotStorageAccountType.StandardLrs
                }
            };

            // 5. Create (or update) the snapshot
            var lro = await resourceGroup
                .GetSnapshots()
                .CreateOrUpdateAsync(WaitUntil.Completed, snapshotName, snapshotData);

            var snapshot = lro.Value;
            logger.LogInformation("Snapshot '{SnapshotName}' created at '{Location}'.", snapshot.Data.Name, snapshot.Data.Location);

            Console.WriteLine($"✅ Snapshot '{snapshot.Data.Name}' created at '{snapshot.Data.Location}'.");
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "An error occurred during the snapshot creation process.");
        }
    }
}