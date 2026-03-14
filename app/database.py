"""Database connection and session management"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from app.config import settings

# Determine if using SQLite (in-memory or file-based)
is_sqlite = settings.DATABASE_URL.startswith("sqlite")

# Create engine with appropriate configuration
engine_kwargs = {
    "echo": settings.DEBUG,
    "pool_pre_ping": True,  # Verify connections before using
}

if is_sqlite:
    # SQLite-specific configuration
    engine_kwargs.update({
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    })
    engine = create_engine(settings.DATABASE_URL, **engine_kwargs)
    
    # Enable foreign keys for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
else:
    # PostgreSQL configuration
    engine_kwargs.update({
        "pool_size": 10,
        "max_overflow": 20,
    })
    engine = create_engine(settings.DATABASE_URL, **engine_kwargs)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base class for all models
Base = declarative_base()


def get_db():
    """Dependency function to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(bind=engine)
