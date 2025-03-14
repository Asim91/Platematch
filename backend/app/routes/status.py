from fastapi import APIRouter, HTTPException
import os
import sys
import platform
from typing import Dict, Any
import psycopg2

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