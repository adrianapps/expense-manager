from view import ExpensesApp
from controller import ExpenseController


def main():
    app = ExpensesApp(ExpenseController())
    app.run()


if __name__ == "__main__":
    main()
