# backend/be/custom_storage.py
import logging
from storages.backends.s3boto3 import S3Boto3Storage

logger = logging.getLogger(__name__)

class MinioMediaStorage(S3Boto3Storage):
    location = 'media/'
    file_overwrite = False
