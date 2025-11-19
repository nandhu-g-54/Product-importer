# app/api/uploads.py
from fastapi import APIRouter, UploadFile, File, HTTPException
import psycopg2
import io

router = APIRouter(prefix="/upload", tags=["Upload"])

@router.post("/")
async def upload_csv(file: UploadFile = File(...)):

    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV file.")

    try:
        # Read CSV content
        content = await file.read()
        csv_text = content.decode("utf-8")

        # Connect to PostgreSQL
        conn = psycopg2.connect(
            dbname="products_db",
            user="postgres",
            password="Nandhu123",
            host="localhost",
            port="5432"
        )
        cur = conn.cursor()

        # STEP 1 — create temp staging table
        cur.execute("""
            CREATE TEMP TABLE staging_products (
                name TEXT,
                sku TEXT,
                description TEXT
            );
        """)

        # STEP 2 — COPY CSV into temp table
        stream = io.StringIO(csv_text)
        next(stream)  # Skip header

        cur.copy_expert("""
            COPY staging_products (name, sku, description)
            FROM STDIN WITH CSV;
        """, stream)

        # STEP 3 — Remove duplicates inside staging
        cur.execute("""
            DELETE FROM staging_products a
            USING staging_products b
            WHERE a.ctid < b.ctid
            AND a.sku = b.sku;
        """)

        # STEP 4 — UPSERT into main products table
        cur.execute("""
            INSERT INTO products (sku, name, description, active)
            SELECT sku, name, description, TRUE
            FROM staging_products
            ON CONFLICT (sku) DO UPDATE SET
                name = EXCLUDED.name,
                description = EXCLUDED.description,
                active = TRUE;
        """)

        conn.commit()
        cur.close()
        conn.close()

        return {
            "status": "success",
            "message": "CSV imported successfully. Duplicates removed."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CSV import failed: {str(e)}")
