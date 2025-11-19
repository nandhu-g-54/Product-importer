from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.products import router as products_router
from app.api.uploads import router as uploads_router
from app.api.webhooks import router as webhooks_router

app = FastAPI(title="Product Importer API")

# CORS setup
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(products_router, prefix="/products")
app.include_router(uploads_router, prefix="/upload")
app.include_router(webhooks_router, prefix="/webhooks")

# Root endpoint
@app.get("/")
def root():
    return {"message": "Product Importer API Running"}
