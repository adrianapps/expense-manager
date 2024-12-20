from datetime import datetime
from textual.app import App, on
from textual.containers import Grid, Horizontal, Vertical
from textual.widgets import Footer, Header, DataTable, Label, Button, Static, Input
from textual.screen import Screen
from textual_plotext import PlotextPlot


class ExpensesApp(App):
    CSS_PATH = "../styles.tcss"

    BINDINGS = [
        ("m", "toggle_dark", "Toggle dark mode"),
        ("a", "add", "Add"),
        ("u", "update", "Update"),
        ("f", "filter", "Filter"),
        ("d", "delete", "Delete"),
        ("q", "quit_app", "Quit"),
        ("1", "sort_by_title", "Sort By Title"),
        ("2", "sort_by_price", "Sort By Price"),
        ("3", "sort_by_date", "Sort By Date"),
    ]

    current_sorts = set()

    def __init__(self, controller):
        super().__init__()
        self.controller = controller

    def action_quit_app(self):
        self.exit()

    def compose(self):
        yield Header()
        self.expenses_table = DataTable()
        self.expenses_table.focus()

        self.expenses_table.add_column("Title", key="title")
        self.expenses_table.add_column("Price", key="price")
        self.expenses_table.add_column("Date", key="date")

        self.expenses_table.zebra_stripes = True
        self.expenses_table.cursor_type = "row"

        buttons_panel = Vertical(
            Button("Add", variant="success", id="add"),
            Button("Update", variant="default", id="update"),
            Button("Filter", variant="primary", id="filter"),
            Button("Delete", variant="error", id="delete"),
            Static(classes="separator"),
        )

        yield Horizontal(self.expenses_table, buttons_panel)
        self.expenses_plot = PlotextPlot()
        yield self.expenses_plot
        yield Footer()

    def on_mount(self):
        self.title = "Your Expenses"
        self.sub_title = "Expense Manager Application built with Python"
        self._load_expenses()
        self._load_plot()

    def sort_reverse(self, sort_type):
        reverse = sort_type in self.current_sorts
        if reverse:
            self.current_sorts.remove(sort_type)
        else:
            self.current_sorts.add(sort_type)
        return reverse

    def action_sort_by_title(self):
        table = self.query_one(DataTable)
        table.sort(
            "title",
            key=lambda title: title.lower(),
            reverse=self.sort_reverse("Title"),
        )

    def action_sort_by_price(self):
        table = self.query_one(DataTable)
        table.sort("price", reverse=self.sort_reverse("price"))

    def action_sort_by_date(self):
        table = self.query_one(DataTable)
        table.sort("date", reverse=self.sort_reverse("date"))

    def _load_plot(self, expenses=None):
        if expenses is None:
            expenses = self.controller.get_expenses()

        prices = [expense.price for expense in expenses]
        dates = [expense.date.strftime("%d/%m/%Y") for expense in expenses]

        plt = self.expenses_plot.plt
        plt.clf()
        plt.scatter(dates, prices, marker="o", color="orange")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.title("Expenses chart")

    def _load_expenses(self, expenses=None):
        self.expenses_table.clear()

        if expenses is None:
            expenses = self.controller.get_expenses()
        for expense in expenses:
            self.expenses_table.add_row(
                expense.title, expense.price, expense.date, key=expense.id
            )

    @on(Button.Pressed, "#add")
    def action_add(self):
        self.push_screen(InputDialog(self.controller))

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

    @on(Button.Pressed, "#update")
    def action_update(self):
        expenses = self.query_one(DataTable)
        cell_key = expenses.coordinate_to_cell_key(expenses.cursor_coordinate)
        row_key = cell_key.row_key

        if row_key:
            self.push_screen(UpdateInput(self.controller, row_key.value))
    


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
            Button("Apply", variant="success", id="apply"),
            id="input-dialog",
        )

    @on(Button.Pressed, "#apply")
    def apply(self):
        title = self.query_one("#input_title").value
        min_price = self.query_one("#input_min_price").value
        max_price = self.query_one("#input_max_price").value
        min_date = self.query_one("#input_min_date").value
        max_date = self.query_one("#input_max_date").value

        min_price = float(min_price) if min_price else None
        max_price = float(max_price) if max_price else None

        min_date = datetime.strptime(min_date, "%Y-%m-%d").date() if min_date else None
        max_date = datetime.strptime(max_date, "%Y-%m-%d").date() if max_date else None

        filtered_expenses = self.controller.filter_expense(
            title=title,
            min_price=min_price,
            max_price=max_price,
            min_date=min_date,
            max_date=max_date,
        )

        self.app._load_expenses(filtered_expenses)
        self.app._load_plot(filtered_expenses)
        self.app.pop_screen()

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
            id="confirm-dialog",
        )

    @on(Button.Pressed, "#confirm")
    def delete(self):
        self.controller.delete_expense(expense_id=self.expense_id)
        self.app.pop_screen()
        self.app._load_expenses()
        self.app._load_plot()

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
        self.app._load_expenses()
        self.app._load_plot()
        self.app.pop_screen()

    @on(Button.Pressed, "#cancel")
    def cancel(self):
        self.app.pop_screen()


class UpdateInput(Screen):
    def __init__(self, controller, expense_id):
        super().__init__()
        self.controller = controller
        self.expense_id = expense_id

    def on_mount(self):
        self.expense_data = self.controller.get_expense_detail(self.expense_id)
        self.query_one("#input_title").value = self.expense_data.title
        self.query_one("#input_price").value = str(self.expense_data.price)
        self.query_one("#input_date").value = self.expense_data.date.strftime("%Y-%m-%d")

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

        updated_data = {
            "title": title,
            "price": float(price),
            "date": datetime.strptime(date, "%Y-%m-%d")
        }

        self.controller.update_expense(self.expense_id, updated_data)
        self.app._load_expenses()
        self.app._load_plot()
        self.app.pop_screen()

    @on(Button.Pressed, "#cancel")
    def cancel(self):
        self.app.pop_screen()
