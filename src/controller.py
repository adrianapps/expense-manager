from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.model import Expense, Base

DATABASE_URL = "sqlite:///app.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)


class ExpenseController:
    def get_session(self):
        return Session()

    def get_expenses(self):
        with self.get_session() as session:
            expenses = session.query(Expense).all()
            return expenses
    
    def get_expense_detail(self, expense_id):
        with self.get_session() as session:
            expense = session.query(Expense).filter(Expense.id == expense_id).first()
            if expense:
                return expense

    def add_expense(self, title, price, date=None):
        with self.get_session() as session:
            if date == "":
                date = datetime.now().date()
            if isinstance(date, str):
                date = datetime.strptime(date, "%Y-%m-%d").date()
            new_expense = Expense(title=title, price=price, date=date)
            session.add(new_expense)
            session.commit()

    def delete_expense(self, expense_id):
        with self.get_session() as session:
            expense = session.query(Expense).filter(Expense.id == expense_id).first()
            if expense:
                session.delete(expense)
                session.commit()

    def update_expense(self, expense_id, props):
        with self.get_session() as session:
            expense = session.query(Expense).filter(Expense.id == expense_id).first()
            for field, value in props.items():
                setattr(expense, field, value)
            session.commit()

    def filter_expense(self, title=None, min_price=None, max_price=None, min_date=None, max_date=None):
        with self.get_session() as session:
            query = session.query(Expense)

            if title:
                query = query.filter(Expense.title.like(f"%{title}%"))
            if min_price is not None:
                query = query.filter(Expense.price >= min_price)
            if max_price is not None:
                query = query.filter(Expense.price <= max_price)
            if min_date:
                query = query.filter(Expense.date >= min_date)
            if max_date:
                query = query.filter(Expense.date <= max_date)

            return query.all()
