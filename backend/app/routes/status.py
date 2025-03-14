import yaml
import os.path
from fastapi import APIRouter, HTTPException
import os
import sys
import platform
from typing import Dict, Any
import psycopg2
import datetime

router = APIRouter()

@router.get("/status", response_model=Dict[str, Any])
async def get_status():
    """
    Get comprehensive system status including database information.
    """
    status_data = {
        "api": {
            "status": "online",
            "version": "1.0.0",
            "environment": os.getenv("ENV", "development"),
            "python_version": sys.version,
            "platform": platform.platform()
        },
        "database": {
            "connected": False,
            "tables": []
        }
    }
    
    # Check database connection
    try:
        # Get database connection info from environment variables
        db_url = os.getenv("DATABASE_URL", "")
        
        if not db_url:
            status_data["database"]["error"] = "No DATABASE_URL environment variable found"
            return status_data
            
        # Parse the database URL
        # Format: postgresql://username:password@hostname:port/database
        parts = db_url.split("://")[1].split("@")
        credentials = parts[0].split(":")
        hostname_parts = parts[1].split("/")
        
        username = credentials[0]
        password = credentials[1] if len(credentials) > 1 else ""
        
        host_port = hostname_parts[0].split(":")
        host = host_port[0]
        port = int(host_port[1]) if len(host_port) > 1 else 5432
        
        database = hostname_parts[1]
        
        # Connect to the database
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=username,
            password=password
        )
        
        cursor = conn.cursor()
        
        # Get table information
        cursor.execute("""
            SELECT 
                table_name
            FROM 
                information_schema.tables
            WHERE 
                table_schema='public' AND table_type='BASE TABLE'
        """)
        
        tables = cursor.fetchall()
        status_data["database"]["connected"] = True
        
        # Get record counts for each table
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM \"{table_name}\"")
            count = cursor.fetchone()[0]
            
            # Get column count
            cursor.execute(f"SELECT COUNT(*) FROM information_schema.columns WHERE table_name='{table_name}'")
            column_count = cursor.fetchone()[0]
            
            # Check for primary key
            cursor.execute(f"SELECT COUNT(*) FROM information_schema.table_constraints WHERE table_name='{table_name}' AND constraint_type='PRIMARY KEY'")
            has_pk = cursor.fetchone()[0] > 0
            
            status_data["database"]["tables"].append({
                "name": table_name,
                "record_count": count,
                "column_count": column_count,
                "has_primary_key": has_pk
            })
            
        cursor.close()
        conn.close()
            
    except Exception as e:
        status_data["database"]["error"] = str(e)
    
    return status_data

# Update the file path discovery functions

def find_schema_file():
    """Find the schema file by trying multiple locations"""
    possible_paths = [
        # Docker container paths
        "/app/shared/db_schema.yaml",
        # Local development paths
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                   'shared', 'db_schema.yaml'),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                   'shared', 'db_schema.yaml')
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

def find_init_sql():
    """Find the init.sql file by trying multiple locations"""
    possible_paths = [
        # Docker container paths
        "/app/shared/init.sql",
        # Local development paths
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                   'shared', 'init.sql'),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                   'shared', 'init.sql')
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

@router.post("/initialize-database")
async def initialize_database():
    """
    Initialize database tables based on schema definition
    """
    try:
        # Get database connection info from environment variables
        db_url = os.getenv("DATABASE_URL", "")
        
        if not db_url:
            raise HTTPException(status_code=500, detail="No DATABASE_URL environment variable found")
        
        print(f"Database URL: {db_url}")
        
        # Parse the database URL
        try:
            parts = db_url.split("://")[1].split("@")
            credentials = parts[0].split(":")
            hostname_parts = parts[1].split("/")
            
            username = credentials[0]
            password = credentials[1] if len(credentials) > 1 else ""
            
            host_port = hostname_parts[0].split(":")
            host = host_port[0]
            port = int(host_port[1]) if len(host_port) > 1 else 5432
            
            database = hostname_parts[1]
            
            print(f"Connecting to database: {host}:{port}/{database} as {username}")
        except Exception as parse_error:
            raise HTTPException(status_code=500, detail=f"Failed to parse database URL: {str(parse_error)}")
        
        # Connect to the database
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=username,
                password=password
            )
            print("Database connection successful")
        except Exception as conn_error:
            raise HTTPException(status_code=500, detail=f"Database connection failed: {str(conn_error)}")
        
        cursor = conn.cursor()
        tables_created = []
        tables_skipped = []
        
        # Find schema file
        schema_path = find_schema_file()
        print(f"Schema file path: {schema_path}")
        
        # Use schema if found
        if schema_path:
            try:
                with open(schema_path, 'r') as file:
                    schema_content = file.read()
                    print(f"Schema content read: {len(schema_content)} bytes")
                    schema = yaml.safe_load(schema_content)
                    print(f"YAML parsed: {schema is not None}")
            except Exception as yaml_error:
                print(f"Error loading YAML: {str(yaml_error)}")
                raise HTTPException(status_code=500, detail=f"Failed to load YAML schema: {str(yaml_error)}")
            
            # Check which tables already exist
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema='public' AND table_type='BASE TABLE'
            """)
            existing_tables = [row[0] for row in cursor.fetchall()]
            print(f"Existing tables: {existing_tables}")
            
            # Create tables based on schema
            if 'tables' not in schema:
                print(f"Invalid schema format: 'tables' key not found. Schema keys: {list(schema.keys())}")
                raise HTTPException(status_code=500, detail="Invalid schema format: 'tables' key not found")
            
            for table_name, columns in schema.get('tables', {}).items():
                # Skip if table already exists
                if table_name.lower() in [t.lower() for t in existing_tables]:
                    tables_skipped.append(table_name)
                    print(f"Skipping existing table: {table_name}")
                    continue
                
                try:
                    print(f"Creating table: {table_name}")
                    columns_sql = []
                    for column_name, column_def in columns.items():
                        columns_sql.append(f'"{column_name}" {column_def}')
                    
                    sql = f'''
                        CREATE TABLE IF NOT EXISTS "{table_name}" (
                            {', '.join(columns_sql)}
                        )
                    '''
                    cursor.execute(sql)
                    tables_created.append(table_name)
                    print(f"Table {table_name} created successfully")
                except Exception as table_error:
                    print(f"Error creating table {table_name}: {str(table_error)}")
                    raise HTTPException(status_code=500, detail=f"Error creating table {table_name}: {str(table_error)}")
        else:
            # Try to use init.sql as fallback
            print("Schema file not found, looking for init.sql")
            init_sql_path = find_init_sql()
            print(f"Init SQL path: {init_sql_path}")
            
            if init_sql_path:
                try:
                    with open(init_sql_path, 'r') as file:
                        init_sql = file.read()
                        print(f"Read SQL file: {len(init_sql)} bytes")
                    
                    # Execute the SQL file with better error handling
                    try:
                        cursor.execute(init_sql)
                        tables_created.append("Tables from init.sql")
                        print("Tables created from init.sql")
                    except Exception as exec_error:
                        print(f"Error executing SQL: {str(exec_error)}")
                        raise HTTPException(status_code=500, detail=f"Failed to execute init.sql: {str(exec_error)}")
                    
                except Exception as read_error:
                    print(f"Error reading SQL file: {str(read_error)}")
                    raise HTTPException(status_code=500, detail=f"Failed to read init.sql: {str(read_error)}")
            else:
                # Use fallback schema
                print("No schema or init.sql found, using basic schema")
                basic_schema = {
                    "tables": {
                        "plates": {
                            "id": "SERIAL PRIMARY KEY",
                            "registration": "VARCHAR(255) NOT NULL",
                            "normalized_registration": "VARCHAR(255)",
                            "created_at": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"
                        },
                        "names": {
                            "id": "SERIAL PRIMARY KEY",
                            "name": "VARCHAR(255) NOT NULL",
                            "created_at": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"
                        },
                        "matches": {
                            "id": "SERIAL PRIMARY KEY",
                            "plate_id": "INTEGER REFERENCES plates(id)",
                            "name_id": "INTEGER REFERENCES names(id)",
                            "similarity": "FLOAT NOT NULL",
                            "created_at": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"
                        }
                    }
                }
                
                # Create tables from basic schema
                for table_name, columns in basic_schema.get('tables', {}).items():
                    # Skip if table already exists
                    if table_name.lower() in [t.lower() for t in existing_tables]:
                        tables_skipped.append(table_name)
                        print(f"Skipping existing table: {table_name}")
                        continue
                    
                    try:
                        print(f"Creating table from basic schema: {table_name}")
                        columns_sql = []
                        for column_name, column_def in columns.items():
                            columns_sql.append(f'"{column_name}" {column_def}')
                        
                        sql = f'''
                            CREATE TABLE IF NOT EXISTS "{table_name}" (
                                {', '.join(columns_sql)}
                            )
                        '''
                        cursor.execute(sql)
                        tables_created.append(table_name)
                        print(f"Table {table_name} created successfully")
                    except Exception as table_error:
                        print(f"Error creating table {table_name}: {str(table_error)}")
                        raise HTTPException(status_code=500, detail=f"Error creating table {table_name}: {str(table_error)}")
        
        # Commit the transaction
        conn.commit()
        print("Transaction committed")
        
        # Close connection
        cursor.close()
        conn.close()
        
        return {
            "message": "Database initialized successfully",
            "tables_created": tables_created,
            "tables_skipped": tables_skipped
        }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-dummy-data")
async def create_dummy_data():
    """
    Legacy endpoint - redirects to initialize-database
    """
    return await initialize_database()

@router.get("/table-data/{table_name}")
async def get_table_data(table_name: str):
    """
    Get data from a specific table
    """
    try:
        # Get database connection info from environment variables
        db_url = os.getenv("DATABASE_URL", "")
        
        if not db_url:
            raise HTTPException(status_code=500, detail="No DATABASE_URL environment variable found")
            
        # Parse the database URL
        parts = db_url.split("://")[1].split("@")
        credentials = parts[0].split(":")
        hostname_parts = parts[1].split("/")
        
        username = credentials[0]
        password = credentials[1] if len(credentials) > 1 else ""
        
        host_port = hostname_parts[0].split(":")
        host = host_port[0]
        port = int(host_port[1]) if len(host_port) > 1 else 5432
        
        database = hostname_parts[1]
        
        # Connect to the database
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=username,
            password=password
        )
        
        cursor = conn.cursor()
        
        # Validate the table name to prevent SQL injection
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema='public' AND table_type='BASE TABLE'
        """)
        
        valid_tables = [row[0] for row in cursor.fetchall()]
        
        if table_name not in valid_tables:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
        
        # Get the column names
        cursor.execute(f"""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema='public' AND table_name='{table_name}'
            ORDER BY ordinal_position
        """)
        
        columns = [row[0] for row in cursor.fetchall()]
        
        # Get the data (limit to 100 rows for safety)
        cursor.execute(f'SELECT * FROM "{table_name}" LIMIT 100')
        rows = cursor.fetchall()
        
        # Convert data to JSON serializable format
        serializable_rows = []
        for row in rows:
            serializable_row = []
            for item in row:
                if isinstance(item, (datetime.date, datetime.datetime)):
                    serializable_row.append(item.isoformat())
                else:
                    serializable_row.append(item)
            serializable_rows.append(serializable_row)
        
        # Close connection
        cursor.close()
        conn.close()
        
        return {
            "columns": columns,
            "rows": serializable_rows
        }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))