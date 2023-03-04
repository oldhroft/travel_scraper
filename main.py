import boto3
import os

if __name__ == "__main__":
    boto_session = boto3.session.Session(
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"]
    )

    client = boto3.client(
        'lambda', region_name=os.environ["AWS_REGION_NAME"],
        endpoint_url="serverless-functions.api.cloud.yandex.net:443"
        
    )
    print(client.list_functions())