from crewai.tools import tool
import oracledb
import os
from dotenv import load_dotenv

load_dotenv()

pool = oracledb.create_pool(
    user=os.getenv("ORACLE_USER"),
    password=os.getenv("ORACLE_PASSWORD"),
    dsn=os.getenv("ORACLE_DSN"),
    min=2,
    max=10,
    increment=1
)

@tool()
def list_tables(schema: str) -> list[dict]:
    """List all tables in an Oracle schema."""
    results = []
    with pool.acquire() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name 
                FROM all_tables 
                WHERE owner = :schema 
                ORDER BY table_name
            """, schema=schema.upper())
            
            tables = [r[0] for r in cur.fetchall()]
            
            for table in tables:
                cur.execute(f"SELECT COUNT(*) FROM {schema.upper()}.{table}")
                count = cur.fetchone()[0]
                results.append({"table_name": table, "row_count": count})
    
    return results

@tool()
def list_views(schema: str) -> list[dict]:
    """List all views in an Oracle schema."""
    results = []
    with pool.acquire() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT view_name, text 
                FROM all_views 
                WHERE owner = :schema
            """, schema=schema.upper())
            
            views = cur.fetchall()
            
            for view_name, view_ddl in views:
                cur.execute(f"SELECT COUNT(*) FROM {schema.upper()}.{view_name}")
                count = cur.fetchone()[0]
                results.append({"view_name": view_name, "view_ddl": view_ddl, "row_count": count})
    
    return results

@tool()
def list_procedures(owner: str) -> list[dict]:
    """List all stored procedures and functions in an Oracle schema."""
    with pool.acquire() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT object_name, object_type, status, last_ddl_time
            FROM all_objects
            WHERE owner = UPPER(:owner)
            AND object_type IN ('PROCEDURE', 'FUNCTION')
            ORDER BY object_type, object_name
        """, owner=owner)
        return [
            {
                "object_name": r[0],
                "object_type": r[1].lower(),
                "status":      r[2],
                "last_modified": str(r[3])
            }
            for r in cur.fetchall()
        ]

@tool()
def get_table_ddl(table_name: str, schema: str) -> str:
    """Get the full CREATE TABLE DDL for an Oracle table"""
    with pool.acquire() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT DBMS_METADATA.GET_DDL('TABLE', :t, :s) FROM DUAL",
            t=table_name.upper(), s=schema.upper()
        )
        row = cur.fetchone()
        return str(row[0]) if row else f"Table {table_name} not found"
    
@tool()
def get_view_ddl(view_name: str, schema: str) -> str:
    """Get the full CREATE VIEW DDL for an Oracle view"""
    with pool.acquire() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT DBMS_METADATA.GET_DDL('VIEW', :v, :s) FROM DUAL",
            v=view_name.upper(), s=schema.upper()
        )
        row = cur.fetchone()
        return str(row[0]) if row else f"View {view_name} not found"

@tool()
def get_proc_body(proc_name: str, schema: str) -> str:
    """Get the full PL/SQL source body of an Oracle stored procedure or function"""
    with pool.acquire() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT text FROM all_source
            WHERE owner = UPPER(:s) AND name = UPPER(:p)
            ORDER BY line
        """, s=schema, p=proc_name)
        lines = [row[0] for row in cur.fetchall()]
        return "".join(lines) if lines else f"Procedure {proc_name} not found"

@tool()
def get_dependencies(object_name: str, schema: str) -> list[dict]:
    """Get all objects that a given Oracle object depends on using ALL_DEPENDENCIES"""
    with pool.acquire() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT referenced_name, referenced_type, referenced_owner
            FROM all_dependencies
            WHERE owner = UPPER(:s) AND name = UPPER(:n)
        """, s=schema, n=object_name)
        return [
            {"name": r[0], "type": r[1], "owner": r[2]}
            for r in cur.fetchall()
        ]

@tool()
def count_rows(table_name: str, schema: str) -> int:
    """Get exact row count for an Oracle table for reconciliation"""
    with pool.acquire() as conn:
        cur = conn.cursor()
        cur.execute(
            f'SELECT COUNT(*) FROM "{schema.upper()}"."{table_name.upper()}"'
        )
        return cur.fetchone()[0]

@tool()
def sample_rows(table_name: str, schema: str, n: int = 50) -> list[dict]:
    """Sample n rows from an Oracle table for data profiling and validation"""
    with pool.acquire() as conn:
        cur = conn.cursor()
        cur.execute(
            f"""
                SELECT * FROM "{schema.upper()}"."{table_name.upper()}"
                FETCH FIRST {n} ROWS ONLY
            """
        )
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]
