# backend/be/custom_storage.py
import logging
from storages.backends.s3boto3 import S3Boto3Storage

logger = logging.getLogger(__name__)

class MinioMediaStorage(S3Boto3Storage):
    location = 'media/'
    file_overwrite = False

    def _save(self, name, content):
        logger.info(f"Saving file: {name}")
        return super()._save(name, content)

    def _open(self, name, mode='rb'):
        logger.info(f"Opening file: {name}")
        return super()._open(name, mode)

class MinioStaticStorage(S3Boto3Storage):
    location = 'static/'

    def _save(self, name, content):
        logger.info(f"Saving static file: {name}")
        return super()._save(name, content)

    def _open(self, name, mode='rb'):
        logger.info(f"Opening static file: {name}")
        return super()._open(name, mode)