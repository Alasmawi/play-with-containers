import os

from sqlalchemy import URL, Column, Integer, Numeric, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False)
    number_of_items = Column(Integer, nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)


def get_session_factory():
    # URL.create escapes special characters in the password.
    url = URL.create(
        "postgresql",
        username=os.environ["BILLING_DB_USER"],
        password=os.environ["BILLING_DB_PASSWORD"],
        host=os.environ["BILLING_DB_HOST"],
        port=int(os.environ.get("BILLING_DB_PORT", 5432)),
        database=os.environ["BILLING_DB_NAME"],
    )
    engine = create_engine(url, pool_pre_ping=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)
