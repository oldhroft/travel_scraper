import boto3
import os
import json

from travel_scraper.utils import add_meta, config_logger
import logging
logger = logging.getLogger()

def load_process_meta_from_s3(
    client, Bucket: str, Key: str,
) -> list:
    get_object_response = client.get_object(
        Bucket=Bucket, Key=Key)
    
    meta = json.loads(get_object_response["Body"].read())

    if "failed" not in meta:
        meta["failed"] = "NULL"
    else:
        meta["failed"] = "true" if meta["failed"] else "false"
    if "exception" not in meta:
        meta["exception"] = None
    if "global_id" not in meta:
        meta["global_id"] = None

    meta["stat"] = json.dumps(meta["stat"])
    meta["func_args"] = json.dumps(meta["func_args"])

    return meta

if __name__ == "__main__":
    boto_session = boto3.session.Session(
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    )

    s3 = boto_session.client(
        service_name="s3",
        endpoint_url=os.environ["AWS_ENDPOITNT_URL"],
        region_name=os.environ["AWS_REGION_NAME"],
    )
    config_logger(logger, "parser", "logs")

    KEY = "parsing_data/travelata/092fede2-efdb-40c3-866d-c07ae9c4c221/meta.json"
    result = load_process_meta_from_s3(s3, "parsing", KEY)
    print(result)