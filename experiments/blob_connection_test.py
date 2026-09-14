from azure.storage.blob import BlobServiceClient

print("Getting Databricks service credential...")

credential = dbutils.credentials.getServiceCredentialsProvider(
    "customer_support_blob"
)

print("Connecting to Azure Blob Storage...")

blob_service = BlobServiceClient(
    account_url="https://customersupportsbase320.blob.core.windows.net",
    credential=credential,
)

blob_client = blob_service.get_blob_client(
    container="raw",
    blob="customer_support/test.txt",
)

print("Uploading test file...")

blob_client.upload_blob(
    "Hello from Databricks!",
    overwrite=True,
)

print("SUCCESS!")