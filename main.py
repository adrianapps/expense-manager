from src.view import ExpensesApp
from src.controller import ExpenseController


def main():
    app = ExpensesApp(ExpenseController())
    app.run()


if __name__ == "__main__":
    main()
