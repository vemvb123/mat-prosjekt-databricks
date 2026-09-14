# Upgrade Databricks SDK to the latest version and restart Python to see updated packages
%pip install --upgrade databricks-sdk==0.70.0
%restart_python

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.jobs import JobSettings as Job

from src.config import USER_EMAIL, WAREHOUSE_ID

# Databricks workspace path where this repository is expected to be checked out.
repo_path = f"/Workspace/Users/{USER_EMAIL}/mat-prosjekt-databricks"

# Jobben kjører hele dataflyten fra scraping til ferdig gold-tabell.
Weekly_Scrape_Job = Job.from_dict(
    {
        "name": "Weekly Scrape Job",
        "schedule": {
            "quartz_cron_expression": "20 0 3 ? * Mon",
            "timezone_id": "Europe/Oslo",
            "pause_status": "UNPAUSED",
        },
        "tasks": [
            {
                # First task: scrape products from the store APIs and save raw JSON.
                "task_key": "scrape",
                "spark_python_task": {
                    "python_file": f"{repo_path}/src/scrape.py",
                },
                "environment_key": "Default",
            },
            {
                # Second task: turn the chosen JSON file into the products Delta table.
                "task_key": "scraped_json_to_sql_table",
                "depends_on": [
                    {
                        "task_key": "scrape",
                    },
                ],
                "spark_python_task": {
                    "python_file": f"{repo_path}/src/products.py",
                },
                "environment_key": "Default",
            },
            {
                # SQL layers build progressively cleaner tables: bronze, silver, then gold.
                "task_key": "bronze",
                "depends_on": [
                    {
                        "task_key": "scraped_json_to_sql_table",
                    },
                ],
                "sql_task": {
                    "file": {
                        "path": f"{repo_path}/sql/bronze.sql",
                        "source": "WORKSPACE",
                    },
                    "warehouse_id": WAREHOUSE_ID,
                },
            },
            {
                "task_key": "silver",
                "depends_on": [
                    {
                        "task_key": "bronze",
                    },
                ],
                "sql_task": {
                    "file": {
                        "path": f"{repo_path}/sql/silver.sql",
                        "source": "WORKSPACE",
                    },
                    "warehouse_id": WAREHOUSE_ID,
                },
            },
            {
                "task_key": "gold",
                "depends_on": [
                    {
                        "task_key": "silver",
                    },
                ],
                "sql_task": {
                    "file": {
                        "path": f"{repo_path}/sql/gold.sql",
                        "source": "WORKSPACE",
                    },
                    "warehouse_id": WAREHOUSE_ID,
                },
            },
        ],
        "queue": {
            "enabled": True,
        },
        "environments": [
            {
                "environment_key": "Default",
                "spec": {
                    "environment_version": "5",
                },
            },
        ],
        "performance_target": "PERFORMANCE_OPTIMIZED",
    }
)

w = WorkspaceClient()

# Create a new job:
w.jobs.create(**Weekly_Scrape_Job.as_shallow_dict())

# If you want to update an existing job instead, use:
# w.jobs.reset(new_settings=Weekly_Scrape_Job, job_id=YOUR_JOB_ID)
