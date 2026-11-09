import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import engine, Base, SessionLocal
from . import models  # noqa: F401 ensure models registered
from .routers import auth, clients, products, invoices, dashboard
from .services.auth_service import hash_password

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("billing")

app = FastAPI(title="Billing API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(clients.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")
app.include_router(invoices.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")
    # Seed demo user
    db = SessionLocal()
    try:
        from .models.user import User
        demo_email = "demo@facturacion.com"
        existing = db.query(User).filter(User.email == demo_email).first()
        if not existing:
            user = User(
                email=demo_email,
                hashed_password=hash_password("demo1234"),
                full_name="Usuario Demo",
            )
            db.add(user)
            db.commit()
            logger.info("Seeded demo user: %s / demo1234", demo_email)
    finally:
        db.close()


@app.get("/")
def root():
    return {"status": "ok", "docs": "/docs"}