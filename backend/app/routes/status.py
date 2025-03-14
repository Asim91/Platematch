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

@router.post("/create-dummy-data")
async def create_dummy_data():
    """
    Create sample data in the database for testing purposes
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
        
        # Create tables if they don't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS plates (
                id SERIAL PRIMARY KEY,
                registration VARCHAR(255) NOT NULL,
                normalized_registration VARCHAR(255),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS names (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                id SERIAL PRIMARY KEY,
                plate_id INTEGER REFERENCES plates(id),
                name_id INTEGER REFERENCES names(id),
                similarity FLOAT NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Clear existing data
        cursor.execute("TRUNCATE plates, names, matches RESTART IDENTITY CASCADE")
        
        # Insert sample data
        plates_data = [
            ('ABC123', 'ABC123'),
            ('XYZ789', 'XYZ789'),
            ('P14TE', 'PLATE'),
            ('M1KE', 'MIKE'),
            ('JON123', 'JON123'),
            ('SM1TH', 'SMITH'),
            ('W1LL', 'WILL')
        ]
        
        for reg, norm in plates_data:
            cursor.execute(
                "INSERT INTO plates (registration, normalized_registration) VALUES (%s, %s)",
                (reg, norm)
            )
        
        names_data = [
            'John',
            'Mike',
            'Smith',
            'William',
            'Jones',
            'Plate',
            'Richards'
        ]
        
        for name in names_data:
            cursor.execute(
                "INSERT INTO names (name) VALUES (%s)",
                (name,)
            )
        
        # Create some matches
        matches_data = [
            (1, 1, 0.8),  # ABC123 - John
            (3, 6, 0.9),  # P14TE - Plate
            (4, 2, 0.95), # M1KE - Mike
            (6, 3, 0.7),  # SM1TH - Smith
            (7, 4, 0.85)  # W1LL - William
        ]
        
        for plate_id, name_id, similarity in matches_data:
            cursor.execute(
                "INSERT INTO matches (plate_id, name_id, similarity) VALUES (%s, %s, %s)",
                (plate_id, name_id, similarity)
            )
        
        # Commit the transaction
        conn.commit()
        
        # Close connection
        cursor.close()
        conn.close()
        
        return {"message": "Dummy data created successfully"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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