import csv
from app.db.database import SessionLocal
from app.db.models import Product
from app.celery_app import celery_app

@celery_app.task
def import_csv_task(file_path: str):
    session = SessionLocal()
    inserted = 0
    try:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Check if SKU exists
                existing = session.query(Product).filter(Product.sku == row['sku']).first()
                if existing:
                    continue

                product = Product(
                    sku=row['sku'],
                    name=row['name'],
                    description=row.get('description', ''),
                    price=int(row.get('price') or 0),
                    active=row.get('active', 'True').lower() in ['true', '1', 'yes']
                )
                session.add(product)
                inserted += 1
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
    return {"inserted": inserted}
