import boto3
from app.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION_NAME, AWS_S3_BUCKET_NAME

# Create S3 client — this is how you talk to AWS
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION_NAME
)

def upload_video(file, filename: str) -> str:
    """
    Upload video to S3 and return the file URL
    """
    s3_client.upload_fileobj(
        file,                          # the actual video file
        AWS_S3_BUCKET_NAME,            # your bucket
        f"uploads/{filename}",         # path inside bucket
        ExtraArgs={"ContentType": "video/mp4"}
    )

    # Return the S3 URL of the uploaded file
    url = f"https://{AWS_S3_BUCKET_NAME}.s3.{AWS_REGION_NAME}.amazonaws.com/uploads/{filename}"
    return url