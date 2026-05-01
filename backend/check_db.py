from app.models.incident_sqlite import Incident
from app.db.database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
print("Incident table columns:")
for c in inspector.get_columns('incidents'):
    print(f'  - {c["name"]}')