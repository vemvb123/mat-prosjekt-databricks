# Upgrade Databricks SDK to the latest version and restart Python to see updated packages
%pip install --upgrade databricks-sdk==0.70.0
%restart_python

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.jobs import JobSettings as Job

useremail = "xxx"
warehouse_id = "xxx"

repo_path = f"/Workspace/Users/{useremail}/mat-prosjekt-databricks"

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
                "task_key": "scrape",
                "spark_python_task": {
                    "python_file": f"{repo_path}/src/scrape.py",
                },
                "environment_key": "Default",
            },
            {
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
                    "warehouse_id": warehouse_id,
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
                    "warehouse_id": warehouse_id,
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
                    "warehouse_id": warehouse_id,
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