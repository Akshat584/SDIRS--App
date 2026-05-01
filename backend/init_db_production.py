"""
Production Database Initialization Script

This script initializes the PostgreSQL database for production deployment.
It creates all necessary tables and sets up the database schema.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL not found in environment variables!")
    print("Please set DATABASE_URL in your .env file")
    sys.exit(1)

def init_database():
    """Initialize the database with schema."""
    try:
        print("🔧 Initializing production database...")
        print(f"Database URL: {DATABASE_URL[:50]}...")

        # Create engine
        engine = create_engine(DATABASE_URL)

        # Test connection
        print("📡 Testing database connection...")
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful")

        # Note: In production, you would use Alembic migrations
        # For now, we'll create tables using SQLAlchemy models
        print("\n📊 Creating database schema...")

        # Import models and create tables
        from app.models.sqlalchemy import Base

        # Create all tables
        Base.metadata.create_all(bind=engine)

        # Verify tables were created
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        print(f"\n✅ Tables created successfully:")
        for table in tables:
            print(f"  - {table}")

        # Create indexes for better performance
        print("\n📇 Creating database indexes...")
        with engine.connect() as conn:
            # Example indexes - adjust based on your query patterns
            try:
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_incidents_location ON incidents (latitude, longitude)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_incidents_type ON incidents (incident_type)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_incidents_created_at ON incidents (created_at)"))
                conn.commit()
                print("✅ Indexes created successfully")
            except Exception as e:
                print(f"⚠️  Index creation skipped: {e}")

        print("\n🎉 Database initialization complete!")
        print("\nNext steps:")
        print("  1. Start the backend server")
        print("  2. Run: python -m alembic stamp head  # Mark database as up-to-date")
        print("  3. Deploy the mobile app")

        return True

    except OperationalError as e:
        print(f"\n❌ Database connection failed!")
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Check if PostgreSQL is running")
        print("  2. Verify DATABASE_URL credentials")
        print("  3. Ensure database exists")
        print("  4. Check network connectivity")
        return False

    except Exception as e:
        print(f"\n❌ Database initialization failed!")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)