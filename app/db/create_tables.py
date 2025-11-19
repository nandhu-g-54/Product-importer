# init_db.py
from app.db.database import engine, Base
from app.db.models import Product

Base.metadata.create_all(bind=engine)
print("Tables created successfully!")
