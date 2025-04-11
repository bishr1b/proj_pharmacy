import tkinter as tk
from tkinter import ttk, messagebox
from medicine_manager import MedicineManager
from supplier_manager import SupplierManager
from customer_manager import CustomerManager
from order_manager import OrderManager
from prescription_manager import PrescriptionManager
from employee_manager import EmployeeManager
from database import Database
from logintoapp import LoginWindow  # Import the LoginWindow class

class PharmacyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pharmacy Management System")
        self.root.geometry("1200x800")
        
        # Initialize database
        try:
            Database.initialize_pool()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            self.root.destroy()
            return
        
        # Main container
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar
        self.create_sidebar()
        
        # Content area
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Initialize managers
        self.managers = {
            "medicines": MedicineManager(self.content_frame),
            "suppliers": SupplierManager(self.content_frame),
            "customers": CustomerManager(self.content_frame),
            "orders": OrderManager(self.content_frame),
            "prescriptions": PrescriptionManager(self.content_frame),
            "employees": EmployeeManager(self.content_frame)
        }
        
        # Show default view
        self.show_manager("medicines")

    def create_sidebar(self):
        """Create navigation sidebar"""
        sidebar = ttk.Frame(self.main_frame, width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        buttons = [
            ("Medicines", "medicines"),
            ("Suppliers", "suppliers"),
            ("Customers", "customers"),
            ("Orders", "orders"),
            ("Prescriptions", "prescriptions"),
            ("Employees", "employees")
        ]
        
        for text, manager in buttons:
            ttk.Button(
                sidebar, 
                text=text, 
                command=lambda m=manager: self.show_manager(m),
                width=20
            ).pack(pady=2, fill=tk.X)
        
        ttk.Button(
            sidebar, 
            text="Exit", 
            command=self.root.quit
        ).pack(side=tk.BOTTOM, pady=5, fill=tk.X)

    def show_manager(self, manager_name):
        """Show selected manager view"""
        for widget in self.content_frame.winfo_children():
            widget.pack_forget()
        
        if manager_name in self.managers:
            self.managers[manager_name].frame.pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    # First show the login window
    login_window = LoginWindow()
    if login_window.run():  # This will return True only if login is successful
        # If login is successful, show the main application
        root = tk.Tk()
        app = PharmacyApp(root)
        root.mainloop()
        
    