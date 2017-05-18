import boto3
import urllib
import traceback
import json
import os

DEBUG = True

def debug_log(s, comment=""):
    if DEBUG:
        print comment
        print s

def handler(event, context):
    try:
        debug_log(json.dumps(event, indent=2), "==== Function started")

        ## Get env variables for collection id and dynamo_db
        collection_id = os.environ['COLLECTION_ID']
        users_table = os.environ['USERS_TABLE']

        ## Create AWS clients for services
        rekognition = boto3.client('rekognition')
        dynamodb = boto3.resource('dynamodb')
        ddb_users_table = dynamodb.Table(users_table)

        ## Search through collection
        response = rekognition.search_faces_by_image(
                    CollectionId = collection_id,
                    Image={ 'S3Object': {
                                'Bucket': event['bucket'],
                                'Name': event['key']} },
                    MaxFaces=5,
                    FaceMatchThreshold=75)

        debug_log(json.dumps(response, indent=2), "==== Rekognition responce")

        ## Find all unique user's id
        user_ids = set(face['Face']['ExternalImageId'] for face in response["FaceMatches"])

        ## If one and only one id found
        if len(user_ids) == 1:
            user_id = user_ids.pop()
            info = ddb_users_table.get_item(
                    Key = {'id': user_id.replace(':at:', '@') },
                    ConsistentRead=False)
            return info['Item']

    except Exception as e:
        # If any other exceptions which we didn't expect are raised
        # then fail the job and log the exception message.
        debug_log('Function failed due to exception.'  + str(e))
        traceback.print_exc()

    debug_log('==== Function complete.')
    return "Not found."
