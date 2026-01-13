import ssl
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine
from .config import settings

# 1. Clean the URL and handle Driver Prefixes
# We remove any existing sslmode query parameters because asyncpg handles SSL via connect_args
raw_url = settings.DATABASE_URL.split("?")[0]

if raw_url.startswith("postgres://"):
    async_url = raw_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif raw_url.startswith("postgresql://"):
    async_url = raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)
else:
    async_url = raw_url

# Sync URL (for Table Creation) should not have the +asyncpg driver
sync_url = async_url.replace("+asyncpg", "")

# 2. Setup SSL Context for Neon
# Neon requires SSL. Asyncpg requires this to be an SSLObject or True.
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# --- ASYNC ENGINE (For FastAPI Routes) ---
async_engine = create_async_engine(
    async_url,
    echo=True,
    pool_pre_ping=True,
    connect_args={
        "ssl": ctx  # This replaces the need for ?sslmode=require in the URL
    }
)

# --- SYNC ENGINE (For Table Creation in main.py) ---
sync_engine = create_engine(
    sync_url,
    pool_pre_ping=True
    # Sync engine (psycopg2) handles SSL via the URL if needed, 
    # but for table creation, the basic URL is usually enough.
)

# --- SESSION CONFIGURATION ---
async_session_maker = sessionmaker(
    async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def get_session():
    """Dependency for providing async database sessions to routes."""
    async with async_session_maker() as session:
        yield session