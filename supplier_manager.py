import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from database import Supplier

class SupplierManager:
    def __init__(self, parent_frame):
        self.frame = ttk.Frame(parent_frame)
        self.current_supplier = None
        self.setup_ui()

    def setup_ui(self):
        # Search frame
        search_frame = ttk.Frame(self.frame)
        search_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(search_frame, text="Search:").pack(side="left")
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self.search_suppliers)
        
        # Supplier treeview
        self.tree = ttk.Treeview(self.frame, columns=(
            "ID", "Name", "Contact", "Phone", "Email", "Country", "Terms"
        ), show="headings", selectmode="browse")
        
        columns = [
            ("ID", "ID", 50),
            ("Name", "Name", 150),
            ("Contact", "Contact", 120),
            ("Phone", "Phone", 100),
            ("Email", "Email", 150),
            ("Country", "Country", 100),
            ("Terms", "Payment Terms", 120)
        ]
        
        for col_id, col_text, width in columns:
            self.tree.heading(col_id, text=col_text)
            self.tree.column(col_id, width=width, anchor="center")
        
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.on_supplier_select)
        
        # Button frame
        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        self.add_btn = ttk.Button(btn_frame, text="Add", command=self.show_add_dialog)
        self.edit_btn = ttk.Button(btn_frame, text="Edit", command=self.show_edit_dialog, state="disabled")
        self.delete_btn = ttk.Button(btn_frame, text="Delete", command=self.delete_supplier, state="disabled")
        
        self.add_btn.pack(side="left", padx=5)
        self.edit_btn.pack(side="left", padx=5)
        self.delete_btn.pack(side="left", padx=5)
        
        ttk.Button(btn_frame, text="Refresh", command=self.load_suppliers).pack(side="right", padx=5)
        
        self.load_suppliers()

    def load_suppliers(self, search_term=None):
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        try:
            suppliers = Supplier.get_all(search_term)
            for sup in suppliers:
                self.tree.insert("", "end", values=(
                    sup['supplier_id'],
                    sup['name'],
                    sup['contact_person'] or "N/A",
                    sup['phone'] or "N/A",
                    sup['email'] or "N/A",
                    sup['country'] or "N/A",
                    sup['payment_terms'] or "N/A"
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load suppliers: {str(e)}")

    def search_suppliers(self, event=None):
        self.load_suppliers(self.search_entry.get())

    def on_supplier_select(self, event):
        selected = self.tree.selection()
        if selected:
            self.current_supplier = self.tree.item(selected[0])['values']
            self.edit_btn.config(state="normal")
            self.delete_btn.config(state="normal")
        else:
            self.current_supplier = None
            self.edit_btn.config(state="disabled")
            self.delete_btn.config(state="disabled")

    def show_add_dialog(self):
        dialog = SupplierDialog(self.frame, title="Add New Supplier")
        if dialog.result:
            try:
                Supplier.create(dialog.result)
                self.load_suppliers()
                messagebox.showinfo("Success", "Supplier added successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add supplier: {str(e)}")

    def show_edit_dialog(self):
        if not self.current_supplier:
            return
        
        supplier_id = self.current_supplier[0]
        supplier_data = {
            'name': self.current_supplier[1],
            'contact_person': self.current_supplier[2],
            'phone': self.current_supplier[3],
            'email': self.current_supplier[4],
            'country': self.current_supplier[5],
            'payment_terms': self.current_supplier[6]
        }
        
        dialog = SupplierDialog(self.frame, title="Edit Supplier", data=supplier_data)
        if dialog.result:
            try:
                Supplier.update(supplier_id, dialog.result)
                self.load_suppliers()
                messagebox.showinfo("Success", "Supplier updated successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update supplier: {str(e)}")

    def delete_supplier(self):
        if not self.current_supplier:
            return
        
        if messagebox.askyesno("Confirm", "Delete this supplier?"):
            try:
                Supplier.delete(self.current_supplier[0])
                self.load_suppliers()
                messagebox.showinfo("Success", "Supplier deleted successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete supplier: {str(e)}")

class SupplierDialog(tk.Toplevel):
    def __init__(self, parent, title, data=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x400")
        self.resizable(False, False)
        self.result = None
        
        self.data = data or {
            'name': '',
            'contact_person': '',
            'phone': '',
            'email': '',
            'country': '',
            'payment_terms': ''
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
        
        ttk.Label(self, text="Contact Person:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.contact_entry = ttk.Entry(self)
        self.contact_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.contact_entry.insert(0, self.data['contact_person'] or "")
        
        ttk.Label(self, text="Phone:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.phone_entry = ttk.Entry(self)
        self.phone_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.phone_entry.insert(0, self.data['phone'] or "")
        
        ttk.Label(self, text="Email:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.email_entry = ttk.Entry(self)
        self.email_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        self.email_entry.insert(0, self.data['email'] or "")
        
        ttk.Label(self, text="Country:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.country_entry = ttk.Entry(self)
        self.country_entry.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        self.country_entry.insert(0, self.data['country'] or "")
        
        ttk.Label(self, text="Payment Terms:").grid(row=5, column=0, padx=5, pady=5, sticky="e")
        self.terms_entry = ttk.Entry(self)
        self.terms_entry.grid(row=5, column=1, padx=5, pady=5, sticky="ew")
        self.terms_entry.insert(0, self.data['payment_terms'] or "")
        
        button_frame = ttk.Frame(self)
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Save", command=self.on_save).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side="right", padx=5)
    
    def on_save(self):
        self.result = {
            'name': self.name_entry.get(),
            'contact_person': self.contact_entry.get() or None,
            'phone': self.phone_entry.get() or None,
            'email': self.email_entry.get() or None,
            'country': self.country_entry.get() or None,
            'payment_terms': self.terms_entry.get() or None
        }
        self.destroy()