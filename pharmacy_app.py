import tkinter as tk
from tkinter import messagebox, ttk
from ttkthemes import ThemedTk
from datetime import datetime, timedelta
from customer_manager import CustomerManager
from supplier_manager import SupplierManager
from medicine_manager import MedicineManager
from sales_manager import SalesManager
from logintoapp import LoginWindow
from database import Database

class PharmacyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pharmacy Management System")
        self.root.geometry("1400x800")
        self.root.configure(bg="#f0f0f0")

        # Initialize database
        try:
            Database.initialize_pool()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect to database: {str(e)}")
            self.root.destroy()
            return

        # Modern Theme
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Pharmacy Name
        self.pharmacy_name_font = tk.font.Font(family="Helvetica", size=24, weight="bold")
        pharmacy_name = tk.Label(root, text="Pharmacy Management System", 
                               font=self.pharmacy_name_font, fg="#333333", bg="#f0f0f0")
        pharmacy_name.place(relx=0.5, rely=0.02, anchor="center")

        # Dashboard Frame
        self.dashboard_frame = tk.Frame(root, bg="#333333", width=200)
        self.dashboard_frame.pack(side="left", fill="y", padx=10, pady=10)

        # Dashboard Buttons
        buttons = [
            ("Medicine Management", self.show_medicine_management),
            ("Sales and Billing", self.show_sales_and_billing),
            ("Customer Management", self.show_customer_management),
            ("Supplier Management", self.show_supplier_management)
        ]
        
        for text, command in buttons:
            btn = tk.Button(self.dashboard_frame, text=text, command=command,
                         bg="#444444", fg="white", bd=0, 
                         font=("Helvetica", 12), padx=10, pady=10)
            btn.pack(pady=5, fill="x")

        # Main Content Frame
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Initialize all managers
        self.medicine_manager = MedicineManager(self.main_frame)
        self.sales_manager = SalesManager(self.main_frame)
        self.customer_manager = CustomerManager(self.main_frame)
        self.supplier_manager = SupplierManager(self.main_frame)

        # Show default view
        self.show_medicine_management()
        self.check_expiration_alerts()

    def check_expiration_alerts(self):
        """Check for medicines nearing expiration"""
        try:
            today = datetime.now().date()
            alert_date = today + timedelta(days=30)
            query = "SELECT name, expiry_date FROM medicines WHERE expiry_date <= %s"
            expiring_medicines = Database.execute_query(query, (alert_date,), fetch=True)

            if expiring_medicines:
                alert_message = "The following medicines are nearing expiration:\n\n"
                for medicine in expiring_medicines:
                    days_left = (medicine['expiry_date'] - today).days
                    alert_message += f"{medicine['name']} (Expires on: {medicine['expiry_date']}, {days_left} days left)\n"
                messagebox.showwarning("Expiration Alert", alert_message)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to check expiration alerts: {str(e)}")

    def show_medicine_management(self):
        """Show medicine management interface"""
        self.hide_all_frames()
        self.medicine_manager.frame.pack(fill="both", expand=True)

    def show_sales_and_billing(self):
        """Show sales and billing interface"""
        self.hide_all_frames()
        self.sales_manager.frame.pack(fill="both", expand=True)
        self.sales_manager.load_medicine_names()
        self.sales_manager.load_customer_names()

    def show_customer_management(self):
        """Show customer management interface"""
        self.hide_all_frames()
        self.customer_manager.frame.pack(fill="both", expand=True)
        self.customer_manager.load_customers()

    def show_supplier_management(self):
        """Show supplier management interface"""
        self.hide_all_frames()
        self.supplier_manager.frame.pack(fill="both", expand=True)
        self.supplier_manager.load_suppliers()

    def hide_all_frames(self):
        """Hide all content frames"""
        self.medicine_manager.frame.pack_forget()
        self.sales_manager.frame.pack_forget()
        self.customer_manager.frame.pack_forget()
        self.supplier_manager.frame.pack_forget()

if __name__ == "__main__":
    login_window = LoginWindow()
    if login_window.run():
        root = ThemedTk(theme="clam")
        app = PharmacyApp(root)
        root.mainloop()