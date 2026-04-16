from crewai.tools import tool
from google.cloud import bigquery
from google.oauth2 import service_account
import os
from dotenv import load_dotenv
from google.cloud.bigquery.table import RowIterator

load_dotenv()

client = bigquery.Client(
    project=os.getenv("GCP_PROJECT"),
    credentials=service_account.Credentials.from_service_account_file(os.getenv("GCP_CREDENTIAL_LOCATION"))
)

@tool()
def create_dataset(name: str) -> None:
    """
    Creates a new BigQuery dataset in the configured GCP project.
    The dataset is created in the US region by default.
    Use this before creating tables if the target dataset does not yet exist.

    Args:
        name (str): The name of the dataset to create (e.g., 'my_dataset').
    """
    dataset = bigquery.Dataset(client.dataset(name))
    dataset.location = "US"
    client.create_dataset(dataset=dataset)


@tool()
def create_table(ddl: str) -> None:
    """
    Executes a DDL statement to create a new table in BigQuery.
    Use this to define a table schema using a CREATE TABLE SQL statement.
    Ensure the target dataset already exists before calling this tool.

    Args:
        ddl (str): A valid BigQuery DDL statement
                   (e.g., 'CREATE TABLE project.dataset.table (col1 STRING, col2 INT64)').
    """
    query_job = client.query(ddl)
    query_job.result()


@tool()
def dry_run_bq(sql: str) -> str:
    """
    Submits a SQL query to BigQuery as a dry run to validate syntax and estimate costs
    without actually executing it or returning results.
    Use this to verify a query is valid before running it for real.

    Args:
        sql (str): The SQL query string to validate.

    Returns:
        str: A message confirming the query is valid and the estimated bytes processed.
    """
    job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
    query_job = client.query(sql, job_config=job_config)
    bytes_processed = query_job.total_bytes_processed
    return f"Query is valid. Estimated bytes processed: {bytes_processed}"


@tool()
def execute_query(sql: str) -> RowIterator:
    """
    Executes a SQL query on BigQuery and returns the resulting rows.
    Use this for SELECT statements or any DML that returns a result set.
    Avoid using this for DDL — use create_table instead.

    Args:
        sql (str): A valid BigQuery SQL query string.

    Returns:
        RowIterator: An iterable of result rows from the query.
    """
    query_job = client.query(sql)
    return query_job.result()


@tool()
def count_rows_bq(table: str) -> int:
    """
    Returns the total number of rows in a specified BigQuery table.
    Use this to quickly check the size of a table after loading data or running transformations.

    Args:
        table (str): The fully qualified table name in the format 'project.dataset.table'.

    Returns:
        int: The total row count of the table.
    """
    query = f"SELECT COUNT(*) AS total FROM `{table}`"
    query_job = client.query(query=query)
    result = query_job.result()
    return next(iter(result))["total"]


@tool()
def load_gcs_to_bq(uri: str, tbl: str) -> None:
    """
    Loads a CSV file from Google Cloud Storage (GCS) into a BigQuery table.
    Schema is auto-detected from the CSV. The first row is treated as a header and skipped.
    Use this to ingest raw CSV data from GCS into BigQuery for further processing.

    Args:
        uri (str): The GCS URI of the source CSV file (e.g., 'gs://my-bucket/data.csv').
        tbl (str): The fully qualified destination table name (e.g., 'project.dataset.table').
    """
    job_config = bigquery.LoadJobConfig(
        autodetect=True,
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1
    )
    load_job = client.load_table_from_uri(uri, tbl, job_config=job_config)
    load_job.result()


@tool()
def get_table_schema(tbl: str) -> list:
    """
    Retrieves the schema of a BigQuery table as a list of field definitions.
    Use this to inspect column names, types, and modes before writing queries or loading data.

    Args:
        tbl (str): The fully qualified table name in the format 'project.dataset.table'.

    Returns:
        list: A list of field definitions, each represented as a dictionary with keys
              such as 'name', 'type', and 'mode'.
    """
    table = client.get_table(tbl)
    schema = table.schema
    schema_dicts = [field.to_api_repr() for field in schema]
    return schema_dicts