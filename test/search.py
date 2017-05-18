import boto3
import sys
import json

file_name = sys.argv[1]
lambda_name = sys.argv[2]

f = open (file_name, 'rb')
l = boto3.client('lambda', region_name='us-west-2')

payload = {
    'image': f.read()
}

responce = l.invoke (
            FunctionName = lambda_name,
            InvocationType = 'RequestResponse',
            LogType = 'None',
            Payload = json.dumps(payload))

print response
