import os
from sqlalchemy import create_engine
from app.models.sqlalchemy import Base
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sdirs_dev.sqlite")

def init_db():
    print(f"Initializing SQLite database at {SQLALCHEMY_DATABASE_URL}")

    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

    # Create all tables
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)

    # Verify tables were created
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Tables created: {', '.join(tables)}")
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()