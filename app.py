import json
import boto3
from uuid import uuid4

dynamodb = boto3.client('dynamodb', region_name='us-east-1')
table_name = 'lva.lol'

def shorten_url(event, context):
    try:
        request_body = json.loads(event['body'])
        if 'url' not in request_body:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing "url" in the request body'})
            }

        short_url = generate_short_url()

        check_params = {
            'TableName': table_name,
            'Key': {
                'id': {'S': short_url},
            },
        }
        response = dynamodb.get_item(**check_params)
        if 'Item' in response:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Short URL already exists'})
            }

        params = {
            'TableName': table_name,
            'Item': {
                'id': {'S': short_url},
                'url': {'S': request_body['url']},
            },
        }
        dynamodb.put_item(**params)

        shortened_url = f'http://lva.lol/{short_url}'
        return {
            'statusCode': 200,
            'body': shortened_url
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }

def generate_short_url():
    return str(uuid4())[:7]

def redirect_url(event, context):
    try:
        short_url = event['pathParameters']['short_url']
        params = {
            'TableName': table_name,
            'Key': {
                'id': {'S': short_url},
            },
        }
        response = dynamodb.get_item(**params)
        if 'Item' in response and 'url' in response['Item']:
            original_url = response['Item']['url']['S']
            return {
                'statusCode': 302,
                'headers': {'Location': original_url},
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Short URL not found'}),
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }