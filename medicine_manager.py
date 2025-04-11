import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import traceback
from database import Medicine, Supplier, Database

class MedicineManager:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.current_medicine = None
        self.setup_ui()

    def setup_ui(self):
        """Initialize all UI components"""
        # Search Frame
        search_frame = ttk.Frame(self.frame)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_medicines())
        
        # Treeview
        self.tree = ttk.Treeview(self.frame, columns=(
            "ID", "Name", "Qty", "Price", "Expiry", "Category", "Supplier"
        ), show="headings", selectmode="browse")
        
        # Configure columns
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Qty", text="Quantity")
        self.tree.heading("Price", text="Price")
        self.tree.heading("Expiry", text="Expiry Date")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Supplier", text="Supplier")
        
        self.tree.column("ID", width=50, anchor=tk.CENTER)
        self.tree.column("Name", width=150)
        self.tree.column("Qty", width=80, anchor=tk.CENTER)
        self.tree.column("Price", width=80, anchor=tk.CENTER)
        self.tree.column("Expiry", width=100, anchor=tk.CENTER)
        self.tree.column("Category", width=100)
        self.tree.column("Supplier", width=150)
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # Buttons
        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Add", command=self.add_medicine).pack(side=tk.LEFT, padx=5)
        self.edit_btn = ttk.Button(btn_frame, text="Edit", state=tk.DISABLED, command=self.edit_medicine)
        self.edit_btn.pack(side=tk.LEFT, padx=5)
        self.delete_btn = ttk.Button(btn_frame, text="Delete", state=tk.DISABLED, command=self.delete_medicine)
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Refresh", command=self.load_medicines).pack(side=tk.RIGHT, padx=5)
        
        # Load initial data
        self.load_medicines()

    def load_medicines(self):
        """Load medicines with optional search filter"""
        search_term = self.search_entry.get()
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        try:
            medicines = Medicine.get_all(search_term if search_term else None, include_supplier=True)
            for med in medicines:
                self.tree.insert("", tk.END, values=(
                    med['medicine_id'],
                    med['name'],
                    med['quantity'],
                    f"${med['price']:.2f}",
                    med['expiry_date'].strftime("%Y-%m-%d") if med['expiry_date'] else "N/A",
                    med['category'] or "N/A",
                    med.get('supplier_name', "N/A")
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load medicines: {str(e)}")

    def on_select(self, event):
        """Handle medicine selection"""
        selected = self.tree.selection()
        if selected:
            self.current_medicine = self.tree.item(selected[0])['values']
            self.edit_btn.config(state=tk.NORMAL)
            self.delete_btn.config(state=tk.NORMAL)
        else:
            self.current_medicine = None
            self.edit_btn.config(state=tk.DISABLED)
            self.delete_btn.config(state=tk.DISABLED)

    def add_medicine(self):
        """Open add medicine dialog"""
        dialog = MedicineDialog(self.frame, "Add Medicine")
        if dialog.result:
            try:
                # Convert price to float and quantity to int
                dialog.result['price'] = float(dialog.result['price'])
                dialog.result['quantity'] = int(dialog.result['quantity'])
                
                Medicine.create(dialog.result)
                self.load_medicines()
                messagebox.showinfo("Success", "Medicine added successfully")
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid input: {str(e)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add medicine: {str(e)}")

    def edit_medicine(self):
        """Open edit medicine dialog"""
        if not self.current_medicine:
            return
            
        medicine_id = self.current_medicine[0]
        try:
            medicine_data = Medicine.get_by_id(medicine_id, include_supplier=True)
            if not medicine_data:
                messagebox.showerror("Error", "Medicine not found")
                return
                
            dialog = MedicineDialog(
                self.frame, 
                "Edit Medicine",
                initial_data={
                    'name': medicine_data['name'],
                    'quantity': medicine_data['quantity'],
                    'price': medicine_data['price'],
                    'expiry_date': medicine_data['expiry_date'].strftime("%Y-%m-%d") if medicine_data['expiry_date'] else "",
                    'category': medicine_data['category'] or "",
                    'manufacturer': medicine_data.get('manufacturer', ""),
                    'batch_number': medicine_data.get('batch_number', ""),
                    'description': medicine_data.get('description', ""),
                    'supplier_id': medicine_data['supplier_id']
                }
            )
            
            if dialog.result:
                # Convert price to float and quantity to int
                dialog.result['price'] = float(dialog.result['price'])
                dialog.result['quantity'] = int(dialog.result['quantity'])
                
                Medicine.update(medicine_id, dialog.result)
                self.load_medicines()
                messagebox.showinfo("Success", "Medicine updated successfully")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to edit medicine: {str(e)}")

    def delete_medicine(self):
        """Delete selected medicine from the database"""
        if not self.current_medicine:
            messagebox.showwarning("Warning", "No medicine selected")
            return
    
        # Confirm deletion with user
        if not messagebox.askyesno(
            "Confirm Deletion", 
            f"Are you sure you want to delete {self.current_medicine[1]}?",
            icon='warning'):
            return
    
        try:
            # Get medicine ID from current selection
            medicine_id = self.current_medicine[0]
    
            # Attempt to delete the medicine
            success = Medicine.delete(medicine_id)
    
            if success:
                self.load_medicines()  # Refresh the list
                self.current_medicine = None  # Clear current selection
                messagebox.showinfo("Success", "Medicine deleted successfully")
            else:
                messagebox.showerror("Error", "Failed to delete medicine")
    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete medicine: {str(e)}")
            print(f"Delete error: {traceback.format_exc()}")
        
        # Confirm deletion with user
        if not messagebox.askyesno(
            "Confirm Deletion", 
            f"Are you sure you want to delete {self.current_medicine[1]}?",
            icon='warning'):
            return
        
        try:
            # Get medicine ID from current selection
            medicine_id = self.current_medicine[0]
            
            # First check if medicine exists
            medicine = Medicine.get_by_id(medicine_id)
            if not medicine:
                messagebox.showerror("Error", "Medicine not found")
                return
                
            # Check if medicine is referenced in any orders
            if self.is_medicine_referenced(medicine_id):
                messagebox.showerror("Error", 
                    "Cannot delete - this medicine is referenced in existing orders")
                return
                
            # Perform the deletion
            success = Medicine.delete(medicine_id)
            
            if success:
                self.load_medicines()  # Refresh the list
                self.current_medicine = None  # Clear current selection
                messagebox.showinfo("Success", "Medicine deleted successfully")
            else:
                messagebox.showerror("Error", "Failed to delete medicine")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete medicine: {str(e)}")
            print(f"Delete error: {traceback.format_exc()}")

    def is_medicine_referenced(self, medicine_id):
        """Check if medicine is referenced in order_items table"""
        try:
            query = "SELECT COUNT(*) FROM order_items WHERE medicine_id = %s"
            result = Database.fetch_one(query, (medicine_id,))
            return result['COUNT(*)'] > 0 if result else False
        except Exception as e:
            messagebox.showerror("Error", f"Could not check references: {str(e)}")
            return True  # Be conservative - prevent deletion if we can't check

    def get_supplier_name(self, supplier_id):
        """Get supplier name by ID"""
        if not supplier_id:
            return "N/A"
        try:
            supplier = Supplier.get_by_id(supplier_id)
            return supplier['name'] if supplier else "N/A"
        except Exception:
            return "N/A"


class MedicineDialog(tk.Toplevel):
    def __init__(self, parent, title, initial_data=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("500x400")
        self.resizable(False, False)
        self.result = None
        
        # Form fields
        fields = [
            ("Name", "name", True),
            ("Quantity", "quantity", True),
            ("Price", "price", True),
            ("Expiry Date (YYYY-MM-DD)", "expiry_date", False),
            ("Manufacturer", "manufacturer", False),
            ("Batch Number", "batch_number", False),
            ("Category", "category", False),
            ("Description", "description", False)
        ]
        
        self.entries = {}
        for i, (label, field, required) in enumerate(fields):
            ttk.Label(self, text=label + ("" if not required else "*")).grid(row=i, column=0, padx=10, pady=5, sticky=tk.E)
            entry = ttk.Entry(self, width=30)
            entry.grid(row=i, column=1, padx=10, pady=5)
            if initial_data and field in initial_data:
                entry.insert(0, str(initial_data[field]) if initial_data[field] is not None else "")
            self.entries[field] = entry
        
        # Supplier selection
        ttk.Label(self, text="Supplier").grid(row=len(fields), column=0, padx=10, pady=5, sticky=tk.E)
        self.supplier_combo = ttk.Combobox(self, state="readonly")
        self.supplier_combo.grid(row=len(fields), column=1, padx=10, pady=5)
        self.load_suppliers(initial_data.get('supplier_id') if initial_data else None)
        
        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=len(fields)+1, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Save", command=self.on_save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side=tk.RIGHT, padx=5)
        
        self.transient(parent)
        self.grab_set()
        self.wait_window(self)
    
    def load_suppliers(self, selected_supplier_id=None):
        """Load suppliers into combobox and select the current one if provided"""
        try:
            suppliers = Supplier.get_all()
            supplier_list = []
            selected_index = 0
            
            for i, supplier in enumerate(suppliers):
                display_text = f"{supplier['supplier_id']} - {supplier['name']}"
                supplier_list.append(display_text)
                if selected_supplier_id and supplier['supplier_id'] == selected_supplier_id:
                    selected_index = i
            
            self.supplier_combo['values'] = supplier_list
            if selected_supplier_id and suppliers:
                self.supplier_combo.current(selected_index)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load suppliers: {str(e)}")

    def on_save(self):
        """Validate and save form data"""
        try:
            # Validate required fields
            if not all(self.entries[f].get() for f in ['name', 'quantity', 'price']):
                raise ValueError("Required fields are missing")
                
            # Validate numeric fields
            try:
                int(self.entries['quantity'].get())
                float(self.entries['price'].get())
            except ValueError:
                raise ValueError("Quantity must be integer and Price must be number")
                
            # Prepare result dictionary
            self.result = {
                'name': self.entries['name'].get(),
                'quantity': self.entries['quantity'].get(),
                'price': self.entries['price'].get(),
                'expiry_date': self.entries['expiry_date'].get() or None,
                'manufacturer': self.entries['manufacturer'].get() or None,
                'batch_number': self.entries['batch_number'].get() or None,
                'category': self.entries['category'].get() or None,
                'description': self.entries['description'].get() or None,
                'supplier_id': int(self.supplier_combo.get().split(" - ")[0]) if self.supplier_combo.get() else None
            }
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Validation Error", f"Validation error: {str(e)}")
            
            def delete_medicine(self):
                """Delete selected medicine from the database"""
                if not self.current_medicine:
                    return

                if messagebox.askyesno("Confirm", "Delete this medicine?"):
                    try:
                        # Delete related rows in dependent tables
                        medicine_id = self.current_medicine[0]
                        # Ensure you have methods to delete related data by medicine_id
                        Database.execute("DELETE FROM order_items WHERE medicine_id = %s", (medicine_id,))

                        # Delete the medicine
                        Medicine.delete(medicine_id)
                        self.load_medicines()
                        messagebox.showinfo("Success", "Medicine deleted successfully")
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to delete medicine: {str(e)}")
                        
                        
                        