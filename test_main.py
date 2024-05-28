from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import pytest

from main import app
from model.database import Base, get_db
from model.core import Timestamp

DATABASE_PATH = "sqlite:///:memory:"

engine = create_engine(DATABASE_PATH, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="module")
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="module")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c


def test_read_timestamps(client, db):
    # Add test data, return it and compare
    new_timestamp = Timestamp(timestamp=datetime(2024, 1, 1, 0, 0, 0))
    db.add(new_timestamp)
    db.commit()
    db.refresh(new_timestamp)

    response = client.get("/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["timestamp"] == "2024-01-01T00:00:00"


def test_delete_all_timestamps(client, db):
    # Add another entry to the database if the previous test fails and the database is empty
    new_timestamp = Timestamp(timestamp=datetime(2024, 1, 1, 0, 0, 0))
    db.add(new_timestamp)
    db.commit()
    db.refresh(new_timestamp)
    # Delete all data and check the answer
    response = client.delete("/")
    assert response.status_code == 200
    assert response.json() == {"message": "All records deleted"}
    # Trying to delete an empty database and checking the answer
    response = client.delete("/")
    assert response.status_code == 200
    assert response.json() == {"message": "No records"}
