from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError

# SQLite DB inside container
DATABASE_URL = "sqlite:///./tasks.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# Create tables — safe for multi-worker environments (swallows "already exists")
def init_db():
    try:
        Base.metadata.create_all(bind=engine)
    except OperationalError as e:
        if "already exists" in str(e).lower():
            pass  # another worker beat us to it — that's fine
        else:
            raise