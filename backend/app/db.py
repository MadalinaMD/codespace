"""Conexiunea la baza de date prin SQLAlchemy 2.0 (SQLite)."""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app import config

# check_same_thread=False: FastAPI poate servi cereri din thread-uri diferite;
# fiecare cerere primește propria sesiune, deci accesul rămâne sigur.
engine = create_engine(
    config.DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)


@event.listens_for(engine, "connect")
def _activeaza_foreign_keys(dbapi_connection, connection_record):
    """SQLite nu impune cheile străine implicit — le activăm la fiecare conexiune."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.close()


SesiuneLocala = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Baza(DeclarativeBase):
    """Clasa de bază pentru toate modelele ORM."""
