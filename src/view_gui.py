from datetime import datetime
import customtkinter
from CTkTable import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("green")


class App(customtkinter.CTk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        self.geometry("900x700")

        sidebar_frame = customtkinter.CTkFrame(self, width=150)
        sidebar_frame.pack(side="left", fill="y", padx=10, pady=10)

        add_button = customtkinter.CTkButton(
            sidebar_frame, text="Add", command=self.add_expense
        )
        add_button.pack(pady=10)

        filter_button = customtkinter.CTkButton(sidebar_frame, text="Filter", command=self.filter_expenses)
        filter_button.pack(pady=10)

        self.table_frame = customtkinter.CTkScrollableFrame(self)
        self.table_frame.pack(expand=True, fill="both", padx=20, pady=10)

        self.create_table()

        self.plot_frame = customtkinter.CTkFrame(self)
        self.plot_frame.pack(expand=True, fill="both", padx=20, pady=10)
        self.create_plot()

    def create_plot(self, expenses=None):
        if expenses is None:
            expenses = self.controller.get_expenses()

        prices = [expense.price for expense in expenses]
        dates = [expense.date for expense in expenses]

        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(8, 6))

        ax.scatter(dates, prices, color="green")

        ax.set_xlabel('Date')
        ax.set_ylabel('Price')
        ax.set_title('Expense Prices Over Time')

        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()

    def create_table(self, expenses=None):
        if expenses is None:
            expenses = self.controller.get_expenses()

        expenses_list = [
            [expense.id, expense.title, expense.price, expense.date] for expense in expenses
        ]

        for widget in self.table_frame.winfo_children():
            widget.destroy()

        for index, expense_data in enumerate(expenses_list):
            row_frame = customtkinter.CTkFrame(self.table_frame)
            row_frame.pack(fill="x", pady=5)

            label_title = customtkinter.CTkLabel(row_frame, text=expense_data[0])  # id
            label_title.pack(side="left", padx=10)
            label_price = customtkinter.CTkLabel(row_frame, text=expense_data[1])  # title 
            label_price.pack(side="left", padx=10)
            label_date = customtkinter.CTkLabel(row_frame, text=expense_data[2])  # price 
            label_date.pack(side="left", padx=10)
            label_date = customtkinter.CTkLabel(row_frame, text=expense_data[3])  # date
            label_date.pack(side="left", padx=10)

            update_button = customtkinter.CTkButton(row_frame, text="Update", command=lambda idx=expense_data[0]: self.update_expense(idx))
            update_button.pack(side="right", padx=5)

            delete_button = customtkinter.CTkButton(row_frame, text="Delete", command=lambda idx=expense_data[0]: self.delete_expense(idx))
            delete_button.pack(side="right", padx=5)

    def add_expense(self):
        AddExpense(self, self.controller)

    def update_expense(self, expense_id):
        expense = self.controller.get_expense_detail(expense_id)
        UpdateExpense(self, self.controller, expense)

    def delete_expense(self, expense_id):
        self.controller.delete_expense(expense_id)
        self.create_table()
        self.create_plot()

    def filter_expenses(self):
        FilterExpenses(self, self.controller)


class AddExpense(customtkinter.CTkToplevel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.geometry("400x300")
        self.title("Add New Expense")

        self.title_label = customtkinter.CTkLabel(self, text="Title:")
        self.title_label.pack(pady=5)
        self.title_entry = customtkinter.CTkEntry(self)
        self.title_entry.pack(pady=5)

        self.price_label = customtkinter.CTkLabel(self, text="Price:")
        self.price_label.pack(pady=5)
        self.price_entry = customtkinter.CTkEntry(self)
        self.price_entry.pack(pady=5)

        today_date = datetime.now().strftime("%Y-%m-%d")
        self.date_label = customtkinter.CTkLabel(self, text="Date:")
        self.date_label.pack(pady=5)
        self.date_entry = customtkinter.CTkEntry(self, placeholder_text=today_date)
        self.date_entry.pack(pady=5)

        self.save_button = customtkinter.CTkButton(
            self, text="Save", command=self.save_expense
        )
        self.save_button.pack(pady=10)

    def save_expense(self):
        title = self.title_entry.get()
        price = self.price_entry.get()
        date = self.date_entry.get()

        self.controller.add_expense(title, price, date)
        self.master.create_table()
        self.master.create_plot()

        self.destroy()


class UpdateExpense(customtkinter.CTkToplevel):
    def __init__(self, parent, controller, expense):
        super().__init__(parent)
        self.controller = controller
        self.expense = expense

        self.geometry("400x300")
        self.title("Update Expense")

        self.title_label = customtkinter.CTkLabel(self, text="Title:")
        self.title_label.pack(pady=5)
        self.title_entry = customtkinter.CTkEntry(self)
        self.title_entry.pack(pady=5)
        self.title_entry.insert(0, expense.title)

        self.price_label = customtkinter.CTkLabel(self, text="Price:")
        self.price_label.pack(pady=5)
        self.price_entry = customtkinter.CTkEntry(self)
        self.price_entry.pack(pady=5)
        self.price_entry.insert(0, expense.price)

        self.date_label = customtkinter.CTkLabel(self, text="Date:")
        self.date_label.pack(pady=5)
        self.date_entry = customtkinter.CTkEntry(self)
        self.date_entry.pack(pady=5)
        self.date_entry.insert(0, expense.date)

        self.save_button = customtkinter.CTkButton(
            self, text="Save", command=self.update_expense
        )
        self.save_button.pack(pady=10)

    def update_expense(self):
        title = self.title_entry.get()
        price = self.price_entry.get()
        date = self.date_entry.get()

        expense_data = {
            "title": title,
            "price": float(price),
            "date": datetime.strptime(date, "%Y-%m-%d")
        }

        self.controller.update_expense(self.expense.id, expense_data)
        self.master.create_table()
        self.master.create_plot()

        self.destroy()


class FilterExpenses(customtkinter.CTkToplevel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.geometry("400x300")
        self.title("Filter Expenses")

        self.title_label = customtkinter.CTkLabel(self, text="Title:")
        self.title_label.pack(pady=5)
        self.title_entry = customtkinter.CTkEntry(self)
        self.title_entry.pack(pady=5)

        price_frame = customtkinter.CTkFrame(self)
        price_frame.pack(pady=5)

        self.min_price_label = customtkinter.CTkLabel(price_frame, text="Min Price:")
        self.min_price_label.grid(row=0, column=0, padx=5, pady=5)
        self.min_price_entry = customtkinter.CTkEntry(price_frame)
        self.min_price_entry.grid(row=1, column=0, padx=5, pady=5)

        self.max_price_label = customtkinter.CTkLabel(price_frame, text="Max Price:")
        self.max_price_label.grid(row=0, column=1, padx=5, pady=5)
        self.max_price_entry = customtkinter.CTkEntry(price_frame)
        self.max_price_entry.grid(row=1, column=1, padx=5, pady=5)

        date_frame = customtkinter.CTkFrame(self)
        date_frame.pack(pady=5)

        self.min_date_label = customtkinter.CTkLabel(date_frame, text="Min Date:")
        self.min_date_label.grid(row=0, column=0, padx=5, pady=5)
        self.min_date_entry = customtkinter.CTkEntry(date_frame)
        self.min_date_entry.grid(row=1, column=0, padx=5, pady=5)

        self.max_date_label = customtkinter.CTkLabel(date_frame, text="Max Date:")
        self.max_date_label.grid(row=0, column=1, padx=5, pady=5)
        self.max_date_entry = customtkinter.CTkEntry(date_frame)
        self.max_date_entry.grid(row=1, column=1, padx=5, pady=5)

        self.save_button = customtkinter.CTkButton(
            self, text="Apply", command=self.apply_filter
        )
        self.save_button.pack(pady=10)

    def apply_filter(self):
        title = self.title_entry.get()
        min_price = self.min_price_entry.get()
        max_price = self.max_price_entry.get()
        min_date = self.min_date_entry.get()
        max_date = self.max_date_entry.get()

        min_price = float(min_price) if min_price else None
        max_price = float(max_price) if max_price else None
        min_date = datetime.strptime(min_date, "%Y-%m-%d") if min_date else None
        max_date = datetime.strptime(max_date, "%Y-%m-%d") if max_date else None

        filtered_query = self.controller.filter_expense(
            title=title,
            min_price=min_price,
            max_price=max_price,
            min_date=min_date,
            max_date=max_date
        )

        self.master.create_table(filtered_query)
        self.master.create_plot(filtered_query)

        self.destroy()
