import os
import sys
from sqlalchemy import create_engine, text
from app.db.database import Base, SQLALCHEMY_DATABASE_URL, SessionLocal
from app.models.sqlalchemy import User, Resource, SafeZone, Incident
from passlib.hash import sha256_crypt
from dotenv import load_dotenv

load_dotenv()

def init_db():
    print(f"Initializing database with URL: {SQLALCHEMY_DATABASE_URL}")

    engine = create_engine(SQLALCHEMY_DATABASE_URL)

    # Create all tables
    print("Creating tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully!")

        # Seed initial data
        seed_data()
        print("Database initialized and seeded successfully!")

    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)

def seed_data():
    db = SessionLocal()
    try:
        # 1. Create Admin User
        from app.core.config import settings
        admin_email = settings.admin_email
        admin_password = settings.admin_password
        
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        if not existing_admin:
            print(f"Seeding admin user: {admin_email}...")
            admin_user = User(
                name="SDIRS Admin",
                email=admin_email,
                hashed_password=sha256_crypt.hash(admin_password),
                role="admin",
                status="active"
            )
            db.add(admin_user)
        else:
            print("Admin user already exists.")

        # 2. Create Sample Resources
        if db.query(Resource).count() == 0:
            print("Seeding sample resources...")
            resources = [
                Resource(name="Ambulance Alpha", resource_type="ambulance", status="available", latitude=26.8467, longitude=80.9462),
                Resource(name="Fire Truck 01", resource_type="fire_truck", status="available", latitude=26.8500, longitude=80.9500),
                Resource(name="Police Patrol 10", resource_type="police_car", status="available", latitude=26.8400, longitude=80.9400),
                Resource(name="Rescue Drone A1", resource_type="drone", status="available", latitude=26.8600, longitude=80.9600),
            ]
            db.add_all(resources)
        else:
            print("Resources already exist.")

        # 3. Create Sample Safe Zones
        if db.query(SafeZone).count() == 0:
            print("Seeding sample safe zones...")
            safe_zones = [
                SafeZone(name="Central Emergency Shelter", latitude=26.8588, longitude=80.9200, capacity=500),
                SafeZone(name="West Community Hall", latitude=26.8300, longitude=80.9000, capacity=200),
                SafeZone(name="North High School Safe Zone", latitude=26.8800, longitude=80.9500, capacity=300),
            ]
            db.add_all(safe_zones)
        else:
            print("Safe zones already exist.")

        db.commit()
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
