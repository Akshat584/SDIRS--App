import os
from sqlalchemy import create_engine, text
from app.db.database import Base, SQLALCHEMY_DATABASE_URL
from app.db import schemas
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_database_if_not_exists():
    # Parse connection string
    # postgresql://postgres:postgres@localhost:5432/disaster_db
    base_url = SQLALCHEMY_DATABASE_URL.rsplit('/', 1)[0]
    db_name = SQLALCHEMY_DATABASE_URL.rsplit('/', 1)[1]
    
    # Connect to default 'postgres' database to create the new one
    conn = psycopg2.connect(f"{base_url}/postgres")
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    # Check if DB exists
    cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}'")
    exists = cur.fetchone()
    if not exists:
        print(f"Creating database {db_name}...")
        cur.execute(f"CREATE DATABASE {db_name}")
    else:
        print(f"Database {db_name} already exists.")
    
    cur.close()
    conn.close()

def init_db():
    create_database_if_not_exists()
    
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    # Enable PostGIS extension
    with engine.connect() as conn:
        print("Enabling PostGIS extension...")
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        conn.commit()
    
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")

if __name__ == "__main__":
    try:
        init_db()
    except Exception as e:
        print(f"Error initializing database: {e}")
