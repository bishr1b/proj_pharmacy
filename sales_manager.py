import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import os
from database import Database

class SalesManager:
    def __init__(self, parent_frame, connection, medicine_manager):
        self.frame = ttk.Frame(parent_frame)
        self.connection = connection
        self.medicine_manager = medicine_manager
        self.bill_items = []
        self.setup_ui()

    def setup_ui(self):
        customer_frame = ttk.LabelFrame(self.frame, text="Customer Information", padding=10)
        customer_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(customer_frame, text="Customer:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.customer_var = tk.StringVar()
        self.customer_dropdown = ttk.Combobox(customer_frame, textvariable=self.customer_var, width=40)
        self.customer_dropdown.grid(row=0, column=1, padx=5, pady=5)
        self.load_customer_names()

        add_to_bill_frame = ttk.LabelFrame(self.frame, text="Add to Bill", padding=10)
        add_to_bill_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(add_to_bill_frame, text="Select Medicine").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.medicine_var = tk.StringVar()
        self.medicine_dropdown = ttk.Combobox(add_to_bill_frame, textvariable=self.medicine_var, width=40)
        self.medicine_dropdown.grid(row=0, column=1, padx=10, pady=5)
        self.load_medicine_names()

        ttk.Label(add_to_bill_frame, text="Quantity").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.quantity_entry = ttk.Entry(add_to_bill_frame, width=40)
        self.quantity_entry.grid(row=1, column=1, padx=10, pady=5)

        ttk.Button(add_to_bill_frame, text="Add to Bill", command=self.add_to_bill).grid(row=2, column=1, pady=10)

        self.bill_tree = ttk.Treeview(self.frame, columns=("Medicine", "Quantity", "Price", "Total"), show="headings")
        self.bill_tree.heading("Medicine", text="Medicine")
        self.bill_tree.heading("Quantity", text="Quantity")
        self.bill_tree.heading("Price", text="Price")
        self.bill_tree.heading("Total", text="Total")
        self.bill_tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.total_label = ttk.Label(self.frame, text="Total: $0.00", font=("Helvetica", 14))
        self.total_label.pack(pady=10)

        button_frame = ttk.Frame(self.frame)
        button_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(button_frame, text="Delete Selected", command=self.delete_from_bill).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Change Quantity", command=self.change_quantity).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Clear Bill", command=self.clear_bill).pack(side="left", padx=5)

        ttk.Button(self.frame, text="Generate Bill", command=self.generate_bill).pack(pady=10)

    def load_customer_names(self):
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT customer_id, name FROM customers ORDER BY name")
            customers = [f"{row[0]} - {row[1]}" for row in cursor.fetchall()]
            self.customer_dropdown['values'] = customers
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load customers: {e}")
        finally:
            cursor.close()

    def load_medicine_names(self):
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT medicine_id, name FROM medicines WHERE quantity > 0 ORDER BY name")
            medicines = [f"{row[0]} - {row[1]}" for row in cursor.fetchall()]
            self.medicine_dropdown['values'] = medicines
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load medicines: {e}")
        finally:
            cursor.close()

    def add_to_bill(self):
        medicine_selection = self.medicine_var.get()
        if not medicine_selection:
            messagebox.showwarning("Warning", "Please select a medicine")
            return
            
        try:
            medicine_id = int(medicine_selection.split(" - ")[0])
        except (IndexError, ValueError):
            messagebox.showerror("Error", "Invalid medicine selection")
            return
            
        try:
            quantity = int(self.quantity_entry.get())
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive quantity")
            return

        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT name, price, quantity FROM medicines WHERE medicine_id = %s", (medicine_id,))
            medicine = cursor.fetchone()

            if medicine:
                medicine_name, price, available_quantity = medicine
                if quantity > available_quantity:
                    messagebox.showerror("Error", f"Only {available_quantity} units available in stock")
                    return
                    
                total = price * quantity
                self.bill_tree.insert("", "end", 
                                    values=(medicine_name, quantity, price, total), 
                                    tags=(medicine_id,))
                self.update_total()
                self.quantity_entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add to bill: {e}")
        finally:
            cursor.close()

    def update_total(self):
        total = sum(float(self.bill_tree.item(item, "values")[3]) 
                for item in self.bill_tree.get_children())
        self.total_label.config(text=f"Total: ${total:.2f}")

    def delete_from_bill(self):
        selected_item = self.bill_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an item to delete.")
            return
        self.bill_tree.delete(selected_item)
        self.update_total()

    def change_quantity(self):
        selected_item = self.bill_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an item to change quantity.")
            return

        medicine_name, old_quantity, price, total = self.bill_tree.item(selected_item, "values")
        medicine_id = self.bill_tree.item(selected_item, "tags")[0]

        new_quantity = simpledialog.askinteger(
            "Change Quantity", 
            f"Enter new quantity for {medicine_name}:", 
            minvalue=1
        )
        
        if new_quantity:
            cursor = self.connection.cursor()
            try:
                cursor.execute("SELECT quantity FROM medicines WHERE medicine_id = %s", (medicine_id,))
                available_quantity = cursor.fetchone()[0]
                
                if new_quantity > available_quantity:
                    messagebox.showerror("Error", f"Only {available_quantity} units available in stock")
                    return
                    
                total = float(price) * new_quantity
                self.bill_tree.item(selected_item, 
                                  values=(medicine_name, new_quantity, price, total))
                self.update_total()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to change quantity: {e}")
            finally:
                cursor.close()

    def clear_bill(self):
        if not self.bill_tree.get_children():
            return
            
        if messagebox.askyesno("Confirm", "Are you sure you want to clear the bill?"):
            self.bill_tree.delete(*self.bill_tree.get_children())
            self.total_label.config(text="Total: $0.00")

    def generate_bill(self):
        if not self.bill_tree.get_children():
            messagebox.showwarning("Warning", "No items in the bill!")
            return
            
        customer_id = None
        customer_selection = self.customer_var.get()
        if customer_selection:
            try:
                customer_id = int(customer_selection.split(" - ")[0])
            except (IndexError, ValueError):
                messagebox.showerror("Error", "Invalid customer selection")
                return

        bill_data = []
        for item in self.bill_tree.get_children():
            medicine_name, quantity, price, total = self.bill_tree.item(item, "values")
            medicine_id = self.bill_tree.item(item, "tags")[0]
            bill_data.append((medicine_name, quantity, float(price), float(total), medicine_id))

        total_price = sum(item[3] for item in bill_data)

        cursor = self.connection.cursor()
        try:
            self.connection.start_transaction()
            
            for medicine_name, quantity, price, total, medicine_id in bill_data:
                cursor.execute(
                    """INSERT INTO sales 
                    (medicine_id, quantity, unit_price, total_price, sale_date, customer_id) 
                    VALUES (%s, %s, %s, %s, NOW(), %s)""",
                    (medicine_id, quantity, price, total, customer_id)
                )
                
                if not self.medicine_manager.reduce_medicine_quantity(medicine_id, quantity):
                    raise Exception("Failed to update medicine quantity")
            
            if customer_id:
                points_to_add = int(total_price)
                cursor.execute(
                    "UPDATE customers SET loyalty_points = loyalty_points + %s WHERE customer_id = %s",
                    (points_to_add, customer_id)
                )
            
            self.connection.commit()
            
            self.generate_receipt_image(
                [(item[0], item[1], item[2], item[3]) for item in bill_data], 
                total_price,
                customer_id
            )
            
            messagebox.showinfo("Success", "Bill generated and saved!")
            
            self.clear_bill()
            self.load_medicine_names()
            self.medicine_manager.load_medicines()

        except Exception as e:
            self.connection.rollback()
            messagebox.showerror("Error", f"Failed to generate bill: {str(e)}")
        finally:
            cursor.close()

    def generate_receipt_image(self, bill_data, total_price, customer_id=None):
        img = Image.new('RGB', (600, 800), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
    
        try:
            font = ImageFont.truetype("arial.ttf", 18)
            font_bold = ImageFont.truetype("arialbd.ttf", 20)
            font_large = ImageFont.truetype("arialbd.ttf", 24)
        except IOError:
            font = ImageFont.load_default()
            font_bold = ImageFont.load_default()
            font_large = ImageFont.load_default()
    
        # Pharmacy name and address
        draw.text((50, 20), "Al-Khwarizmi Pharmacy", fill=(0, 0, 0), font=font_bold)
        draw.text((50, 50), "Address: Baghdad University", fill=(0, 0, 0), font=font)
        draw.text((50, 80), "Phone: +123 456 7890", fill=(0, 0, 0), font=font)
    
        current_datetime = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        draw.text((50, 110), f"Date: {current_datetime}", fill=(0, 0, 0), font=font)
    
        y_offset = 140
        if customer_id:
            cursor = self.connection.cursor()
            try:
                cursor.execute("SELECT name, phone FROM customers WHERE customer_id = %s", (customer_id,))
                customer = cursor.fetchone()
                if customer:
                    draw.text((50, y_offset), f"Customer: {customer[0]}", fill=(0, 0, 0), font=font)
                    draw.text((50, y_offset+30), f"Phone: {customer[1]}" if customer[1] else "", 
                             fill=(0, 0, 0), font=font)
                    y_offset += 60
            except Exception:
                pass
            finally:
                cursor.close()
    
        draw.line((50, y_offset, 550, y_offset), fill=(0, 0, 0), width=2)
        y_offset += 20
    
        draw.text((50, y_offset), "Item", fill=(0, 0, 0), font=font_bold)
        draw.text((350, y_offset), "Qty", fill=(0, 0, 0), font=font_bold)
        draw.text((400, y_offset), "Price", fill=(0, 0, 0), font=font_bold)
        draw.text((500, y_offset), "Total", fill=(0, 0, 0), font=font_bold)
        y_offset += 30
    
        for medicine, quantity, price, total in bill_data:
            name_lines = [medicine[i:i+30] for i in range(0, len(medicine), 30)]
            for i, line in enumerate(name_lines):
                draw.text((50, y_offset + (i*25)), line, fill=(0, 0, 0), font=font)
            
            draw.text((350, y_offset), str(quantity), fill=(0, 0, 0), font=font)
            draw.text((400, y_offset), f"${price:.2f}", fill=(0, 0, 0), font=font)
            draw.text((500, y_offset), f"${total:.2f}", fill=(0, 0, 0), font=font)
            
            y_offset += 25 * max(1, len(name_lines)) + 10
    
        draw.line((50, y_offset, 550, y_offset), fill=(0, 0, 0), width=2)
        y_offset += 20
    
        tax = total_price * 0.10
        draw.text((400, y_offset), "Subtotal:", fill=(0, 0, 0), font=font)
        draw.text((500, y_offset), f"${total_price:.2f}", fill=(0, 0, 0), font=font)
        y_offset += 30
        
        draw.text((400, y_offset), "Tax (10%):", fill=(0, 0, 0), font=font)
        draw.text((500, y_offset), f"${tax:.2f}", fill=(0, 0, 0), font=font)
        y_offset += 30
    
        draw.text((400, y_offset), "TOTAL:", fill=(0, 0, 0), font=font_bold)
        draw.text((500, y_offset), f"${total_price + tax:.2f}", fill=(0, 0, 0), font=font_bold)
        y_offset += 40
    
        draw.text((125, y_offset), "THANK YOU FOR YOUR PURCHASE", fill=(0, 0, 0), font=font_bold)
        y_offset += 30
        draw.text((200, y_offset), "Please come again!", fill=(0, 0, 0), font=font)

        # Stars divider
        draw.text((125, y_offset + 40), "*" * 50, fill=(0, 0, 0), font=font)

        receipt_dir = os.path.join(os.getcwd(), "receipts")
        if not os.path.exists(receipt_dir):
            os.makedirs(receipt_dir)
            
        receipt_path = os.path.join(receipt_dir, f"receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        img.save(receipt_path)
        messagebox.showinfo("Receipt Saved", f"Receipt saved as:\n{receipt_path}")