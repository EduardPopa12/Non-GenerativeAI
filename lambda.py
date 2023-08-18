import boto3
import json
import os

def lambda_handler(event, context):
    # Initialize AWS clients
    ec2_client = boto3.client('ec2')
    s3_client = boto3.client('s3')
    unattached_volumes = []
    not_encrypted_volumes = []
    not_encrypted_snapshots = []
    volumes_response = ec2_client.describe_volumes()
    for volume in volumes_response['Volumes']:
        if 'Attachments' not in volume:
            unattached_volumes.append(volume['VolumeId'])
            if not volume.get('Encrypted'):
                not_encrypted_volumes.append(volume['VolumeId'])


    snapshots_response = ec2_client.describe_snapshots(OwnerIds=['self'])
    for snapshot in snapshots_response['Snapshots']:
        if not snapshot.get('Encrypted'):
            not_encrypted_snapshots.append(snapshot['SnapshotId'])


    metrics = {
        'unattached_volumes': unattached_volumes,
        'not_encrypted_volumes': not_encrypted_volumes,
        'not_encrypted_snapshots': not_encrypted_snapshots
    }

    s3_bucket = os.environ['S3_BUCKET_NAME']
    s3_key = 'metrics.json'
    s3_client.put_object(
        Bucket=s3_bucket,
        Key=s3_key,
        Body=json.dumps(metrics)
    )
