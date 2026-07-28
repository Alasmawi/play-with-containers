import os

from sqlalchemy import Column, Integer, Numeric, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False)
    number_of_items = Column(Integer, nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)


def get_session_factory():
    db_user = os.environ["BILLING_DB_USER"]
    db_password = os.environ["BILLING_DB_PASSWORD"]
    db_host = os.environ["BILLING_DB_HOST"]
    db_port = os.environ.get("BILLING_DB_PORT", "5432")
    db_name = os.environ["BILLING_DB_NAME"]

    url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)
