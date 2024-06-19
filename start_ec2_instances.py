import boto3

# List of instance IDs to start
instance_ids = ["i-081c1f40067a1dda2", "i-0c487a87144e03729", "i-0ee8e0fadc2f2e190", "i-00d54e97fa6c41e5a", "i-081c1f40067a1dda2", "i-09d24fe8eed49ae4e", "i-0e6f3d3e815b6ae20", "i-0ab7316cfb0fa0c02", "i-0b82998bf9fc79391"]

# AWS region
region = 'us-east-1'  # Change to your region

# Create a boto3 client to interact with EC2
ec2 = boto3.client('ec2', region_name=region)

# Start the instances
try:
    response = ec2.start_instances(InstanceIds=instance_ids, DryRun=False)
    print('Success', response)
except Exception as e:
    print('Error starting instances:', e)
