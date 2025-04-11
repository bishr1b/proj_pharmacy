import tkinter as tk
from tkinter import ttk, messagebox
from database import Stock, Medicine, Database

class StockManager:
    def __init__(self, parent_frame):
        self.frame = ttk.Frame(parent_frame)
        self.setup_ui()

    def setup_ui(self):
        # Low stock alert frame
        alert_frame = ttk.LabelFrame(self.frame, text="Low Stock Alerts", padding=10)
        alert_frame.pack(fill="x", padx=10, pady=10)
        
        self.alert_tree = ttk.Treeview(alert_frame, columns=("Medicine", "Current", "Reorder"), show="headings")
        self.alert_tree.heading("Medicine", text="Medicine")
        self.alert_tree.heading("Current", text="Current Stock")
        self.alert_tree.heading("Reorder", text="Reorder Level")
        self.alert_tree.pack(fill="both", expand=True)
        
        ttk.Button(alert_frame, text="Refresh Alerts", 
                  command=self.load_low_stock).pack(pady=5)
        
        # Stock management frame
        stock_frame = ttk.LabelFrame(self.frame, text="Stock Management", padding=10)
        stock_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Search and filter
        filter_frame = ttk.Frame(stock_frame)
        filter_frame.pack(fill="x", pady=5)
        
        ttk.Label(filter_frame, text="Search:").pack(side="left")
        self.search_entry = ttk.Entry(filter_frame, width=30)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self.search_stock)
        
        # Stock treeview
        self.stock_tree = ttk.Treeview(stock_frame, columns=(
            "Medicine", "Current", "Reorder", "Last Updated"
        ), show="headings")
        
        columns = [
            ("Medicine", "Medicine", 200),
            ("Current", "Current Stock", 100),
            ("Reorder", "Reorder Level", 100),
            ("Last Updated", "Last Updated", 120)
        ]
        
        for col_id, col_text, width in columns:
            self.stock_tree.heading(col_id, text=col_text)
            self.stock_tree.column(col_id, width=width, anchor="center")
        
        self.stock_tree.pack(fill="both", expand=True)
        self.stock_tree.bind("<<TreeviewSelect>>", self.on_stock_select)
        
        # Update frame
        update_frame = ttk.Frame(stock_frame)
        update_frame.pack(fill="x", pady=5)
        
        ttk.Label(update_frame, text="New Qty:").pack(side="left")
        self.qty_entry = ttk.Entry(update_frame, width=10)
        self.qty_entry.pack(side="left", padx=5)
        
        ttk.Label(update_frame, text="Reorder Level:").pack(side="left")
        self.reorder_entry = ttk.Entry(update_frame, width=10)
        self.reorder_entry.pack(side="left", padx=5)
        
        ttk.Button(update_frame, text="Update", 
                  command=self.update_stock).pack(side="left", padx=5)
        
        # Load data
        self.load_low_stock()
        self.load_stock()

    def load_low_stock(self):
        for row in self.alert_tree.get_children():
            self.alert_tree.delete(row)
        
        try:
            low_stock = Stock.check_low_stock()
            for item in low_stock:
                self.alert_tree.insert("", "end", values=(
                    item['name'],
                    item['quantity_in_stock'],
                    item['reorder_level']
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load low stock alerts: {str(e)}")

    def load_stock(self, search_term=None):
        for row in self.stock_tree.get_children():
            self.stock_tree.delete(row)
        
        query = """SELECT m.name, s.quantity_in_stock, s.reorder_level, s.last_updated 
                  FROM stock s JOIN medicines m ON s.medicine_id = m.medicine_id"""
        
        if search_term:
            query += " WHERE m.name LIKE %s"
            try:
                stock_items = Database.execute_query(query, (f"%{search_term}%",), fetch=True)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load stock: {str(e)}")
                return
        else:
            try:
                stock_items = Database.execute_query(query, fetch=True)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load stock: {str(e)}")
                return
        
        for item in stock_items:
            self.stock_tree.insert("", "end", values=(
                item['name'],
                item['quantity_in_stock'],
                item['reorder_level'],
                item['last_updated'].strftime("%Y-%m-%d") if item['last_updated'] else "N/A"
            ))

    def search_stock(self, event=None):
        self.load_stock(self.search_entry.get())

    def on_stock_select(self, event):
        selected = self.stock_tree.selection()
        if selected:
            values = self.stock_tree.item(selected[0])['values']
            self.qty_entry.delete(0, tk.END)
            self.qty_entry.insert(0, str(values[1]))
            self.reorder_entry.delete(0, tk.END)
            self.reorder_entry.insert(0, str(values[2]))

    def update_stock(self):
        selected = self.stock_tree.selection()
        if not selected:
            return
        
        medicine_name = self.stock_tree.item(selected[0])['values'][0]
        new_qty = self.qty_entry.get()
        new_reorder = self.reorder_entry.get()
        
        try:
            new_qty = int(new_qty)
            new_reorder = int(new_reorder)
            
            # Get medicine ID
            med = next((m for m in Medicine.get_all() if m['name'] == medicine_name), None)
            if not med:
                messagebox.showerror("Error", "Medicine not found")
                return
            
            # Update stock
            try:
                Database.execute_query(
                    """UPDATE stock SET quantity_in_stock = %s, 
                      reorder_level = %s, last_updated = CURRENT_DATE 
                      WHERE medicine_id = %s""",
                    (new_qty, new_reorder, med['medicine_id'])
                )
                
                messagebox.showinfo("Success", "Stock updated successfully")
                self.load_low_stock()
                self.load_stock()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update stock: {str(e)}")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for quantity and reorder level")  