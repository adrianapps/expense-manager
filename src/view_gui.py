from datetime import datetime
from math import exp
import customtkinter
from CTkTable import *

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("green")


class App(customtkinter.CTk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        self.geometry("900x600")

        sidebar_frame = customtkinter.CTkFrame(self, width=150)
        sidebar_frame.pack(side="left", fill="y", padx=10, pady=10)

        add_button = customtkinter.CTkButton(
            sidebar_frame, text="Add", command=self.add_expense
        )
        add_button.pack(pady=10)

        # delete_button = customtkinter.CTkButton(sidebar_frame, text="Delete", command=self.delete_expense)
        # delete_button.pack(pady=10)

        # update_button = customtkinter.CTkButton(sidebar_frame, text="Update", command=self.update_expense)
        # update_button.pack(pady=10)

        # filter_button = customtkinter.CTkButton(sidebar_frame, text="Filter", command=self.filter_expense)
        # filter_button.pack(pady=10)

        self.table_frame = customtkinter.CTkFrame(self)
        self.table_frame.pack(expand=True, fill="both", padx=20, pady=10)

        self.create_table()

    def create_table(self):
        self.expenses = self.controller.get_expenses()
        self.expenses_list = [
            [expense.id, expense.title, expense.price, expense.date] for expense in self.expenses
        ]

        # Clear the current table rows before creating new ones
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        # Create a row for each expense in the list
        for index, expense_data in enumerate(self.expenses_list):
            row_frame = customtkinter.CTkFrame(self.table_frame)
            row_frame.pack(fill="x", pady=5)

            # Add labels to display data in the row
            label_title = customtkinter.CTkLabel(row_frame, text=expense_data[0])  # Id
            label_title.pack(side="left", padx=10)
            label_price = customtkinter.CTkLabel(row_frame, text=expense_data[1])  # Price
            label_price.pack(side="left", padx=10)
            label_date = customtkinter.CTkLabel(row_frame, text=expense_data[2])  # Date
            label_date.pack(side="left", padx=10)
            label_date = customtkinter.CTkLabel(row_frame, text=expense_data[3])  # Date
            label_date.pack(side="left", padx=10)

            # Add Update and Delete buttons
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
        self.date_label = customtkinter.CTkLabel(self, text="Price:")
        self.date_label.pack(pady=5)
        self.date_entry = customtkinter.CTkEntry(self, placeholder_text=today_date)
        self.date_entry.pack(pady=5)

        # Przycisk do zapisania wydatku
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

        self.destroy()
