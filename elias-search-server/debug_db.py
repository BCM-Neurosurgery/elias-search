#!/usr/bin/env python
"""
Debug script to test database routing and query issues
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'es_server.settings')
django.setup()

from django.db import connections
from django.conf import settings
from es_server.models import TaskIDComments, TaskComments, Patient

def debug_database_routing():
    """Test database routing for different models"""
    print("=== Database Routing Debug ===\n")
    
    # Check environment variables
    print("1. Environment Variables:")
    print(f"   ENVIRONMENT: {os.environ.get('ENVIRONMENT', 'NOT SET')}")
    print(f"   DJ_HOST: {os.environ.get('DJ_HOST', 'NOT SET')}")
    print(f"   DJ_USER: {os.environ.get('DJ_USER', 'NOT SET')}")
    print(f"   DJ_PASSWORD: {'SET' if os.environ.get('DJ_PASSWORD') else 'NOT SET'}")
    print(f"   DJ_PORT: {os.environ.get('DJ_PORT', 'NOT SET')}")
    
    # Check database configuration
    print("\n2. Database Configuration:")
    print(f"   DATABASES config: {list(settings.DATABASES.keys())}")
    
    # Check which my.cnf file is being used
    db_config_path = str(settings.BASE_DIR / "es_server/my.cnf") if os.environ.get("ENVIRONMENT", "development") == "production" else str(settings.BASE_DIR / "es_server/my.cnf.dev")
    print(f"   Config file path: {db_config_path}")
    print(f"   Config file exists: {os.path.exists(db_config_path)}")
    
    if os.path.exists(db_config_path):
        try:
            with open(db_config_path, 'r') as f:
                config_content = f.read()
                print(f"   Config file content:\n{config_content}")
        except Exception as e:
            print(f"   Error reading config file: {e}")
    
    # Check database connections
    print("\n3. Database Connections:")
    for db_name in connections.databases:
        try:
            with connections[db_name].cursor() as cursor:
                cursor.execute("SELECT 1")
                print(f"   Database '{db_name}': Connected ✓")
                
                # Check current database name for MySQL
                if db_name == 'neural_data':
                    try:
                        cursor.execute("SELECT DATABASE()")
                        current_db = cursor.fetchone()[0]
                        print(f"     Current MySQL database: {current_db}")
                        
                        # Check available databases
                        cursor.execute("SHOW DATABASES")
                        databases = [row[0] for row in cursor.fetchall()]
                        print(f"     Available databases: {databases}")
                    except Exception as e:
                        print(f"     Error checking MySQL info: {e}")
        except Exception as e:
            print(f"   Database '{db_name}': Error - {e}")
    
    # Check which database each model is using
    print("\n4. Testing TaskIDComments routing:")
    try:
        # Test basic count
        count = TaskIDComments.objects.count()
        print(f"   Total TaskIDComments count: {count}")
        
        # Check which database it's using
        db = TaskIDComments.objects.db
        print(f"   Database being used: {db}")
        
        # Test values_list
        task_names = list(TaskIDComments.objects.values_list('task_name', flat=True))
        print(f"   Unique task names count: {len(task_names)}")
        print(f"   First 5 task names: {task_names[:5]}")
        
        # Test raw SQL to see if it's a Django ORM issue
        with connections[db].cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM __task_i_d_comments")
            raw_count = cursor.fetchone()[0]
            print(f"   Raw SQL count: {raw_count}")
            
            cursor.execute("SELECT COUNT(DISTINCT task_name) FROM __task_i_d_comments")
            raw_unique_count = cursor.fetchone()[0]
            print(f"   Raw SQL unique task names: {raw_unique_count}")
            
            # Check table structure
            try:
                cursor.execute("SHOW CREATE TABLE __task_i_d_comments")
                table_info = cursor.fetchone()
                if table_info:
                    print(f"   Table type: {'VIEW' if 'VIEW' in table_info[1] else 'TABLE'}")
                else:
                    print("   No table info available")
            except Exception as e:
                print(f"   Error checking table structure: {e}")
            
    except Exception as e:
        print(f"   Error with TaskIDComments: {e}")
    
    print("\n5. Testing TaskComments routing:")
    try:
        count = TaskComments.objects.count()
        print(f"   Total TaskComments count: {count}")
        db = TaskComments.objects.db
        print(f"   Database being used: {db}")
    except Exception as e:
        print(f"   Error with TaskComments: {e}")
    
    print("\n6. Testing Patient routing:")
    try:
        count = Patient.objects.count()
        print(f"   Total Patient count: {count}")
        db = Patient.objects.db
        print(f"   Database being used: {db}")
    except Exception as e:
        print(f"   Error with Patient: {e}")
    
    print("\n7. Django Settings:")
    print(f"   DEBUG: {getattr(settings, 'DEBUG', 'NOT SET')}")
    print(f"   BASE_DIR: {getattr(settings, 'BASE_DIR', 'NOT SET')}")
    print(f"   DATABASE_ROUTERS: {getattr(settings, 'DATABASE_ROUTERS', 'NOT SET')}")

if __name__ == "__main__":
    debug_database_routing()
