import os
import boto3

# Create CloudWatch client
cloudwatch = boto3.client('cloudwatch')

def record_cloudwatch_metric():
    cloudwatch.put_metric_data(
        MetricData=[
            {
                'MetricName': 'PANEL_READ',
                'Dimensions': [
                    {
                        'Name': 'CELLAR_NAME',
                        'Value': os.environ['CELLAR_NAME']
                    },
                ],
                'Unit': 'None',
                'Value': 1.0
            },
        ],
        Namespace='CELLAR/INFO'
    )