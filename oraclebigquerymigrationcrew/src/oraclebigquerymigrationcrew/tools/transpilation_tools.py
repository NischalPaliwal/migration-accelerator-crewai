import sqlglot
from crewai.tools import tool

@tool()
def transpile_oracle_to_bq(oracle_sql: str) -> str:
    """
    Converts Oracle SQL schemas, tables, views and basic stored procedures
    into Google BigQuery standard SQL dialect using sqlglot.
    """
    try:
        result = sqlglot.transpile(
            oracle_sql, 
            read="oracle", 
            write="bigquery", 
            pretty=True
        )
        
        return "\n".join(result)
    
    except sqlglot.errors.ParseError as e:
        return f"SQL Parsing Error: Check if the Oracle syntax is valid. Details: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"