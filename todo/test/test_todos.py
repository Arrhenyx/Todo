from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from routers.todos import get_db
from ..database import Base
from ..main import app

SQLALCHEMY_DATABASE_URI = 'sqlite:///./testdb.db'

engine = create_engine(
    SQLALCHEMY_DATABASE_URI,
    connect_args={"check_same_thread":False},
    poolclass=StaticPool,
)

TestingSessionLocal= sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.creat_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()



app.dependency_overrides[get_db]=override_get_db()
