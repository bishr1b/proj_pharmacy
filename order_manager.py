import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import Order, Medicine, Customer, Employee, Stock, Database

class OrderManager:
    def __init__(self, parent_frame):
        self.frame = ttk.Frame(parent_frame)
        self.current_order = None
        self.order_items = []
        self.setup_ui()

    def setup_ui(self):
        # Main frames
        top_frame = ttk.Frame(self.frame)
        top_frame.pack(fill="x", padx=10, pady=10)
        
        # Order info frame
        order_info_frame = ttk.LabelFrame(top_frame, text="Order Information", padding=10)
        order_info_frame.pack(side="left", fill="y", padx=5)
        
        ttk.Label(order_info_frame, text="Customer:").grid(row=0, column=0, sticky="e")
        self.customer_combo = ttk.Combobox(order_info_frame, state="readonly")
        self.customer_combo.grid(row=0, column=1, pady=5)
        
        ttk.Label(order_info_frame, text="Employee:").grid(row=1, column=0, sticky="e")
        self.employee_combo = ttk.Combobox(order_info_frame, state="readonly")
        self.employee_combo.grid(row=1, column=1, pady=5)
        
        ttk.Label(order_info_frame, text="Order Type:").grid(row=2, column=0, sticky="e")
        self.order_type_combo = ttk.Combobox(order_info_frame, 
                                         values=["Retail", "Wholesale", "Online"])
        self.order_type_combo.grid(row=2, column=1, pady=5)
        self.order_type_combo.current(0)
        
        # Add item frame
        add_item_frame = ttk.LabelFrame(top_frame, text="Add Item", padding=10)
        add_item_frame.pack(side="left", fill="y", padx=5)
        
        ttk.Label(add_item_frame, text="Medicine:").grid(row=0, column=0, sticky="e")
        self.medicine_combo = ttk.Combobox(add_item_frame, state="readonly")
        self.medicine_combo.grid(row=0, column=1, pady=5)
        
        ttk.Label(add_item_frame, text="Quantity:").grid(row=1, column=0, sticky="e")
        self.quantity_entry = ttk.Entry(add_item_frame)
        self.quantity_entry.grid(row=1, column=1, pady=5)
        
        ttk.Button(add_item_frame, text="Add Item", 
                 command=self.add_item).grid(row=2, column=1, pady=5)
        
        # Order items treeview
        items_frame = ttk.LabelFrame(self.frame, text="Order Items", padding=10)
        items_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.items_tree = ttk.Treeview(items_frame, columns=(
            "Medicine", "Quantity", "Price", "Subtotal"
        ), show="headings")
        
        columns = [
            ("Medicine", "Medicine", 200),
            ("Quantity", "Qty", 80),
            ("Price", "Unit Price", 100),
            ("Subtotal", "Subtotal", 100)
        ]
        
        for col_id, col_text, width in columns:
            self.items_tree.heading(col_id, text=col_text)
            self.items_tree.column(col_id, width=width, anchor="center")
        
        self.items_tree.pack(fill="both", expand=True)
        
        # Total and buttons frame
        bottom_frame = ttk.Frame(self.frame)
        bottom_frame.pack(fill="x", padx=10, pady=10)
        
        self.total_label = ttk.Label(bottom_frame, text="Total: $0.00", font=("Arial", 12, "bold"))
        self.total_label.pack(side="left", padx=5)
        
        ttk.Button(bottom_frame, text="New Order", 
                 command=self.new_order).pack(side="left", padx=5)
        ttk.Button(bottom_frame, text="Save Order", 
                 command=self.save_order).pack(side="left", padx=5)
        ttk.Button(bottom_frame, text="Delete Item", 
                 command=self.delete_item).pack(side="right", padx=5)
        
        # Load initial data
        self.load_combos()
        self.new_order()

    def load_combos(self):
        try:
            # Load customers
            customers = Customer.get_all()
            self.customer_combo['values'] = [f"{c['customer_id']} - {c['name']}" for c in customers]
            if customers:
                self.customer_combo.current(0)
            
            # Load employees
            employees = Employee.get_all()
            self.employee_combo['values'] = [f"{e['employee_id']} - {e['name']}" for e in employees]
            if employees:
                self.employee_combo.current(0)
            
            # Load medicines
            medicines = Medicine.get_all()
            self.medicine_combo['values'] = [f"{m['medicine_id']} - {m['name']}" for m in medicines]
            if medicines:
                self.medicine_combo.current(0)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")

    def new_order(self):
        self.order_items = []
        self.update_items_tree()
        self.customer_combo.set('')
        self.employee_combo.set('')
        self.order_type_combo.current(0)
        self.total_label.config(text="Total: $0.00")

    def add_item(self):
        medicine = self.medicine_combo.get()
        quantity = self.quantity_entry.get()
        
        if not medicine or not quantity:
            messagebox.showwarning("Warning", "Please select medicine and enter quantity")
            return
        
        try:
            medicine_id = int(medicine.split(" - ")[0])
            quantity = int(quantity)
            
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
            
            # Get medicine details
            med = Medicine.get_by_id(medicine_id, ['medicine_id', 'name', 'quantity_in_stock', 'price', 'wholesale_price'])
            if not med:
                messagebox.showerror("Error", "Medicine not found")
                return
            
            if quantity > med['quantity_in_stock']:
                messagebox.showerror("Error", f"Only {med['quantity_in_stock']} available in stock")
                return
            
            # Calculate price based on order type
            price = float(med['price'])
            if self.order_type_combo.get() == "Wholesale" and 'wholesale_price' in med:
                price = float(med['wholesale_price'])
            
            # Add to order items
            self.order_items.append({
                'medicine_id': medicine_id,
                'name': med['name'],
                'quantity': quantity,
                'price': price,
                'subtotal': price * quantity
            })
            
            self.update_items_tree()
            self.medicine_combo.set('')
            self.quantity_entry.delete(0, tk.END)
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def update_items_tree(self):
        for row in self.items_tree.get_children():
            self.items_tree.delete(row)
        
        total = 0.0
        for item in self.order_items:
            self.items_tree.insert("", "end", values=(
                item['name'],
                item['quantity'],
                f"${item['price']:.2f}",
                f"${item['subtotal']:.2f}"
            ))
            total += item['subtotal']
        
        self.total_label.config(text=f"Total: ${total:.2f}")

    def delete_item(self):
        selected = self.items_tree.selection()
        if not selected:
            return
        
        index = self.items_tree.index(selected[0])
        if 0 <= index < len(self.order_items):
            self.order_items.pop(index)
            self.update_items_tree()

    def save_order(self):
        if not self.order_items:
            messagebox.showwarning("Warning", "No items in order")
            return
        
        customer = self.customer_combo.get()
        employee = self.employee_combo.get()
        order_type = self.order_type_combo.get()
        
        if not customer or not employee or not order_type:
            messagebox.showwarning("Warning", "Please fill all order information fields")
            return
        
        try:
            customer_id = int(customer.split(" - ")[0])
            employee_id = int(employee.split(" - ")[0])
            
            order_data = {
                'customer_id': customer_id,
                'employee_id': employee_id,
                'order_type': order_type,
                'total_amount': sum(item['subtotal'] for item in self.order_items),
                'order_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Create order with items
            order_id = Order.create_with_items(order_data, self.order_items)
            
            if not order_id:
                raise Exception("Failed to create order")
            
            # Update medicine quantities
            for item in self.order_items:
                success = Medicine.reduce_stock(item['medicine_id'], item['quantity'], item['name'])
                if not success:
                    raise Exception(f"Failed to update stock for {item['name']}")
            
            # Update customer loyalty points
            points = int(order_data['total_amount'] * 10)
            Customer.add_loyalty_points(customer_id, points)
            
            messagebox.showinfo("Success", f"Order #{order_id} created successfully")
            self.new_order()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save order: {str(e)}")
            
            
            # Helper function to reduce stock
            def reduce_stock(medicine_id, quantity, medicine_name):
                try:
                    stock = Stock.get_by_medicine_id(medicine_id)
                    if not stock:
                        raise Exception(f"Stock record not found for {medicine_name}")
                    
                    if stock['quantity_in_stock'] < quantity:
                        raise Exception(f"Insufficient stock for {medicine_name}")
                    
                    new_quantity = stock['quantity_in_stock'] - quantity
                    Stock.update_quantity(medicine_id, new_quantity)
                    return True
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to update stock: {str(e)}")
                    return False

            # Add the reduce_stock method to the Medicine class
            class Medicine:
                @staticmethod
                def reduce_stock(medicine_id, quantity, medicine_name):
                    return reduce_stock(medicine_id, quantity, medicine_name)
                
                @staticmethod
                def get_by_id(medicine_id, fields=None):
                    try:
                        fields = ", ".join(fields) if fields else "*"
                        query = f"SELECT {fields} FROM medicines m JOIN stock s ON m.medicine_id = s.medicine_id WHERE m.medicine_id = %s"
                        result = Database.execute_query(query, (medicine_id,))
                        return result[0] if result else None
                    except Exception as e:
                        raise Exception(f"Failed to fetch medicine by ID: {str(e)}")

                @staticmethod
                def get_all():
                    try:
                        query = "SELECT m.medicine_id, m.name, s.quantity_in_stock FROM medicines m JOIN stock s ON m.medicine_id = s.medicine_id"
                        return Database.execute_query(query)
                    except Exception as e:
                        raise Exception(f"Failed to fetch all medicines: {str(e)}")