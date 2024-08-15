from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


# Custom storage backend for static files, using Amazon S3
class StaticStorage(S3Boto3Storage):
    # Specifies the directory within the S3 bucket where static files will be stored
    location = settings.STATICFILES_LOCATION


# Custom storage backend for media files, using Amazon S3
class MediaStorage(S3Boto3Storage):
    # Specifies the directory within the S3 bucket where media files will be stored
    location = settings.MEDIAFILES_LOCATION
