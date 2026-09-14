import json
import time
from typing import Any
from urllib import error, request
from datetime import datetime, timezone
from azure.storage.blob import BlobServiceClient

from config import (
    AZURE_BLOB_PREFIX,
    AZURE_STORAGE_ACCOUNT_URL,
    AZURE_STORAGE_CONTAINER,
    AZURE_STORAGE_CREDENTIAL_NAME,
    PLATFORM_REST_BASE_URL,
    SCRAPE_FILENAME_PREFIX,
)

# One config entry per chain keeps API IDs and website URLs in one place.
CHAIN_CONFIGS = {
    "spar": {
        "key": "spar",
        "chain_id": "1210",
        "name": "SPAR",
        "site_base_url": "https://spar.no",
    },
    "meny": {
        "key": "meny",
        "chain_id": "1300",
        "name": "MENY",
        "site_base_url": "https://meny.no",
    },
}


def get_selected_chain_keys(requested_chain_keys: list[str] | None) -> list[str]:
    # Default to all configured chains when no valid chain list is provided.
    valid_keys = ["spar", "meny"]
    selected: list[str] = []

    for chain_key in requested_chain_keys or []:
        if chain_key in valid_keys and chain_key not in selected:
            selected.append(chain_key)

    return selected or valid_keys


def get_product_compare_unit(compare_unit: str | None) -> str:
    # Product comparison units should be either liter or kilo.
    return "l" if compare_unit == "l" else "kg"


def get_page_content(url: str) -> str:
    # Send browser-like headers so the public product API accepts the request.
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0 Safari/537.36",
        "Accept-Language": "nb-NO,nb;q=0.9,en;q=0.8",
    }
    req = request.Request(url, headers=headers)
    with request.urlopen(req, timeout=60) as response:
        return response.read().decode("utf-8")


def get_json(url: str) -> Any:
    # All product API endpoints return JSON payloads.
    return json.loads(get_page_content(url))


def get_json_with_retry(url: str, max_attempts: int = 3) -> Any:
    # The store API can fail temporarily, so retry before giving up.
    last_exc: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            return get_json(url)
        except Exception as exc:  # pragma: no cover - network path
            last_exc = exc
            if attempt >= max_attempts:
                raise
            time.sleep(0.7 * attempt)

    raise last_exc or RuntimeError("Unexpected retry failure")


def test_is_catalog_window_limit_failure(exc: Exception, page: int, page_size: int) -> bool:
    # The provider API may stop returning pages around offset 10 000.
    offset = (page - 1) * page_size
    if offset < 10000:
        return False

    if isinstance(exc, error.HTTPError):
        return exc.code >= 500

    return "500" in str(exc)


def get_chain_config(chain_key: str) -> dict[str, str]:
    # Fail fast if an unknown chain key is used.
    return CHAIN_CONFIGS[chain_key]


def get_default_store(chain_config: dict[str, str]) -> dict[str, Any]:
    # The product API needs a store GLN before it can return catalog products.
    url = f"{PLATFORM_REST_BASE_URL}/api/extended-user/{chain_config['chain_id']}/default"
    user = get_json_with_retry(url)
    return user["store"]


def fetch_chain_catalog(chain_key: str) -> tuple[list[dict[str, Any]], list[str], dict[str, Any]]:
    # Fetch the default store first, then read the full catalog for that store.
    chain_config = get_chain_config(chain_key)
    store = get_default_store(chain_config)
    page = 1
    page_size = 250
    products: list[dict[str, Any]] = []
    warnings: list[str] = []

    # Fetch products page by page until the API returns a partial final page.
    while True:
        url = (
            f"{PLATFORM_REST_BASE_URL}/api/products/{chain_config['chain_id']}/{store['gln']}/"
            f"?page={page}&page_size={page_size}&fieldset=maximal&showNotForSale=true"
        )
        try:
            response = get_json_with_retry(url)
        except Exception as exc:  # pragma: no cover - network path
            if test_is_catalog_window_limit_failure(exc, page, page_size):
                warnings.append(
                    f"{chain_config['name']}-katalogen ser ut til å stoppe rundt produkt-offset 10 000 i leverandørens API."
                )
                break
            raise

        hits = response.get("hits") or []
        products.extend(hits)

        # A page smaller than page_size means this was the last catalog page.
        if len(hits) < page_size:
            break

        page += 1

    return products, warnings, store


def get_products():
    # Keep each chain separated so later steps can preserve the source chain.
    all_products = {}
    for key in CHAIN_CONFIGS:
        products, warnings, store = fetch_chain_catalog(key)
        all_products[key] = {
            "products": products
        }
    # returnerte tidligere products, men trur det var feil
    # trur riktig verdi er all_products
    return all_products

def put_data_into_blob() -> str:

    print("gets data")
    all_products = get_products()

    # Add retrieval time both to the JSON content and to the filename.
    print("creates timestamp")
    retrieved_at = datetime.now(timezone.utc)
    all_products["retrieved_at"] = retrieved_at.isoformat()

    print("creates filename")
    file_timestamp = retrieved_at.strftime("%Y%m%dT%H%M%SZ")
    filename = f"{SCRAPE_FILENAME_PREFIX}_{file_timestamp}.json"

    print("saving dict to json")
    json_content = json.dumps(
        all_products,
        ensure_ascii=False,
        indent=2,
    )

    # Get the Azure identity from the Databricks Service Credential
    credential = dbutils.credentials.getServiceCredentialsProvider(
        AZURE_STORAGE_CREDENTIAL_NAME
    )

    # Connect to your normal Azure Blob Storage account
    blob_service = BlobServiceClient(
        account_url=AZURE_STORAGE_ACCOUNT_URL,
        credential=credential,
    )

    blob_path = f"{AZURE_BLOB_PREFIX}/{filename}"

    # Point to the exact blob path where this run should be stored.
    blob_client = blob_service.get_blob_client(
        container=AZURE_STORAGE_CONTAINER,
        blob=blob_path,
    )

    print("putting data in azure storage")
    blob_client.upload_blob(
        json_content,
        overwrite=False,
    )

    destination = (
        f"{AZURE_STORAGE_ACCOUNT_URL}/"
        f"{AZURE_STORAGE_CONTAINER}/{blob_path}"
    )

    print(f"Saved JSON to: {destination}")
    return destination



if __name__ == "__main__":
    put_data_into_blob()


