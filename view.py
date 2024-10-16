from textual.app import App, on
from textual.containers import Grid, Horizontal, Vertical
from textual.widgets import Footer, Header, DataTable, Label, Button, Static, Input
from textual.screen import Screen


class ExpensesApp(App):
    BINDINGS = [
        ("m", "toggle_dark", "Toggle dark mode"),
        ("a", "add", "Add"),
        ("d", "delete", "Delete"),
        ("q", "quit_app", "Quit"),
    ]

    def __init__(self, controller):
        super().__init__()
        self.controller = controller

    def action_quit_app(self):
        self.exit()

    def compose(self):
        yield Header()
        expenses = DataTable()
        expenses.focus()
        expenses.add_columns("Title", "Price", "Date")
        expenses.zebra_stripes = True
        expenses.cursor_type = "row"

        buttons_panel = Vertical(
            Button("Add", variant="success", id="add"),
            Button("Delete", variant="error", id="delete"),
            Static(classes="separator"),
        )

        yield Horizontal(expenses, buttons_panel)
        yield Footer()

    def on_mount(self):
        self.title = "Your Expenses"
        self.sub_title = "Expense Manager Application built with Python"
        self._load_expenses()

    def _load_expenses(self):
        expenses = self.query_one(DataTable)
        expenses.clear()
        for expense in self.controller.get_expenses():
            expenses.add_row(expense.title, expense.price, expense.date, key=expense.id)

    @on(Button.Pressed, "#add")
    def action_add(self):
        self.push_screen(InputDialog(self.controller))

    def _add_expense(self, title, price, date):
        self.controller.add_expense(title, price, date)

    @on(Button.Pressed, "#delete")
    def action_delete(self):
        expenses = self.query_one(DataTable)
        cell_key = expenses.coordinate_to_cell_key(expenses.cursor_coordinate)
        row_key = cell_key.row_key

        if row_key:
            self.push_screen(DeleteConfirm(self.controller, row_key.value))


class DeleteConfirm(Screen):
    def __init__(self, controller, expense_id):
        super().__init__()
        self.controller = controller
        self.expense_id = expense_id 

    def compose(self):
        yield Grid(
            Label("Confirm Deletion"),
            Label("Are you sure you want to delete this expense?"),
            Button("Cancel", variant="error", id="cancel"),
            Button("Delete", variant="success", id="confirm"),
        )
    
    @on(Button.Pressed, "#confirm")
    def delete(self):
        self.controller.delete_expense(expense_id=self.expense_id)
        self.app.pop_screen()
        self.app._load_expenses()

    @on(Button.Pressed, "#cancel")
    def cancel(self):
        self.app.pop_screen()


class InputDialog(Screen):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

    def compose(self):
        yield Grid(
            Label("Add Expense"),
            Label("Title:"),
            Input(
                placeholder="Expense Title",
                id="input_title",
            ),
            Label("Price:"),
            Input(
                placeholder="Expense Price",
                id="input_price",
            ),
            Label("Date: "),
            Input(
                placeholder="Expense Date",
                id="input_date",
            ),
            Static(),
            Button("Cancel", variant="error", id="cancel"),
            Button("Ok", variant="success", id="ok"),
            id="input-dialog",
        )

    @on(Button.Pressed, "#ok")
    def submit(self):
        title = self.query_one("#input_title").value
        price = self.query_one("#input_price").value
        date = self.query_one("#input_date").value
        self.controller.add_expense(title, price, date)
        self.app.pop_screen()

    @on(Button.Pressed, "#cancel")
    def cancel(self):
        self.app.pop_screen()
