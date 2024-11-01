from datetime import datetime
from textual.app import App, on
from textual.containers import Grid, Horizontal, Vertical
from textual.widgets import Footer, Header, DataTable, Label, Button, Static, Input
from textual.screen import Screen
from textual_plotext import PlotextPlot


class ExpensesApp(App):
    CSS_PATH = "styles.tcss"

    BINDINGS = [
        ("m", "toggle_dark", "Toggle dark mode"),
        ("a", "add", "Add"),
        ("f", "filter", "Filter"),
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
            Button("Filter", variant="primary", id="filter"),
            Button("Delete", variant="error", id="delete"),
            Static(classes="separator"),
        )

        yield Horizontal(expenses, buttons_panel)
        yield PlotextPlot() 
        yield Footer()

    def on_mount(self):
        self.title = "Your Expenses"
        self.sub_title = "Expense Manager Application built with Python"
        self._load_expenses()

        expenses = self.controller.get_expenses()

        prices = [expense.price for expense in expenses]
        dates = [expense.date.strftime("%d/%m/%Y") for expense in expenses]


        plt = self.query_one(PlotextPlot).plt
        plt.scatter(dates, prices, marker="o", color="orange")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.title("Expenses chart") 


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

    @on(Button.Pressed, "#filter")
    def action_filter(self):
        self.push_screen(Filter(self.controller))


class Filter(Screen):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

    def compose(self):
        yield Grid(
            Label("Filter Expenses", id="title"),
            Label("Title"),
            Input(
                placeholder="Expense Title",
                classes="input",
                id="input_title",
            ),
            Label("Price:"),
            Input(
                placeholder="Min Price",
                classes="input",
                id="input_min_price",
            ),
            Input(
                placeholder="Max Price",
                classes="input",
                id="input_max_price",
            ),
            Label("Date: "),
            Input(
                placeholder="Min Date",
                classes="input",
                id="input_min_date",
            ),
            Input(
                placeholder="Max Date",
                classes="input",
                id="input_max_date",
            ),
            Static(),
            Button("Cancel", variant="error", id="cancel"),
            Button("Ok", variant="success", id="ok"),
            id="input-dialog",
        )

    @on(Button.Pressed, "#cancel")
    def cancel(self):
        self.app.pop_screen()


class DeleteConfirm(Screen):
    def __init__(self, controller, expense_id):
        super().__init__()
        self.controller = controller
        self.expense_id = expense_id

    def compose(self):
        yield Grid(
            Label("Confirm Deletion", id="title"),
            Label("Are you sure you want to delete this expense?", id="confirmation"),
            Static(),
            Button("Cancel", variant="error", id="cancel"),
            Button("Delete", variant="success", id="confirm"),
            id="confirm-dialog"
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
        today_date = datetime.now().strftime("%Y-%m-%d")

        yield Grid(
            Label("Add Expense", id="title"),
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
                placeholder=today_date,
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
