import json
import pandas as pd

from azure.storage.blob import BlobServiceClient
from pyspark.sql import functions as F

# ============================================================
# Converts the json to a sql table, to be 
# ============================================================

# ============================================================
# 1. SETTINGS
# ============================================================

STORAGE_ACCOUNT_URL = (
    "https://customersupportsbase320.blob.core.windows.net"
)

CONTAINER = "raw"

BLOB_NAME = (
    "customer_support/"
    "weekly_data_20260820T233905Z.json"
)


# ============================================================
# 2. CONNECT TO AZURE BLOB STORAGE
# ============================================================

credential = dbutils.credentials.getServiceCredentialsProvider(
    "customer_support_blob"
)

blob_service = BlobServiceClient(
    account_url=STORAGE_ACCOUNT_URL,
    credential=credential,
)

blob_client = blob_service.get_blob_client(
    container=CONTAINER,
    blob=BLOB_NAME,
)


# ============================================================
# 3. DOWNLOAD JSON
# ============================================================

print("Downloading JSON...")

json_bytes = blob_client.download_blob().readall()

data = json.loads(json_bytes)

print("Downloaded successfully")
print("Top-level keys:", data.keys())


# ============================================================
# 4. GET PRODUCTS
# ============================================================

spar_products = data["spar"]["products"]
meny_products = data["meny"]["products"]

print("SPAR products:", len(spar_products))
print("MENY products:", len(meny_products))


# ============================================================
# 5. CONVERT EACH COMPLETE PRODUCT TO A JSON STRING
#
# We deliberately keep ALL fields here.
# ============================================================

rows = []

for product in spar_products:
    rows.append(
        {
            "chain": "spar",
            "product_json": json.dumps(
                product,
                ensure_ascii=False
            ),
        }
    )

for product in meny_products:
    rows.append(
        {
            "chain": "meny",
            "product_json": json.dumps(
                product,
                ensure_ascii=False
            ),
        }
    )


# ============================================================
# 6. CREATE SIMPLE DATAFRAME
#
# At this stage Spark only needs to understand two strings.
# This avoids inference problems with the nested product data.
# ============================================================

pdf = pd.DataFrame(rows)

products_raw_df = spark.createDataFrame(pdf)

products_raw_df.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("products")