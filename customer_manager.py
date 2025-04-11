import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from database import Customer, Order, Prescription

class CustomerManager:
    def __init__(self, parent_frame):
        self.frame = ttk.Frame(parent_frame)
        self.current_customer = None
        self.setup_ui()

    def setup_ui(self):
        # Search frame
        search_frame = ttk.Frame(self.frame)
        search_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(search_frame, text="Search:").pack(side="left")
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self.search_customers)
        
        # Customer treeview
        self.tree = ttk.Treeview(self.frame, columns=(
            "ID", "Name", "Phone", "Email", "Address", "Age", "Points"
        ), show="headings", selectmode="browse")
        
        columns = [
            ("ID", "ID", 50),
            ("Name", "Name", 150),
            ("Phone", "Phone", 100),
            ("Email", "Email", 150),
            ("Address", "Address", 200),
            ("Age", "Age", 50),
            ("Points", "Loyalty Points", 80)
        ]
        
        for col_id, col_text, width in columns:
            self.tree.heading(col_id, text=col_text)
            self.tree.column(col_id, width=width, anchor="center")
        
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.on_customer_select)
        
        # Button frame
        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        self.add_btn = ttk.Button(btn_frame, text="Add", command=self.show_add_dialog)
        self.edit_btn = ttk.Button(btn_frame, text="Edit", command=self.show_edit_dialog, state="disabled")
        self.delete_btn = ttk.Button(btn_frame, text="Delete", command=self.delete_customer, state="disabled")
        
        self.add_btn.pack(side="left", padx=5)
        self.edit_btn.pack(side="left", padx=5)
        self.delete_btn.pack(side="left", padx=5)
        
        ttk.Button(btn_frame, text="Refresh", command=self.load_customers).pack(side="right", padx=5)
        
        self.load_customers()

    def load_customers(self, search_term=None):
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        try:
            customers = Customer.get_all(search_term)
            for cust in customers:
                self.tree.insert("", "end", values=(
                    cust['customer_id'],
                    cust['name'],
                    cust['phone'] or "N/A",
                    cust['email'] or "N/A",
                    cust['address'] or "N/A",
                    cust['age'] or "N/A",
                    cust['loyalty_points'] or 0
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load customers: {str(e)}")

    def search_customers(self, event=None):
        self.load_customers(self.search_entry.get())

    def on_customer_select(self, event):
        selected = self.tree.selection()
        if selected:
            self.current_customer = self.tree.item(selected[0])['values']
            self.edit_btn.config(state="normal")
            self.delete_btn.config(state="normal")
        else:
            self.current_customer = None
            self.edit_btn.config(state="disabled")
            self.delete_btn.config(state="disabled")

    def show_add_dialog(self):
        dialog = CustomerDialog(self.frame, title="Add New Customer")
        if dialog.result:
            try:
                Customer.create(dialog.result)
                self.load_customers()
                messagebox.showinfo("Success", "Customer added successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add customer: {str(e)}")

    def show_edit_dialog(self):
        if not self.current_customer:
            return
        
        customer_id = self.current_customer[0]
        customer_data = {
            'name': self.current_customer[1],
            'phone': self.current_customer[2],
            'email': self.current_customer[3],
            'address': self.current_customer[4],
            'age': self.current_customer[5],
            'loyalty_points': self.current_customer[6]
        }
        
        dialog = CustomerDialog(self.frame, title="Edit Customer", data=customer_data)
        if dialog.result:
            try:
                Customer.update(customer_id, dialog.result)
                self.load_customers()
                messagebox.showinfo("Success", "Customer updated successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update customer: {str(e)}")

    def delete_customer(self):
        if not self.current_customer:
            return
        
        if messagebox.askyesno("Confirm", "Delete this customer?"):
            try:
                # Delete related rows in dependent tables
                customer_id = self.current_customer[0]
                Order.delete_by_customer_id(customer_id)  # Ensure you have a method to delete orders by customer_id
                Prescription.delete_by_customer_id(customer_id)  # Ensure you have a method to delete prescriptions by customer_id
                
                # Delete the customer
                Customer.delete(customer_id)
                self.load_customers()
                messagebox.showinfo("Success", "Customer deleted successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete customer: {str(e)}")

class CustomerDialog(tk.Toplevel):
    def __init__(self, parent, title, data=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x450")
        self.resizable(False, False)
        self.result = None
        
        self.data = data or {
            'name': '',
            'phone': '',
            'email': '',
            'address': '',
            'age': '',
            'loyalty_points': 0
        }
        
        self.create_widgets()
        self.transient(parent)
        self.grab_set()
        self.wait_window(self)
    
    def create_widgets(self):
        ttk.Label(self, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.name_entry = ttk.Entry(self)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.name_entry.insert(0, self.data['name'])
        
        ttk.Label(self, text="Phone:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.phone_entry = ttk.Entry(self)
        self.phone_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.phone_entry.insert(0, self.data['phone'] or "")
        
        ttk.Label(self, text="Email:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.email_entry = ttk.Entry(self)
        self.email_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.email_entry.insert(0, self.data['email'] or "")
        
        ttk.Label(self, text="Address:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.address_entry = ttk.Entry(self)
        self.address_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        self.address_entry.insert(0, self.data['address'] or "")
        
        ttk.Label(self, text="Age:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.age_entry = ttk.Entry(self)
        self.age_entry.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        self.age_entry.insert(0, str(self.data['age']) if self.data['age'] else "")
        
        ttk.Label(self, text="Loyalty Points:").grid(row=5, column=0, padx=5, pady=5, sticky="e")
        self.points_entry = ttk.Entry(self)
        self.points_entry.grid(row=5, column=1, padx=5, pady=5, sticky="ew")
        self.points_entry.insert(0, str(self.data['loyalty_points']))
        
        button_frame = ttk.Frame(self)
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Save", command=self.on_save).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side="right", padx=5)
    
    def on_save(self):
        try:
            self.result = {
                'name': self.name_entry.get(),
                'phone': self.phone_entry.get() or None,
                'email': self.email_entry.get() or None,
                'address': self.address_entry.get() or None,
                'age': int(self.age_entry.get()) if self.age_entry.get() else None,
                'loyalty_points': int(self.points_entry.get())
            }
            self.destroy()
        except ValueError:
           messagebox.showerror("Error", "Please enter valid numeric values for age and loyalty points")
           
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values for age and loyalty points")
            
            
            if __name__ == "__main__":
                root = tk.Tk()
                root.title("Customer Manager")
                root.geometry("800x600")
                
                app = CustomerManager(root)
                app.frame.pack(fill="both", expand=True)
                
                root.mainloop()
                # Ensure the Order and Prescription classes have the required methods
                # Add the following methods in the respective classes in the `database.py` file:

                class Order:
                    @staticmethod
                    def delete_by_customer_id(customer_id):
                        # Implement the logic to delete orders by customer_id
                        # Example:
                        # db.execute("DELETE FROM orders WHERE customer_id = ?", (customer_id,))
                        pass

                class Prescription:
                    @staticmethod
                    def delete_by_customer_id(customer_id):
                        # Implement the logic to delete prescriptions by customer_id
                        # Example:
                        # db.execute("DELETE FROM prescriptions WHERE customer_id = ?", (customer_id,))
                        pass