from sqlmodel import Session,create_engine
from config import SQLITE_URL
engine = create_engine(SQLITE_URL)


def get_session():
    with Session(engine) as session:
        yield session

