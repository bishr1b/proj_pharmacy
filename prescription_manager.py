import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from database import Prescription, Customer, Medicine, Database

class PrescriptionDialog(tk.Toplevel):
    def __init__(self, parent, title, data=None):
        super().__init__(parent)
        self.title(title)
        self.result = None
        self.data = data if data else {
            'prescription': {
                'customer_id': None,
                'doctor_name': '',
                'doctor_license': '',
                'issue_date': datetime.now().strftime("%Y-%m-%d"),
                'expiry_date': (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
                'notes': ''
            },
            'items': []
        }
        
        self.setup_ui()
        self.load_initial_data()
        
    def setup_ui(self):
        self.geometry("800x600")
        self.resizable(True, True)
        
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Prescription details frame
        details_frame = ttk.LabelFrame(main_frame, text="Prescription Details")
        details_frame.pack(fill="x", padx=5, pady=5)
        
        # Customer selection
        ttk.Label(details_frame, text="Customer:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.customer_combo = ttk.Combobox(details_frame, state="readonly")
        self.customer_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        # Doctor information
        ttk.Label(details_frame, text="Doctor Name:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.doctor_name_entry = ttk.Entry(details_frame)
        self.doctor_name_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(details_frame, text="License No:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.license_entry = ttk.Entry(details_frame)
        self.license_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        
        # Dates
        ttk.Label(details_frame, text="Issue Date:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.issue_date_entry = ttk.Entry(details_frame)
        self.issue_date_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(details_frame, text="Expiry Date:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.expiry_date_entry = ttk.Entry(details_frame)
        self.expiry_date_entry.grid(row=4, column=1, sticky="ew", padx=5, pady=5)
        
        # Notes
        ttk.Label(details_frame, text="Notes:").grid(row=5, column=0, sticky="nw", padx=5, pady=5)
        self.notes_text = tk.Text(details_frame, height=4, width=40)
        self.notes_text.grid(row=5, column=1, sticky="ew", padx=5, pady=5)
        
        # Items frame
        items_frame = ttk.LabelFrame(main_frame, text="Prescription Items")
        items_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Treeview for items
        self.items_tree = ttk.Treeview(items_frame, columns=("ID", "Medicine", "Quantity", "Dosage", "Instructions"), show="headings")
        self.items_tree.heading("ID", text="Medicine ID")
        self.items_tree.heading("Medicine", text="Medicine")
        self.items_tree.heading("Quantity", text="Quantity")
        self.items_tree.heading("Dosage", text="Dosage")
        self.items_tree.heading("Instructions", text="Instructions")
        
        self.items_tree.column("ID", width=80, anchor="center")
        self.items_tree.column("Medicine", width=200)
        self.items_tree.column("Quantity", width=80, anchor="center")
        self.items_tree.column("Dosage", width=150)
        self.items_tree.column("Instructions", width=200)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(items_frame, orient="vertical", command=self.items_tree.yview)
        self.items_tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid layout
        self.items_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Configure grid weights
        items_frame.grid_rowconfigure(0, weight=1)
        items_frame.grid_columnconfigure(0, weight=1)
        
        # Item controls
        controls_frame = ttk.Frame(items_frame)
        controls_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)
        
        ttk.Button(controls_frame, text="Add Item", command=self.add_item).pack(side="left", padx=5)
        ttk.Button(controls_frame, text="Edit Item", command=self.edit_item).pack(side="left", padx=5)
        ttk.Button(controls_frame, text="Remove Item", command=self.remove_item).pack(side="left", padx=5)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", padx=5, pady=10)
        
        ttk.Button(button_frame, text="Save", command=self.save).pack(side="right", padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side="right", padx=5)
        
        # Load customers and medicines
        self.load_customers()
        
    def load_initial_data(self):
        # Set prescription data
        pres_data = self.data['prescription']
        if pres_data['customer_id']:
            for i, customer in enumerate(self.customer_combo['values']):
                if customer.startswith(f"{pres_data['customer_id']} -"):
                    self.customer_combo.current(i)
                    break
        
        self.doctor_name_entry.insert(0, pres_data['doctor_name'] or '')
        self.license_entry.insert(0, pres_data['doctor_license'] or '')
        self.issue_date_entry.insert(0, pres_data['issue_date'] or '')
        self.expiry_date_entry.insert(0, pres_data['expiry_date'] or '')
        self.notes_text.insert("1.0", pres_data['notes'] or '')
        
        # Load items
        for item in self.data['items']:
            med = Medicine.get_by_id(item['medicine_id'])
            self.items_tree.insert("", "end", values=(
                item['medicine_id'],
                med['name'] if med else "Unknown",
                item['quantity'],
                item['dosage'] or '',
                item['instructions'] or ''
            ))
    
    def load_customers(self):
        try:
            customers = Customer.get_all()
            self.customer_combo['values'] = [f"{c['customer_id']} - {c['name']}" for c in customers]
            if customers and not self.data['prescription']['customer_id']:
                self.customer_combo.current(0)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load customers: {str(e)}")
    
    def add_item(self):
        dialog = ItemDialog(self)
        if dialog.result:
            med = Medicine.get_by_id(dialog.result['medicine_id'])
            if not med:
                messagebox.showerror("Error", "Selected medicine not found")
                return
            
            if dialog.result['quantity'] <= 0:
                messagebox.showerror("Error", "Quantity must be positive")
                return
            
            # Check if medicine already exists in items
            for child in self.items_tree.get_children():
                values = self.items_tree.item(child)['values']
                if values and values[0] == dialog.result['medicine_id']:
                    messagebox.showerror("Error", "This medicine is already in the prescription")
                    return
            
            self.items_tree.insert("", "end", values=(
                dialog.result['medicine_id'],
                med['name'],
                dialog.result['quantity'],
                dialog.result['dosage'],
                dialog.result['instructions']
            ))
    
    def edit_item(self):
        selected = self.items_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item to edit")
            return
        
        item = self.items_tree.item(selected[0])['values']
        if not item:
            return
        
        dialog = ItemDialog(self, data={
            'medicine_id': item[0],
            'quantity': item[2],
            'dosage': item[3],
            'instructions': item[4]
        })
        
        if dialog.result:
            med = Medicine.get_by_id(dialog.result['medicine_id'])
            if not med:
                messagebox.showerror("Error", "Selected medicine not found")
                return
            
            if dialog.result['quantity'] <= 0:
                messagebox.showerror("Error", "Quantity must be positive")
                return
            
            self.items_tree.item(selected[0], values=(
                dialog.result['medicine_id'],
                med['name'],
                dialog.result['quantity'],
                dialog.result['dosage'],
                dialog.result['instructions']
            ))
    
    def remove_item(self):
        selected = self.items_tree.selection()
        if selected:
            self.items_tree.delete(selected[0])
    
    def save(self):
        try:
            # Validate customer
            customer = self.customer_combo.get()
            if not customer:
                messagebox.showerror("Error", "Please select a customer")
                return
            
            customer_id = int(customer.split(" - ")[0])
            
            # Validate dates
            issue_date = self.issue_date_entry.get()
            expiry_date = self.expiry_date_entry.get()
            
            try:
                datetime.strptime(issue_date, "%Y-%m-%d")
                if expiry_date:
                    datetime.strptime(expiry_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
                return
            
            # Validate items
            if not self.items_tree.get_children():
                messagebox.showerror("Error", "Please add at least one item to the prescription")
                return
            
            # Collect items
            items = []
            for child in self.items_tree.get_children():
                values = self.items_tree.item(child)['values']
                items.append({
                    'medicine_id': values[0],
                    'quantity': values[2],
                    'dosage': values[3],
                    'instructions': values[4]
                })
            
            # Prepare result
            self.result = {
                'prescription': {
                    'customer_id': customer_id,
                    'doctor_name': self.doctor_name_entry.get(),
                    'doctor_license': self.license_entry.get(),
                    'issue_date': issue_date,
                    'expiry_date': expiry_date if expiry_date else None,
                    'notes': self.notes_text.get("1.0", "end-1c")
                },
                'items': items
            }
            
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Validation failed: {str(e)}")

class ItemDialog(tk.Toplevel):
    def __init__(self, parent, data=None):
        super().__init__(parent)
        self.title("Prescription Item")
        self.result = None
        self.data = data if data else {
            'medicine_id': None,
            'quantity': 1,
            'dosage': '',
            'instructions': ''
        }
        
        self.setup_ui()
        self.load_initial_data()
        
    def setup_ui(self):
        self.geometry("400x300")
        
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Medicine selection
        ttk.Label(main_frame, text="Medicine:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.medicine_combo = ttk.Combobox(main_frame, state="readonly")
        self.medicine_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        # Quantity
        ttk.Label(main_frame, text="Quantity:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.quantity_entry = ttk.Entry(main_frame)
        self.quantity_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        # Dosage
        ttk.Label(main_frame, text="Dosage:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.dosage_entry = ttk.Entry(main_frame)
        self.dosage_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        
        # Instructions
        ttk.Label(main_frame, text="Instructions:").grid(row=3, column=0, sticky="nw", padx=5, pady=5)
        self.instructions_text = tk.Text(main_frame, height=4, width=30)
        self.instructions_text.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, sticky="e", pady=10)
        
        ttk.Button(button_frame, text="Save", command=self.save).pack(side="right", padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side="right", padx=5)
        
        # Load medicines
        self.load_medicines()
    
    def load_initial_data(self):
        if self.data['medicine_id']:
            for i, med in enumerate(self.medicine_combo['values']):
                if med.startswith(f"{self.data['medicine_id']} -"):
                    self.medicine_combo.current(i)
                    break
        
        self.quantity_entry.insert(0, str(self.data['quantity']))
        self.dosage_entry.insert(0, self.data['dosage'] or '')
        self.instructions_text.insert("1.0", self.data['instructions'] or '')
    
    def load_medicines(self):
        try:
            medicines = Medicine.get_all()
            self.medicine_combo['values'] = [f"{m['medicine_id']} - {m['name']} ({m['quantity']} in stock)" for m in medicines]
            if medicines and not self.data['medicine_id']:
                self.medicine_combo.current(0)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load medicines: {str(e)}")
    
    def save(self):
        try:
            # Validate medicine
            medicine = self.medicine_combo.get()
            if not medicine:
                messagebox.showerror("Error", "Please select a medicine")
                return
            
            medicine_id = int(medicine.split(" - ")[0])
            
            # Validate quantity
            try:
                quantity = int(self.quantity_entry.get())
                if quantity <= 0:
                    raise ValueError("Quantity must be positive")
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid positive quantity")
                return
            
            self.result = {
                'medicine_id': medicine_id,
                'quantity': quantity,
                'dosage': self.dosage_entry.get(),
                'instructions': self.instructions_text.get("1.0", "end-1c")
            }
            
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Validation failed: {str(e)}")

class PrescriptionManager:
    def __init__(self, parent_frame):
        self.frame = ttk.Frame(parent_frame)
        self.current_prescription = None
        self.setup_ui()

    def setup_ui(self):
        # Search frame
        search_frame = ttk.Frame(self.frame)
        search_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(search_frame, text="Customer:").pack(side="left")
        self.customer_combo = ttk.Combobox(search_frame, state="readonly")
        self.customer_combo.pack(side="left", padx=5)
        
        ttk.Button(search_frame, text="Search", 
                  command=self.search_prescriptions).pack(side="left", padx=5)
        
        # Prescription treeview
        self.tree = ttk.Treeview(self.frame, columns=("ID", "Customer", "Doctor", "Issued", "Expires", "Items"), show="headings")
        
        columns = [
            ("ID", "Prescription ID", 80),
            ("Customer", "Customer", 150),
            ("Doctor", "Doctor", 150),
            ("Issued", "Issued Date", 100),
            ("Expires", "Expiry Date", 100),
            ("Items", "Items", 50)
        ]
        
        for col_id, col_text, width in columns:
            self.tree.heading(col_id, text=col_text)
            self.tree.column(col_id, width=width, anchor="center")
        
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.on_prescription_select)
        
        # Button frame
        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        self.add_btn = ttk.Button(btn_frame, text="Add", command=self.show_add_dialog)
        self.edit_btn = ttk.Button(btn_frame, text="Edit", command=self.show_edit_dialog, state="disabled")
        self.delete_btn = ttk.Button(btn_frame, text="Delete", command=self.delete_prescription, state="disabled")
        self.view_btn = ttk.Button(btn_frame, text="View Items", command=self.view_items, state="disabled")
        
        self.add_btn.pack(side="left", padx=5)
        self.edit_btn.pack(side="left", padx=5)
        self.delete_btn.pack(side="left", padx=5)
        self.view_btn.pack(side="right", padx=5)
        
        # Load initial data
        self.load_customers()
        self.load_prescriptions()

    def load_customers(self):
        try:
            customers = Customer.get_all()
            self.customer_combo['values'] = [f"{c['customer_id']} - {c['name']}" for c in customers]
            if customers:
                self.customer_combo.current(0)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load customers: {str(e)}")

    def load_prescriptions(self, customer_id=None):
        try:
            # Clear current entries
            for row in self.tree.get_children():
                self.tree.delete(row)
            
            query = """SELECT p.*, c.name as customer_name, 
                      (SELECT COUNT(*) FROM prescription_items WHERE prescription_id = p.prescription_id) as item_count
                      FROM prescriptions p JOIN customers c ON p.customer_id = c.customer_id"""
            
            params = []
            if customer_id:
                query += " WHERE p.customer_id = %s"
                params.append(customer_id)
            
            prescriptions = Database.execute_query(query, tuple(params) if params else None, fetch=True)
            
            if not prescriptions:
                messagebox.showinfo("Info", "No prescriptions found for the selected criteria.")
                return

            for pres in prescriptions:
                expiry_date = pres['expiry_date'].strftime("%Y-%m-%d") if pres['expiry_date'] else "N/A"
                self.tree.insert("", "end", values=(
                    pres['prescription_id'],
                    pres['customer_name'],
                    pres['doctor_name'] or "N/A",
                    pres['issue_date'].strftime("%Y-%m-%d"),
                    expiry_date,
                    pres['item_count']
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load prescriptions: {str(e)}")

    def search_prescriptions(self):
        try:
            customer = self.customer_combo.get()
            if customer:
                customer_id = int(customer.split(" - ")[0])
                self.load_prescriptions(customer_id)
            else:
                self.load_prescriptions()
        except ValueError:
            messagebox.showerror("Error", "Invalid customer selection")
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {str(e)}")

    def on_prescription_select(self, event):
        selected = self.tree.selection()
        if selected:
            try:
                self.current_prescription = self.tree.item(selected[0])['values']
                self.edit_btn.config(state="normal")
                self.delete_btn.config(state="normal")
                self.view_btn.config(state="normal")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to select prescription: {str(e)}")
                self.current_prescription = None
                self.edit_btn.config(state="disabled")
                self.delete_btn.config(state="disabled")
                self.view_btn.config(state="disabled")
        else:
            self.current_prescription = None
            self.edit_btn.config(state="disabled")
            self.delete_btn.config(state="disabled")
            self.view_btn.config(state="disabled")

    def show_add_dialog(self):
        try:
            dialog = PrescriptionDialog(self.frame, title="Add New Prescription")
            self.frame.wait_window(dialog)
            
            if dialog.result:
                # Start transaction
                Database.begin_transaction()
                
                try:
                    # Create prescription
                    prescription_id = Prescription.create(dialog.result['prescription'])
                    
                    # Add prescription items
                    for item in dialog.result['items']:
                        # Check and reserve medicine stock
                        med = Medicine.get_by_id(item['medicine_id'])
                        if not med:
                            raise ValueError(f"Medicine not found with ID: {item['medicine_id']}")
                        
                        if med['quantity'] < item['quantity']:
                            raise ValueError(f"Not enough stock for {med['name']}. Available: {med['quantity']}, Requested: {item['quantity']}")
                        
                        # Update medicine stock
                        Medicine.update_quantity(item['medicine_id'], -item['quantity'])
                        
                        # Add prescription item
                        Database.execute_query(
                            """INSERT INTO prescription_items 
                              (prescription_id, medicine_id, quantity, dosage, instructions) 
                              VALUES (%s, %s, %s, %s, %s)""",
                            (prescription_id, item['medicine_id'], item['quantity'], 
                             item['dosage'], item['instructions'])
                        )
                    
                    Database.commit_transaction()
                    self.load_prescriptions()
                    messagebox.showinfo("Success", "Prescription added successfully")
                except Exception as e:
                    Database.rollback_transaction()
                    raise e
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add prescription: {str(e)}")

    def show_edit_dialog(self):
        if not self.current_prescription:
            return
        
        prescription_id = self.current_prescription[0]
        try:
            # Get existing prescription data
            prescription = Prescription.get_by_id(prescription_id)
            if not prescription:
                raise Exception("Prescription not found")
            
            # Get existing items
            items = Database.execute_query(
                """SELECT medicine_id, quantity, dosage, instructions 
                   FROM prescription_items 
                   WHERE prescription_id = %s""",
                (prescription_id,), fetch=True
            )
            
            dialog = PrescriptionDialog(
                self.frame,
                title="Edit Prescription",
                data={
                    'prescription': {
                        'customer_id': prescription['customer_id'],
                        'doctor_name': prescription['doctor_name'],
                        'doctor_license': prescription['doctor_license'],
                        'issue_date': prescription['issue_date'].strftime("%Y-%m-%d"),
                        'expiry_date': prescription['expiry_date'].strftime("%Y-%m-%d") if prescription['expiry_date'] else None,
                        'notes': prescription['notes']
                    },
                    'items': items
                }
            )
            
            self.frame.wait_window(dialog)
            
            if dialog.result:
                # Start transaction
                Database.begin_transaction()
                
                try:
                    # Update prescription
                    Prescription.update(prescription_id, dialog.result['prescription'])
                    
                    # Get current items to compare
                    current_items = Database.execute_query(
                        "SELECT medicine_id, quantity FROM prescription_items WHERE prescription_id = %s",
                        (prescription_id,), fetch=True
                    )
                    
                    # Restore stock for removed items
                    current_items_dict = {item['medicine_id']: item['quantity'] for item in current_items}
                    new_items_dict = {item['medicine_id']: item['quantity'] for item in dialog.result['items']}
                    
                    # Process stock changes
                    for med_id, old_qty in current_items_dict.items():
                        if med_id not in new_items_dict:
                            Medicine.update_quantity(med_id, old_qty)
                        else:
                            new_qty = new_items_dict[med_id]
                            if new_qty != old_qty:
                                Medicine.update_quantity(med_id, old_qty - new_qty)
                    
                    # Delete existing items
                    Database.execute_query(
                        "DELETE FROM prescription_items WHERE prescription_id = %s",
                        (prescription_id,)
                    )
                    
                    # Add new items
                    for item in dialog.result['items']:
                        # Verify stock is available
                        med = Medicine.get_by_id(item['medicine_id'])
                        if not med or med['quantity'] < item['quantity']:
                            raise ValueError(f"Not enough stock for medicine ID {item['medicine_id']}")
                        
                        Database.execute_query(
                            """INSERT INTO prescription_items 
                              (prescription_id, medicine_id, quantity, dosage, instructions) 
                              VALUES (%s, %s, %s, %s, %s)""",
                            (prescription_id, item['medicine_id'], item['quantity'], 
                             item['dosage'], item['instructions'])
                        )
                    
                    Database.commit_transaction()
                    self.load_prescriptions()
                    messagebox.showinfo("Success", "Prescription updated successfully")
                    
                except Exception as e:
                    Database.rollback_transaction()
                    raise e
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to edit prescription: {str(e)}")

    def delete_prescription(self):
        if not self.current_prescription:
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this prescription? This action cannot be undone."):
            try:
                prescription_id = self.current_prescription[0]
                
                # Start transaction
                Database.begin_transaction()
                
                try:
                    # Check if prescription exists
                    prescription = Prescription.get_by_id(prescription_id)
                    if not prescription:
                        raise ValueError("Prescription not found.")
                    
                    # Get items to restore stock
                    items = Database.execute_query(
                        "SELECT medicine_id, quantity FROM prescription_items WHERE prescription_id = %s",
                        (prescription_id,), fetch=True
                    )
                    
                    # Restore medicine stock
                    for item in items:
                        Medicine.update_quantity(item['medicine_id'], item['quantity'])
                    
                    # Delete prescription items
                    Database.execute_query(
                        "DELETE FROM prescription_items WHERE prescription_id = %s",
                        (prescription_id,)
                    )
                    
                    # Delete prescription
                    Prescription.delete(prescription_id)
                    
                    Database.commit_transaction()
                    self.load_prescriptions()
                    messagebox.showinfo("Success", "Prescription deleted successfully.")
                except Exception as e:
                    Database.rollback_transaction()
                    raise e
            except ValueError as ve:
                messagebox.showerror("Error", str(ve))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete prescription: {str(e)}")

    def view_items(self):
        if not self.current_prescription:
            return
        
        prescription_id = self.current_prescription[0]
        try:
            items = Database.execute_query(
                """SELECT m.name, m.medicine_id, pi.quantity, pi.dosage, pi.instructions 
                  FROM prescription_items pi JOIN medicines m 
                  ON pi.medicine_id = m.medicine_id 
                  WHERE pi.prescription_id = %s""",
                (prescription_id,), fetch=True)
            
            if not items:
                messagebox.showinfo("Info", "No items found for this prescription")
                return
            
            detail_window = tk.Toplevel(self.frame)
            detail_window.title(f"Prescription #{prescription_id} Items")
            
            # Create frame for treeview and scrollbar
            container = ttk.Frame(detail_window)
            container.pack(fill="both", expand=True, padx=10, pady=10)
            
            tree = ttk.Treeview(container, columns=("ID", "Medicine", "Quantity", "Dosage", "Instructions"), show="headings")
            
            # Configure columns
            tree.heading("ID", text="Medicine ID")
            tree.heading("Medicine", text="Medicine")
            tree.heading("Quantity", text="Quantity")
            tree.heading("Dosage", text="Dosage")
            tree.heading("Instructions", text="Instructions")
            
            tree.column("ID", width=80, anchor="center")
            tree.column("Medicine", width=150)
            tree.column("Quantity", width=80, anchor="center")
            tree.column("Dosage", width=100)
            tree.column("Instructions", width=200)
            
            # Add scrollbar
            scrollbar = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            # Grid layout
            tree.grid(row=0, column=0, sticky="nsew")
            scrollbar.grid(row=0, column=1, sticky="ns")
            
            # Configure grid weights
            container.grid_rowconfigure(0, weight=1)
            container.grid_columnconfigure(0, weight=1)
            
            # Insert data
            for item in items:
                tree.insert("", "end", values=(
                    item['medicine_id'],
                    item['name'],
                    item['quantity'],
                    item['dosage'] or "N/A",
                    item['instructions'] or "N/A"
                ))
            
            # Add close button
            ttk.Button(detail_window, text="Close", command=detail_window.destroy).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to view prescription items: {str(e)}")
            
            
                        
                        