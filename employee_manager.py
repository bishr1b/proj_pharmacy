import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from database import Employee

class EmployeeManager:
    def __init__(self, parent_frame):
        self.frame = ttk.Frame(parent_frame)
        self.current_employee = None
        self.setup_ui()

    def setup_ui(self):
        # Search frame
        search_frame = ttk.Frame(self.frame)
        search_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(search_frame, text="Search:").pack(side="left")
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self.search_employees)
        
        # Employee treeview
        self.tree = ttk.Treeview(self.frame, columns=(
            "ID", "Name", "Role", "Phone", "Email", "Salary", "Hire Date"
        ), show="headings", selectmode="browse")
        
        columns = [
            ("ID", "ID", 50),
            ("Name", "Name", 150),
            ("Role", "Role", 100),
            ("Phone", "Phone", 100),
            ("Email", "Email", 150),
            ("Salary", "Salary", 100),
            ("Hire Date", "Hire Date", 100)
        ]
        
        for col_id, col_text, width in columns:
            self.tree.heading(col_id, text=col_text)
            self.tree.column(col_id, width=width, anchor="center")
        
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.on_employee_select)
        
        # Button frame
        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        self.add_btn = ttk.Button(btn_frame, text="Add", command=self.show_add_dialog)
        self.edit_btn = ttk.Button(btn_frame, text="Edit", command=self.show_edit_dialog, state="disabled")
        self.delete_btn = ttk.Button(btn_frame, text="Delete", command=self.delete_employee, state="disabled")
        
        self.add_btn.pack(side="left", padx=5)
        self.edit_btn.pack(side="left", padx=5)
        self.delete_btn.pack(side="left", padx=5)
        
        ttk.Button(btn_frame, text="Refresh", command=self.load_employees).pack(side="right", padx=5)
        
        self.load_employees()

    def load_employees(self, search_term=None):
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        try:
            employees = Employee.get_all(search_term)
            for emp in employees:
                self.tree.insert("", "end", values=(
                    emp['employee_id'],
                    emp['name'],
                    emp['role'] or "N/A",
                    emp['phone'] or "N/A",
                    emp['email'] or "N/A",
                    f"${emp['salary']:.2f}" if emp['salary'] else "N/A",
                    emp['hire_date'].strftime("%Y-%m-%d") if emp['hire_date'] else "N/A"
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load employees: {str(e)}")

    def search_employees(self, event=None):
        self.load_employees(self.search_entry.get())

    def on_employee_select(self, event):
        selected = self.tree.selection()
        if selected:
            self.current_employee = self.tree.item(selected[0])['values']
            self.edit_btn.config(state="normal")
            self.delete_btn.config(state="normal")
        else:
            self.current_employee = None
            self.edit_btn.config(state="disabled")
            self.delete_btn.config(state="disabled")

    def show_add_dialog(self):
        dialog = EmployeeDialog(self.frame, title="Add New Employee")
        if dialog.result:
            try:
                Employee.create(dialog.result)
                self.load_employees()
                messagebox.showinfo("Success", "Employee added successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add employee: {str(e)}")

    def show_edit_dialog(self):
        if not self.current_employee:
            return
        
        employee_id = self.current_employee[0]
        employee_data = {
            'name': self.current_employee[1],
            'role': self.current_employee[2],
            'phone': self.current_employee[3],
            'email': self.current_employee[4],
            'salary': float(self.current_employee[5][1:]) if self.current_employee[5] != "N/A" else None,
            'hire_date': self.current_employee[6]
        }
        
        dialog = EmployeeDialog(self.frame, title="Edit Employee", data=employee_data)
        if dialog.result:
            try:
                Employee.update(employee_id, dialog.result)
                self.load_employees()
                messagebox.showinfo("Success", "Employee updated successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update employee: {str(e)}")

    def delete_employee(self):
        if not self.current_employee:
            return
        
        if messagebox.askyesno("Confirm", "Delete this employee?"):
            try:
                Employee.delete(self.current_employee[0])
                self.load_employees()
                messagebox.showinfo("Success", "Employee deleted successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete employee: {str(e)}")

class EmployeeDialog(tk.Toplevel):
    def __init__(self, parent, title, data=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x450")
        self.resizable(False, False)
        self.result = None
        
        self.data = data or {
            'name': '',
            'role': '',
            'phone': '',
            'email': '',
            'salary': '',
            'hire_date': ''
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
        
        ttk.Label(self, text="Role:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.role_combo = ttk.Combobox(self, values=[
            "Pharmacist", "Technician", "Cashier", "Manager", "Admin"
        ])
        self.role_combo.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.role_combo.set(self.data['role'] or "")
        
        ttk.Label(self, text="Phone:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.phone_entry = ttk.Entry(self)
        self.phone_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.phone_entry.insert(0, self.data['phone'] or "")
        
        ttk.Label(self, text="Email:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.email_entry = ttk.Entry(self)
        self.email_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        self.email_entry.insert(0, self.data['email'] or "")
        
        ttk.Label(self, text="Salary:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.salary_entry = ttk.Entry(self)
        self.salary_entry.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        self.salary_entry.insert(0, str(self.data['salary']) if self.data['salary'] else "")
        
        ttk.Label(self, text="Hire Date (YYYY-MM-DD):").grid(row=5, column=0, padx=5, pady=5, sticky="e")
        self.hire_entry = ttk.Entry(self)
        self.hire_entry.grid(row=5, column=1, padx=5, pady=5, sticky="ew")
        self.hire_entry.insert(0, self.data['hire_date'] or "")
        
        button_frame = ttk.Frame(self)
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Save", command=self.on_save).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side="right", padx=5)
    
    def on_save(self):
        try:
            self.result = {
                'name': self.name_entry.get(),
                'role': self.role_combo.get() or None,
                'phone': self.phone_entry.get() or None,
                'email': self.email_entry.get() or None,
                'salary': float(self.salary_entry.get()) if self.salary_entry.get() else None,
                'hire_date': self.hire_entry.get() or None
            }
            self.destroy()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric value for salary")