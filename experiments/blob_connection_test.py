from azure.storage.blob import BlobServiceClient

from src.config import (
    AZURE_BLOB_PREFIX,
    AZURE_STORAGE_ACCOUNT_URL,
    AZURE_STORAGE_CONTAINER,
    AZURE_STORAGE_CREDENTIAL_NAME,
)

print("Getting Databricks service credential...")

credential = dbutils.credentials.getServiceCredentialsProvider(
    AZURE_STORAGE_CREDENTIAL_NAME
)

print("Connecting to Azure Blob Storage...")

blob_service = BlobServiceClient(
    account_url=AZURE_STORAGE_ACCOUNT_URL,
    credential=credential,
)

blob_client = blob_service.get_blob_client(
    container=AZURE_STORAGE_CONTAINER,
    blob=f"{AZURE_BLOB_PREFIX}/test.txt",
)

print("Uploading test file...")

blob_client.upload_blob(
    "Hello from Databricks!",
    overwrite=True,
)

print("SUCCESS!")
