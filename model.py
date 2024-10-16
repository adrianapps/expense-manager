from datetime import date
from sqlalchemy import Column, Float, Integer, String, Date
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Expense(Base):
    __tablename__ = "expense"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    date = Column(Date, default=date.today, nullable=False)

    def __repr__(self):
        return f"Expense(item={self.title}, price={self.price}, date={self.date})"
