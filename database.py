from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from config import SQLITE_URL

# Create an asynchronous engine
engine = create_async_engine(SQLITE_URL, echo=True)

# Create an asynchronous session factory
async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
