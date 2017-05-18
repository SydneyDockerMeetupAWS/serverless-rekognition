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
        s3 = boto3.client('s3')
        dynamodb = boto3.resource('dynamodb')
        ddb_users_table = dynamodb.Table(users_table)


        ## Get the object from the event
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key'].encode('utf8'))
        etag = event['Records'][0]['s3']['object']['eTag']

        ## Get s3 metadata for object
        metadata = s3.head_object(
                    Bucket = bucket,
                    Key = key,
                    IfMatch = etag)
        # Parse the info
        name = metadata['Metadata']['name']
        surname = metadata['Metadata']['surname']
        user_id = metadata['Metadata']['id']


        ## Index the face
        # TODO: we do not validate the confidence and number of faces here
        response = rekognition.index_faces(
                    CollectionId = collection_id,
                    Image = {
                        'S3Object': {
                            'Bucket': bucket,
                            'Name': key
                        }
                    },
        ExternalImageId = user_id.replace('@', ':at:'),
        DetectionAttributes = ['DEFAULT'] )
        debug_log(json.dumps(response, indent=2), "==== Responce")

        ## Check if we have such id
        item = ddb_users_table.get_item(
                Key = {'id': user_id },
                ConsistentRead=True)

        ## Create user table item and add or update DynamoDB
        if 'Item' in item:
            user = item['Item']
        else:
            user = {
                'id': user_id,
                'name': name,
                'surname': surname,
                'pictures': []
            }

        # Store only first face found
        user['pictures'].append(
                            { 'key': key,
                              'bucket': bucket,
                              'url': '{}/{}/{}'.format(s3.meta.endpoint_url, bucket, key),
                              'faceid': response['FaceRecords'][0]['Face']['FaceId'],
                              'imageid': response['FaceRecords'][0]['Face']['ImageId'],
                              'externalimageid': response['FaceRecords'][0]['Face']['ExternalImageId']
                            })

        result = ddb_users_table.put_item(
                    Item = user)

    except Exception as e:
        # If any other exceptions which we didn't expect are raised
        # then fail the job and log the exception message.
        debug_log('Function failed due to exception.'  + str(e))
        traceback.print_exc()

    debug_log('==== Function complete.')
    return "Complete."
