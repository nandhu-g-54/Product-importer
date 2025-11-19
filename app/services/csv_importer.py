# app/services/csv_importer.py
import csv
from fastapi import UploadFile
from app.db.database import SessionLocal
from app.db.models import Product

def import_csv_service(file: UploadFile):
    db = SessionLocal()
    try:
        content = file.file.read().decode("utf-8").splitlines()
        reader = csv.DictReader(content)

        if "sku" not in reader.fieldnames or "name" not in reader.fieldnames:
            return {"status": "error", "detail": "CSV must have 'sku' and 'name' columns"}

        for row in reader:
            sku = row["sku"].strip().lower()
            existing = db.query(Product).filter(Product.sku == sku).first()
            if existing:
                existing.name = row["name"]
                existing.description = row.get("description", "")
            else:
                db.add(Product(
                    sku=sku,
                    name=row["name"],
                    description=row.get("description", ""),
                    active=True
                ))
        db.commit()
        return {"status": "completed"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "detail": str(e)}
    finally:
        db.close()
