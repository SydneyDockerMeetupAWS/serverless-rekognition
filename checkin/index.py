import json
import datetime
import boto3
import base64
import os


def handler(event, context):
    
    message = ''
    
    bucketName = os.environ['BUCKET']    
    searchLambdaFunction = os.environ['SEARCH_LAMBDA_FUNCTION']

    if "snapshot" in event:
        snapshot = event['snapshot'].replace("data:image/jpeg;base64,","")

        photo = base64.b64decode(snapshot)

        timestamp = datetime.datetime.utcnow().isoformat()
        
        key = 'test/' + timestamp + '.jpeg'

        response = boto3.client('s3').put_object(Body=photo,Bucket=bucketName,Key=key)
        #print('response is ' + json.dumps(response))
        
        request = {}
        
        request['bucket'] = bucketName
        request['key'] = key
        
        #print('request is ' + json.dumps(request))
        
        response = boto3.client('lambda').invoke(
            FunctionName=searchLambdaFunction,
            InvocationType='RequestResponse',
            Payload=json.dumps(request)
        )
        
        data = response['Payload'].read()
        
        #print('data is ' + str(data))
    
        if "name" in data:
            
            ## Parse the JSON response to obtain the name
            jsonResponse = json.loads(data)
            name = jsonResponse['name']
            
            ## Create the welcome message
            data = {
                'output': 'Welcome ' + name + ', thanks for joining our presentation. You are good to go!',
                'timestamp': datetime.datetime.utcnow().isoformat()
            }
            response = {'statusCode': 200,
                        'body': json.dumps(data),
                        'headers': {'Content-Type': 'application/json'}}
        else:
            ## Error message, as record could not be found
            data = {
                'output': 'Sorry, we could not find you. Please come to the desk :(',
                'timestamp': datetime.datetime.utcnow().isoformat()
            }
            response = {'statusCode': 404,
                        'body': json.dumps(data),
                        'headers': {'Content-Type': 'application/json'}}
    else:
        ## Error message, as record could not be found
        data = {
            'output': 'Sorry, we could not find you. Please come to the desk :(',
            'timestamp': datetime.datetime.utcnow().isoformat()
        }
        response = {'statusCode': 500,
                    'body': json.dumps(data),
                    'headers': {'Content-Type': 'application/json'}}

    ## Submit the response
    return response