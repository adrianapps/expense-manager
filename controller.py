from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from model import Expense, Base

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

    def add_expense(self, title, price, date=None):
        with self.get_session() as session:
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
