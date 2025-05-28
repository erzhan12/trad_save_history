from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import QueuePool
from config.settings import DATABASE_URL, ECHO_SQL

# Configure engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    echo=ECHO_SQL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,  # Recycle connections after 30 minutes
)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Create Base class for models
class Base(DeclarativeBase):
    pass


# Function to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
