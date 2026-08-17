from sqlalchemy.ext.asyncio import (create_async_engine, async_sessionmaker)

from app.core.config import settings


url = settings.database_url

engine = create_async_engine(
    url,
    pool_size=5,
    max_overflow=10,
    pool_timeout=60,
    pool_pre_ping=True,
    echo=True)

AsyncSessionFactory = async_sessionmaker(bind=engine)
