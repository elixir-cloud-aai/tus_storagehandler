"""This module provides functionality for managing MinIO client."""

import logging

from foca import Foca
from minio import Minio

from cloud_storage_handler.api.elixircloud.csh.models import MinioConfig
from cloud_storage_handler.utils import get_config_path

logger = logging.getLogger(__name__)


class MinioConfigurationData:
    """Handles the loading and parsing of MinIO configuration files."""

    def __init__(self, config_file=None):
        """Initialize MinioConfig with a configuration file.

        Args:
            config_file : Path to the configuration file. If not provided,
                               uses the default path.
        """
        config_file = config_file or get_config_path()
        self.config = Foca(config_file=config_file).conf

    def get_minio_config(self) -> MinioConfig:
        """Retrieve the MinIO configuration.

        Returns:
            A dictionary containing the MinIO configuration.
        """
        minio_config = self.config.custom.get("minio")
        return MinioConfig(
            hostname=minio_config["hostname"],
            port=minio_config["port"],
            access_key=minio_config["access_key"],
            secret_key=minio_config["secret_key"],
            bucket_name=minio_config["bucket_name"],
        )


class MinioClient:
    """A class to manage MinIO client configuration and bucket creation."""

    def __init__(self):
        """Initialize the MinIO client and create bucket if necessary."""
        config = MinioConfigurationData().get_minio_config()
        self.client = Minio(
            endpoint=f"{config.hostname}:{config.port}",
            access_key=config.access_key,
            secret_key=config.secret_key,
            secure=False,
        )
        self.bucket_name = config.bucket_name

        # Create bucket if it doesn't exist
        self.create_bucket()

    def create_bucket(self):
        """Creation of bucket using the configured bucket name."""
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)
            logger.info(f"Bucket '{self.bucket_name}' created.")
        else:
            logger.info(f"Bucket '{self.bucket_name}' already exists.")

    def get_client(self):
        """Return the MinIO client."""
        return self.client
