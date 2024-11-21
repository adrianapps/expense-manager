from src.controller import ExpenseController
from src.view_gui import App 


def main():
    expense_controller = ExpenseController()
    app = App(expense_controller)
    app.mainloop()


if __name__ == "__main__":
    main()
