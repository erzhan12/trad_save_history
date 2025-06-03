from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from config.settings import DATABASE_URL, ECHO_SQL

# Configure engine with connection pooling
engine = create_async_engine(
    DATABASE_URL,
    echo=ECHO_SQL,
)

# Create sessionmaker
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Create Base class for models
class Base(DeclarativeBase):
    pass


# Function to get a database session
async def get_db():
    async with SessionLocal() as db:
        yield db
