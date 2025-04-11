import mysql.connector
from mysql.connector import pooling
from datetime import datetime
from typing import List, Dict, Optional

class Database:
    __connection_pool = None

    @classmethod
    def initialize_pool(cls):
        try:
            cls.__connection_pool = pooling.MySQLConnectionPool(
                pool_name="pharmacy_pool",
                pool_size=5,
                host="localhost",
                user="root",
                password="",
                database="pharmacy_db",
                autocommit=False
            )
        except mysql.connector.Error as err:
            raise Exception(f"Database connection error: {err}")

    @classmethod
    def get_connection(cls):
        if cls.__connection_pool is None:
            cls.initialize_pool()
        return cls.__connection_pool.get_connection()

    @classmethod
    def close_connection(cls, connection, cursor=None):
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    @classmethod
    def execute_query(cls, query: str, params: tuple = None, fetch: bool = False):
        conn = cls.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            if fetch:
                return cursor.fetchall()
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            if conn:
                if 'conn' in locals() and conn:
                    if 'conn' in locals() and conn:
                        if 'conn' in locals() and conn:
                            conn.rollback()
            raise e
        finally:
            cls.close_connection(conn, cursor)

    @classmethod
    def fetch_all(cls, query: str, params: tuple = None) -> List[Dict]:
        return cls.execute_query(query, params, fetch=True)

    @classmethod
    def fetch_one(cls, query: str, params: tuple = None) -> Optional[Dict]:
        conn = cls.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            return cursor.fetchone()
        except Exception as e:
            raise e
        finally:
            cls.close_connection(conn, cursor)

    @classmethod
    def execute(cls, query: str, params: tuple = None) -> int:
        return cls.execute_query(query, params)

    @classmethod
    def execute_return_id(cls, query: str, params: tuple = None) -> int:
        conn = cls.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params or ())
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            cls.close_connection(conn, cursor)


class BaseModel:
    TABLE = ""

    @classmethod
    def get_all(cls, search_term: str = None) -> List[Dict]:
        query = f"SELECT * FROM {cls.TABLE}"
        if search_term:
            query += " WHERE name LIKE %s"
            return Database.fetch_all(query, (f"%{search_term}%",))
        return Database.fetch_all(query)
    
    @classmethod
    def get_by_id(cls, id: int) -> Optional[Dict]:
        query = f"SELECT * FROM {cls.TABLE} WHERE {cls.TABLE[:-1]}_id = %s"
        return Database.fetch_one(query, (id,))
    
    @classmethod
    def create(cls, data: Dict) -> int:
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {cls.TABLE} ({columns}) VALUES ({placeholders})"
        Database.execute(query, tuple(data.values()))
        return Database.execute_query("SELECT LAST_INSERT_ID()", fetch=True)[0]['LAST_INSERT_ID()']
    
    @classmethod
    def update(cls, id: int, data: Dict) -> bool:
        set_clause = ', '.join([f"{key}=%s" for key in data.keys()])
        query = f"UPDATE {cls.TABLE} SET {set_clause} WHERE {cls.TABLE[:-1]}_id = %s"
        try:
            Database.execute_query(query, tuple(data.values()) + (id,))
            return True
        except:
            return False
    
    @classmethod
    def delete(cls, id: int) -> bool:
        """Delete a record and its related records, ensuring no foreign key constraints are violated."""
        try:
            # Define dependent tables and their foreign key columns
            dependencies = {
                "prescription_items": "prescription_id"
            }

            # Delete related records in dependent tables
            for table, column in dependencies.items():
                delete_query = f"DELETE FROM {table} WHERE {column} = %s"
                Database.execute_query(delete_query, (id,))

            # Proceed with deletion of the main record
            query = f"DELETE FROM {cls.TABLE} WHERE {cls.TABLE[:-1]}_id = %s"
            affected_rows = Database.execute_query(query, (id,))
            return affected_rows > 0
        except Exception as e:
            raise Exception(f"Failed to delete record: {str(e)}")
            @classmethod
            def delete(cls, medicine_id: int) -> bool:
                """Delete medicine and related records"""
                try:
                    # Delete related records in the correct order
                    query = "DELETE FROM order_items WHERE medicine_id = %s"
                    Database.execute_query(query, (medicine_id,))
                    
                    # Finally, delete the medicine
                    query = f"DELETE FROM {cls.TABLE} WHERE {cls.TABLE}_id = %s"
                    affected_rows = Database.execute_query(query, (medicine_id,))
                    if affected_rows > 0:
                        return True
                    else:
                        raise ValueError(f"No medicine found with ID {medicine_id}")
                except Exception as e:
                    raise Exception(f"Failed to delete medicine: {str(e)}")

class Medicine(BaseModel):
    TABLE = "medicines"

    @classmethod
    def get_all(cls, search_term: str = None, include_supplier: bool = False) -> List[Dict]:
        """Get all medicines, with optional supplier information"""
        try:
            if include_supplier:
                # First try with the most common column names
                try:
                    query = """
                        SELECT m.*, s.name AS supplier_name 
                        FROM medicines m
                        LEFT JOIN suppliers s ON m.supplier_id = s.supplier_id
                    """
                    if search_term:
                        query += " WHERE m.name LIKE %s"
                        return Database.fetch_all(query, (f"%{search_term}%",))
                    return Database.fetch_all(query)
                except mysql.connector.Error as err:
                    if err.errno == mysql.connector.errorcode.ER_BAD_FIELD_ERROR:
                        # Fallback to alternative column names
                        query = """
                            SELECT m.*, s.supplier_name 
                            FROM medicines m
                            LEFT JOIN suppliers s ON m.supplier_id = s.supplier_id
                        """
                        if search_term:
                            query += " WHERE m.name LIKE %s"
                            return Database.fetch_all(query, (f"%{search_term}%",))
                        return Database.fetch_all(query)
                    raise

            # Basic query without supplier info
            query = f"SELECT * FROM {cls.TABLE}"
            if search_term:
                query += " WHERE name LIKE %s"
                return Database.fetch_all(query, (f"%{search_term}%",))
            return Database.fetch_all(query)

        except Exception as e:
            raise Exception(f"Failed to load medicines: {str(e)}")

    @classmethod
    def get_by_id(cls, medicine_id: int, include_supplier: bool = False) -> Optional[Dict]:
        """Get single medicine by ID, with optional supplier info"""
        try:
            if include_supplier:
                # Try with common column names first
                try:
                    query = """
                        SELECT m.*, s.name AS supplier_name 
                        FROM medicines m
                        LEFT JOIN suppliers s ON m.supplier_id = s.supplier_id
                        WHERE m.medicine_id = %s
                    """
                    return Database.fetch_one(query, (medicine_id,))
                except mysql.connector.Error as err:
                    if err.errno == mysql.connector.errorcode.ER_BAD_FIELD_ERROR:
                        # Fallback to alternative column names
                        query = """
                            SELECT m.*, s.supplier_name 
                            FROM medicines m
                            LEFT JOIN suppliers s ON m.supplier_id = s.supplier_id
                            WHERE m.medicine_id = %s
                        """
                        return Database.fetch_one(query, (medicine_id,))
                    raise

            return super().get_by_id(medicine_id)
        except Exception as e:
            raise Exception(f"Failed to load medicine: {str(e)}")

    @classmethod
    def create(cls, data: Dict) -> int:
        """Create new medicine with validation"""
        if 'supplier_id' not in data:
            raise ValueError("supplier_id is required")
        return super().create(data)

    @classmethod
    def update(cls, medicine_id: int, data: Dict) -> bool:
        """Update medicine information with validation"""
        if 'supplier_id' in data and not isinstance(data['supplier_id'], int):
            raise ValueError("supplier_id must be an integer")
        return super().update(medicine_id, data)

    @classmethod
    def reduce_stock(cls, medicine_id: int, quantity: int) -> bool:
        """Reduce medicine stock quantity"""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
            
        query = "UPDATE medicines SET quantity = quantity - %s WHERE medicine_id = %s AND quantity >= %s"
        try:
            affected_rows = Database.execute_query(query, (quantity, medicine_id, quantity))
            if affected_rows == 0:
                raise ValueError("Not enough stock or medicine not found")
            return True
        except Exception as e:
            raise Exception(f"Failed to reduce stock: {str(e)}")

    @classmethod
    def get_low_stock(cls, threshold: int = 10) -> List[Dict]:
        """Get medicines with stock below threshold"""
        query = """
            SELECT m.*, s.name AS supplier_name, s.contact_info 
            FROM medicines m
            LEFT JOIN suppliers s ON m.supplier_id = s.supplier_id
            WHERE m.quantity < %s
        """
        try:
            return Database.fetch_all(query, (threshold,))
        except mysql.connector.Error as err:
            if err.errno == mysql.connector.errorcode.ER_BAD_FIELD_ERROR:
                # Fallback without supplier info if column names don't match
                query = f"SELECT * FROM {cls.TABLE} WHERE quantity < %s"
                return Database.fetch_all(query, (threshold,))
            raise

class Supplier(BaseModel):
    TABLE = "suppliers"


class Customer(BaseModel):
    TABLE = "customers"
    
    @classmethod
    def add_loyalty_points(cls, customer_id: int, points: int) -> bool:
        query = "UPDATE customers SET loyalty_points = loyalty_points + %s WHERE customer_id = %s"
        try:
            Database.execute_query(query, (points, customer_id))
            return True
        except:
            return False


class Order(BaseModel):
    TABLE = "orders"
    
    @classmethod
    def delete_by_customer_id(cls, customer_id: int) -> bool:
        """Delete orders associated with a specific customer ID"""
        query = "DELETE FROM orders WHERE customer_id = %s"
        try:
            Database.execute_query(query, (customer_id,))
            return True
        except Exception as e:
            raise Exception(f"Failed to delete orders by customer ID: {str(e)}")

    @classmethod
    def delete(cls, customer_id: int) -> bool:
        """Delete customer and all related records"""
        try:
            # Delete related records in the correct order
            Prescription.delete_by_customer_id(customer_id)
            # Ensure the Order class is defined and implement the delete_by_customer_id method
            class Order(BaseModel):
                TABLE = "orders"
            
                @classmethod
                def delete_by_customer_id(cls, customer_id: int) -> bool:
                    """Delete orders associated with a specific customer ID"""
                    query = "DELETE FROM orders WHERE customer_id = %s"
                    try:
                        Database.execute_query(query, (customer_id,))
                        return True
                    except Exception as e:
                        raise Exception(f"Failed to delete orders by customer ID: {str(e)}")

            Order.delete_by_customer_id(customer_id)
            # Finally, delete the customer
            query = "DELETE FROM customers WHERE customer_id = %s"
            Database.execute_query(query, (customer_id,))
            return True
        except Exception as e:
            raise Exception(f"Failed to delete customer and related records: {str(e)}")


class Employee(BaseModel):
    TABLE = "employees"


class Prescription(BaseModel):
    TABLE = "prescriptions"

    @classmethod
    def create(cls, data: Dict) -> int:
        """Create a new prescription."""
        return super().create(data)

    @classmethod
    def update(cls, prescription_id: int, data: Dict) -> bool:
        """Update an existing prescription."""
        return super().update(prescription_id, data)

    @classmethod
    def delete(cls, prescription_id: int) -> bool:
        """Delete a prescription."""
        return super().delete(prescription_id)
    
    @classmethod
    def get_all(cls, search_term: str = None) -> List[Dict]:
        query = """SELECT p.*, c.name as customer_name 
                   FROM prescriptions p JOIN customers c ON p.customer_id = c.customer_id"""
        if search_term:
            query += " WHERE c.name LIKE %s OR p.doctor_name LIKE %s"
            return Database.fetch_all(query, (f"%{search_term}%", f"%{search_term}%"))
        return Database.fetch_all(query)

    @classmethod
    def delete_by_customer_id(cls, customer_id: int) -> bool:
        """Delete prescriptions and their related items associated with a specific customer ID."""
        try:
            # Delete related prescription items
            delete_items_query = """
                DELETE FROM prescription_items 
                WHERE prescription_id IN (
                    SELECT prescription_id FROM prescriptions WHERE customer_id = %s
                )
            """
            Database.execute_query(delete_items_query, (customer_id,))

            # Delete prescriptions
            delete_prescriptions_query = "DELETE FROM prescriptions WHERE customer_id = %s"
            Database.execute_query(delete_prescriptions_query, (customer_id,))
            return True
        except Exception as e:
            raise Exception(f"Failed to delete prescriptions by customer ID: {str(e)}")
    def delete_by_customer_id(cls, customer_id: int) -> bool:
        """Delete prescriptions and their related items associated with a specific customer ID."""
        try:
            # Delete related prescription items
            delete_items_query = """
                DELETE FROM prescription_items 
                WHERE prescription_id IN (
                    SELECT prescription_id FROM prescriptions WHERE customer_id = %s
                )
            """
            Database.execute_query(delete_items_query, (customer_id,))

            # Delete prescriptions
            delete_prescriptions_query = "DELETE FROM prescriptions WHERE customer_id = %s"
            Database.execute_query(delete_prescriptions_query, (customer_id,))
            return True
        except Exception as e:
            raise Exception(f"Failed to delete prescriptions by customer ID: {str(e)}")
    TABLE = "orders"
    
    @classmethod
    def create_with_details(cls, order_data: Dict, items: List[Dict]) -> int:
        conn = Database.get_connection()
        cursor = conn.cursor()
        try:
            # Create order
            query = """INSERT INTO orders 
                       (customer_id, employee_id, order_date, total_amount, order_type) 
                       VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(query, (
                order_data.get('customer_id'),
                order_data.get('employee_id'),
                order_data.get('order_date', datetime.now()),
                order_data['total_amount'],
                order_data.get('order_type', 'retail')
            ))
            order_id = cursor.lastrowid
            
            # Add order items
            for item in items:
                query = """INSERT INTO order_items 
                          (order_id, medicine_id, quantity, unit_price, subtotal) 
                          VALUES (%s, %s, %s, %s, %s)"""
                cursor.execute(query, (
                    order_id,
                    item['medicine_id'],
                    item['quantity'],
                    item['price'],
                    item['subtotal']
                ))
            
            conn.commit()
            return order_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            if conn and cursor:
                Database.close_connection(conn, cursor)

    @classmethod
    def delete_by_customer_id(cls, customer_id: int) -> bool:
        """Delete orders associated with a specific customer ID"""
        query = "DELETE FROM orders WHERE customer_id = %s"
        try:
            Database.execute_query(query, (customer_id,))
            return True
        except Exception as e:
            raise Exception(f"Failed to delete orders by customer ID: {str(e)}")
        except Exception as e:
            if 'conn' in locals() and conn:
                if conn:
                    conn.rollback()
            raise e
        finally:
            Database.close_connection(conn, cursor)

    @classmethod
    def delete_by_customer_id(cls, customer_id: int) -> bool:
        """Delete orders associated with a specific customer ID"""
        query = "DELETE FROM orders WHERE customer_id = %s"
        try:
            Database.execute_query(query, (customer_id,))
            return True
        except Exception as e:
            raise Exception(f"Failed to delete orders by customer ID: {str(e)}")


class Sale(BaseModel):
    TABLE = "sales"


class Payment(BaseModel):
    @classmethod
    def check_low_stock(cls, threshold: int = 10) -> List[Dict]:
        if threshold <= 0:
            raise ValueError("Threshold must be a positive integer")
        query = f"SELECT * FROM {cls.TABLE} WHERE quantity < %s"
        return Database.fetch_all(query, (threshold,))


class Stock(BaseModel):
    TABLE = "stock"
    
    @classmethod
    def check_low_stock(cls, threshold: int = 10) -> List[Dict]:
        query = """SELECT m.name, s.quantity_in_stock, s.reorder_level 
                   FROM stock s JOIN medicines m 
                   ON s.medicine_id = m.medicine_id 
                   WHERE s.quantity_in_stock <= s.reorder_level"""
        return Database.fetch_all(query)
    
    
    @classmethod
    def delete_by_customer_id(cls, customer_id: int) -> bool:
        """Delete stock entries associated with a specific customer ID"""
        query = "DELETE FROM stock WHERE customer_id = %s"
        try:
            Database.execute_query(query, (customer_id,))
            return True
        except Exception as e:
            raise Exception(f"Failed to delete stock by customer ID: {str(e)}")
        @classmethod
        def delete_by_customer_id(cls, customer_id: int) -> bool:
            """Delete prescriptions associated with a specific customer ID"""
            query = "DELETE FROM prescriptions WHERE customer_id = %s"
            try:
                Database.execute_query(query, (customer_id,))
                return True
            except Exception as e:
                raise Exception(f"Failed to delete prescriptions by customer ID: {str(e)}")
            
            # The duplicate method `delete_by_customer_id` in the Stock class is unnecessary and redundant.
            # Remove the duplicate method to avoid confusion and ensure proper functionality.
            
            # Remove the duplicate method `delete_by_customer_id` in the Stock class.
            # The first implementation of `delete_by_customer_id` is sufficient and should be retained.
            # Remove the duplicate method `delete_by_customer_id` in the Stock class.
            # The first implementation of `delete_by_customer_id` is sufficient and should be retained.
            
            # Remove the duplicate method `delete_by_customer_id` in the Stock class
            # The first implementation of `delete_by_customer_id` is sufficient and should be retained.
            del Stock.delete_by_customer_id
            
            
            # Add delete_by_customer_id methods for other tables

            class Payment(BaseModel):
                TABLE = "payments"

                @classmethod
                def delete_by_customer_id(cls, customer_id: int) -> bool:
                    """Delete payments associated with a specific customer ID"""
                    query = "DELETE FROM payments WHERE customer_id = %s"
                    try:
                        Database.execute_query(query, (customer_id,))
                        return True
                    except Exception as e:
                        raise Exception(f"Failed to delete payments by customer ID: {str(e)}")


            class Sale(BaseModel):
                TABLE = "sales"

                @classmethod
                def delete_by_customer_id(cls, customer_id: int) -> bool:
                    """Delete sales associated with a specific customer ID"""
                    query = "DELETE FROM sales WHERE customer_id = %s"
                    try:
                        Database.execute_query(query, (customer_id,))
                        return True
                    except Exception as e:
                        raise Exception(f"Failed to delete sales by customer ID: {str(e)}")


            class Stock(BaseModel):
                TABLE = "stock"

                @classmethod
                def delete_by_customer_id(cls, customer_id: int) -> bool:
                    """Delete stock entries associated with a specific customer ID"""
                    query = "DELETE FROM stock WHERE customer_id = %s"
                    try:
                        Database.execute_query(query, (customer_id,))
                        return True
                    except Exception as e:
                        raise Exception(f"Failed to delete stock by customer ID: {str(e)}")
                    
                    # Remove the duplicate method `delete_by_customer_id` in the Stock class
                    # The first implementation of `delete_by_customer_id` is sufficient and should be retained.
                    del Stock.delete_by_customer_id
                    
                    # Remove duplicate methods and ensure proper functionality
                    del Stock.delete_by_customer_id

                    # Add delete_by_customer_id methods for other tables
                    class Payment(BaseModel):
                        TABLE = "payments"

                        @classmethod
                        def delete_by_customer_id(cls, customer_id: int) -> bool:
                            """Delete payments associated with a specific customer ID"""
                            query = "DELETE FROM payments WHERE customer_id = %s"
                            try:
                                Database.execute_query(query, (customer_id,))
                                return True
                            except Exception as e:
                                raise Exception(f"Failed to delete payments by customer ID: {str(e)}")


                    class Sale(BaseModel):
                        TABLE = "sales"

                        @classmethod
                        def delete_by_customer_id(cls, customer_id: int) -> bool:
                            """Delete sales associated with a specific customer ID"""
                            query = "DELETE FROM sales WHERE customer_id = %s"
                            try:
                                Database.execute_query(query, (customer_id,))
                                return True
                            except Exception as e:
                                raise Exception(f"Failed to delete sales by customer ID: {str(e)}")

                            
                            
                            
                            
                            @classmethod
                            @classmethod
                            def delete(cls, prescription_id: int) -> bool:
                                """Delete a prescription and its related items."""
                                conn = Database.get_connection()
                                cursor = conn.cursor()
                                try:
                                    # Start transaction
                                    conn.autocommit = False
                        
                                    # Check if the prescription exists
                                    check_query = "SELECT * FROM prescriptions WHERE prescription_id = %s"
                                    cursor.execute(check_query, (prescription_id,))
                                    if cursor.fetchone() is None:
                                        raise ValueError(f"Prescription with ID {prescription_id} does not exist.")
                        
                                    # Delete related prescription items
                                    delete_items_query = "DELETE FROM prescription_items WHERE prescription_id = %s"
                                    cursor.execute(delete_items_query, (prescription_id,))
                        
                                    # Delete the prescription itself
                                    delete_prescription_query = "DELETE FROM prescriptions WHERE prescription_id = %s"
                                    cursor.execute(delete_prescription_query, (prescription_id,))
                        
                                    # Commit transaction
                                    conn.commit()
                                    return cursor.rowcount > 0
                                except Exception as e:
                                    conn.rollback()
                                    raise Exception(f"Failed to delete prescription: {str(e)}")
                                finally:
                                    Database.close_connection(conn, cursor)
                                
                                
                                