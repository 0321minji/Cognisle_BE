import io
import boto3
import uuid
from django.conf import settings
from Cognisle.settings import development
from datetime import datetime


def get_random_text(length):
    return str(uuid.uuid4()).replace('-', '')[:length]

def s3_file_upload_by_file_data(upload_file, region_name, bucket_name, bucket_path, content_type=None):
    bucket_name = bucket_name.replace('/', '')
    # 파일 확장자 추출
    if content_type:
        content_type = content_type
    else:
        content_type = upload_file.content_type

    now = datetime.now()
    random_str = get_random_text(20)
    extension = upload_file.name.split('.')[-1]

    #random_file_name = '{}.{}'.format(str(now.strftime('%Y%m%d%H%M%S'))+random_str,extension)
    # 파일의 ContentType을 설정
    random_file_name = f"{now.strftime('%Y%m%d%H%M%S')}_{random_str}.{extension}"
    upload_file_path_name = f"{bucket_path}/{random_file_name}"
    print(upload_file_path_name)
    s3 = boto3.resource('s3', region_name=region_name, aws_access_key_id=development.AWS_ACCESS_KEY_ID, aws_secret_access_key=development.AWS_SECERT_ACCESS_KEY)

    try:
        # 버킷이 존재하는지 확인
        s3.meta.client.head_bucket(Bucket=bucket_name)
    except s3.meta.client.exceptions.NoSuchBucket:
        raise Exception(f"The specified bucket does not exist: {bucket_name}")

    file_data = io.BytesIO(upload_file.read())

    try:
        # 파일을 S3에 업로드
        s3.Bucket(bucket_name).put_object(Key=upload_file_path_name, Body=file_data, ContentType=content_type)
        #return f"https://{bucket_name}.s3.{region_name}.amazonaws.com/{upload_file_path_name}"
        return f"https://s3.{region_name}.amazonaws.com/{bucket_name}/{upload_file_path_name}"
    except Exception as e:
        print(f"Failed to upload file to S3: {e}")
        return False
