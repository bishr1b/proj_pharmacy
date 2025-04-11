-- Database schema for pharmacy management system
CREATE TABLE customers (
  customer_id int NOT NULL AUTO_INCREMENT,
  name varchar(100) NOT NULL,
  phone varchar(15) DEFAULT NULL,
  email varchar(100) DEFAULT NULL,
  address text DEFAULT NULL,
  age int DEFAULT NULL,
  loyalty_points int DEFAULT 0,
  created_at timestamp NOT NULL DEFAULT current_timestamp(),
  updated_at timestamp NULL DEFAULT NULL ON UPDATE current_timestamp(),
  PRIMARY KEY (customer_id),
  UNIQUE KEY email (email),
  KEY name (name)
);

CREATE TABLE employees (
  employee_id int NOT NULL AUTO_INCREMENT,
  name varchar(100) NOT NULL,
  role varchar(50) DEFAULT NULL,
  phone varchar(15) DEFAULT NULL,
  email varchar(100) DEFAULT NULL,
  salary decimal(10, 2) DEFAULT NULL,
  hire_date date DEFAULT NULL,
  created_at timestamp NOT NULL DEFAULT current_timestamp(),
  updated_at timestamp NULL DEFAULT NULL ON UPDATE current_timestamp(),
  PRIMARY KEY (employee_id),
  UNIQUE KEY email (email),
  KEY name (name),
  KEY role (role)
);

CREATE TABLE suppliers (
  supplier_id int NOT NULL AUTO_INCREMENT,
  name varchar(100) NOT NULL,
  contact_person varchar(85) DEFAULT NULL,
  phone varchar(15) DEFAULT NULL,
  email varchar(100) DEFAULT NULL,
  country varchar(50) DEFAULT NULL,
  payment_terms varchar(100) DEFAULT NULL,
  created_at timestamp NOT NULL DEFAULT current_timestamp(),
  updated_at timestamp NULL DEFAULT NULL ON UPDATE current_timestamp(),
  PRIMARY KEY (supplier_id),
  UNIQUE KEY email (email),
  KEY name (name)
);

CREATE TABLE medicines (
  medicine_id int NOT NULL AUTO_INCREMENT,
  name varchar(100) NOT NULL,
  quantity int NOT NULL DEFAULT 0,
  price decimal(10, 2) NOT NULL,
  expiry_date date DEFAULT NULL,
  manufacturer varchar(100) DEFAULT NULL,
  batch_number varchar(50) DEFAULT NULL,
  category varchar(50) DEFAULT NULL,
  description text DEFAULT NULL,
  supplier_id int DEFAULT NULL,
  created_at timestamp NOT NULL DEFAULT current_timestamp(),
  updated_at timestamp NULL DEFAULT NULL ON UPDATE current_timestamp(),
  PRIMARY KEY (medicine_id),
  KEY supplier_id (supplier_id),
  KEY name (name),
  KEY category (category),
  KEY expiry_date (expiry_date)
);

CREATE TABLE stock (
  stock_id int NOT NULL AUTO_INCREMENT,
  medicine_id int NOT NULL,
  quantity_in_stock int NOT NULL,
  reorder_level int NOT NULL,
  last_updated date DEFAULT NULL,
  created_at timestamp NOT NULL DEFAULT current_timestamp(),
  updated_at timestamp NULL DEFAULT NULL ON UPDATE current_timestamp(),
  PRIMARY KEY (stock_id),
  KEY medicine_id (medicine_id)
);

CREATE TABLE orders (
  order_id int NOT NULL AUTO_INCREMENT,
  customer_id int DEFAULT NULL,
  employee_id int DEFAULT NULL,
  order_type varchar(50) DEFAULT NULL,
  total_amount decimal(10, 2) NOT NULL,
  order_date timestamp NOT NULL DEFAULT current_timestamp(),
  created_at timestamp NOT NULL DEFAULT current_timestamp(),
  updated_at timestamp NULL DEFAULT NULL ON UPDATE current_timestamp(),
  PRIMARY KEY (order_id),
  KEY customer_id (customer_id),
  KEY employee_id (employee_id)
);

CREATE TABLE order_items (
  item_id int NOT NULL AUTO_INCREMENT,
  order_id int NOT NULL,
  medicine_id int NOT NULL,
  quantity int NOT NULL,
  unit_price decimal(10, 2) NOT NULL,
  subtotal decimal(10, 2) NOT NULL,
  created_at timestamp NOT NULL DEFAULT current_timestamp(),
  updated_at timestamp NULL DEFAULT NULL ON UPDATE current_timestamp(),
  PRIMARY KEY (item_id),
  KEY order_id (order_id),
  KEY medicine_id (medicine_id)
);

CREATE TABLE prescriptions (
  prescription_id int NOT NULL AUTO_INCREMENT,
  customer_id int NOT NULL,
  doctor_name varchar(100) DEFAULT NULL,
  doctor_license varchar(50) DEFAULT NULL,
  issue_date date NOT NULL,
  expiry_date date DEFAULT NULL,
  notes text DEFAULT NULL,
  created_at timestamp NOT NULL DEFAULT current_timestamp(),
  updated_at timestamp NULL DEFAULT NULL ON UPDATE current_timestamp(),
  PRIMARY KEY (prescription_id),
  KEY customer_id (customer_id)
);

CREATE TABLE prescription_items (
  item_id int NOT NULL AUTO_INCREMENT,
  prescription_id int NOT NULL,
  medicine_id int NOT NULL,
  quantity int NOT NULL,
  dosage varchar(50) DEFAULT NULL,
  instructions text DEFAULT NULL,
  created_at timestamp NOT NULL DEFAULT current_timestamp(),
  updated_at timestamp NULL DEFAULT NULL ON UPDATE current_timestamp(),
  PRIMARY KEY (item_id),
  KEY prescription_id (prescription_id),
  KEY medicine_id (medicine_id)
);

-- Foreign key constraints

-- Foreign key for medicines → suppliers
ALTER TABLE medicines
ADD FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
ON DELETE SET NULL 
ON UPDATE CASCADE;

-- orders → customers
ALTER TABLE orders
ADD FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
ON DELETE CASCADE
ON UPDATE CASCADE;

-- orders → employees
ALTER TABLE orders
ADD FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
ON DELETE SET NULL
ON UPDATE CASCADE;

-- order_items → orders
ALTER TABLE order_items
ADD FOREIGN KEY (order_id) REFERENCES orders(order_id)
ON DELETE CASCADE
ON UPDATE CASCADE;

-- order_items → medicines
ALTER TABLE order_items
ADD FOREIGN KEY (medicine_id) REFERENCES medicines(medicine_id)
ON DELETE CASCADE
ON UPDATE CASCADE;

-- prescriptions → customers
ALTER TABLE prescriptions
ADD FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
ON DELETE CASCADE
ON UPDATE CASCADE;

-- prescription_items → prescriptions
ALTER TABLE prescription_items
ADD FOREIGN KEY (prescription_id) REFERENCES prescriptions(prescription_id)
ON DELETE CASCADE
ON UPDATE CASCADE;

-- prescription_items → medicines
ALTER TABLE prescription_items
ADD FOREIGN KEY (medicine_id) REFERENCES medicines(medicine_id)
ON DELETE CASCADE
ON UPDATE CASCADE;


-- stock → medicines
ALTER TABLE stock
ADD FOREIGN KEY (medicine_id) REFERENCES medicines(medicine_id)
ON DELETE CASCADE
ON UPDATE CASCADE;



-- Sample data insertion
INSERT INTO customers (name, phone, email, address, age, loyalty_points) VALUES
('John Doe', '1234567890', 'john.doe@example.com', '123 Main St, Cityville', 35, 100),
('Jane Smith', '9876543210', 'jane.smith@example.com', '456 Elm St, Townsville', 28, 50),
('Robert Brown', '5551236789', 'robert.brown@example.com', '789 Pine St, Villagetown', 40, 75),
('Emily Johnson', '4445556666', 'emily.johnson@example.com', '321 Oak St, Hamlet', 30, 120),
('Michael White', '1112223333', 'michael.white@example.com', '654 Cedar St, Suburbia', 45, 90),
('Sarah Wilson', '7778889999', 'sarah.wilson@example.com', '987 Birch St, Metro City', 27, 30),
('David Martinez', '3334445555', 'david.martinez@example.com', '741 Maple St, Uptown', 38, 110),
('Jessica Taylor', '2223334444', 'jessica.taylor@example.com', '852 Cherry St, Downtown', 29, 55),
('Daniel Lee', '9998887777', 'daniel.lee@example.com', '963 Walnut St, Riverside', 32, 80),
('Laura Harris', '6667778888', 'laura.harris@example.com', '159 Palm St, Countryside', 36, 95);

INSERT INTO employees (name, role, phone, email, salary, hire_date) VALUES
('Alice Johnson', 'Pharmacist', '5551234567', 'alice.johnson@example.com', 5000.00, '2022-01-10'),
('Bob Williams', 'Cashier', '5559876543', 'bob.williams@example.com', 3000.00, '2023-05-15'),
('Charlie Brown', 'Technician', '5551112222', 'charlie.brown@example.com', 4000.00, '2021-07-21'),
('Diana Green', 'Manager', '5553334444', 'diana.green@example.com', 6000.00, '2020-03-30'),
('Ethan Adams', 'Pharmacist', '5555556666', 'ethan.adams@example.com', 5500.00, '2021-11-12'),
('Fiona Clark', 'Cashier', '5557778888', 'fiona.clark@example.com', 3100.00, '2023-06-25'),
('George Miller', 'Technician', '5559990000', 'george.miller@example.com', 4200.00, '2022-02-05'),
('Hannah Carter', 'Manager', '5552223333', 'hannah.carter@example.com', 6300.00, '2019-12-15'),
('Isaac Roberts', 'Stock Keeper', '5554445555', 'isaac.roberts@example.com', 2800.00, '2022-09-18'),
('Julia Anderson', 'Delivery', '5556667777', 'julia.anderson@example.com', 2500.00, '2024-01-22');

INSERT INTO suppliers (name, contact_person, phone, email, country, payment_terms) VALUES
('MedSupply Co.', 'Michael Brown', '5553216789', 'michael@medsupply.com', 'USA', 'Net 30'),
('Pharma Distributors', 'Sarah Wilson', '5556541230', 'sarah@pharmadistributors.com', 'UK', 'Net 45'),
('HealthCare Inc.', 'John White', '5557894561', 'john@healthcare.com', 'Canada', 'Net 60'),
('BioPharma Ltd.', 'David Green', '5551239874', 'david@biopharma.com', 'Germany', 'Net 30'),
('Global Medics', 'Emma Brown', '5558527413', 'emma@globalmedics.com', 'Australia', 'Net 40'),
('ZenPharm', 'Oliver Harris', '5553698527', 'oliver@zenpharm.com', 'France', 'Net 45'),
('MediLife', 'Sophia Taylor', '5551472583', 'sophia@medilife.com', 'India', 'Net 30'),
('CureWell', 'Daniel Martinez', '5559638524', 'daniel@curewell.com', 'USA', 'Net 50'),
('QuickMeds', 'Liam Anderson', '5557531594', 'liam@quickmeds.com', 'UK', 'Net 30'),
('SafePharm', 'Isabella Roberts', '5558529637', 'isabella@safepharm.com', 'Italy', 'Net 45');

INSERT INTO medicines (name, quantity, price, expiry_date, manufacturer, batch_number, category, description, supplier_id) VALUES
('Paracetamol', 500, 2.50, '2026-12-31', 'MediPharm Ltd.', 'B12345', 'Painkiller', 'Used to treat pain and fever', 1),
('Amoxicillin', 300, 5.00, '2025-11-30', 'PharmaMed', 'A98765', 'Antibiotic', 'Used to treat bacterial infections', 2),
('Ibuprofen', 400, 3.20, '2027-02-15', 'BioPharma', 'I45678', 'Painkiller', 'Relieves pain and inflammation', 3),
('Cetirizine', 250, 1.80, '2026-06-20', 'ZenPharm', 'C65432', 'Antihistamine', 'Used for allergies', 4),
('Vitamin C', 600, 2.00, '2028-05-10', 'MediLife', 'V78901', 'Supplement', 'Boosts immune system', 5),
('Cough Syrup', 150, 4.50, '2025-09-30', 'HealthCare Inc.', 'CS85296', 'Cough Suppressant', 'Treats cough and throat irritation', 6),
('Aspirin', 700, 2.80, '2027-08-25', 'CureWell', 'A35789', 'Painkiller', 'Used to reduce pain and fever', 7),
('Insulin', 100, 25.00, '2025-12-15', 'Global Medics', 'IN45632', 'Diabetes', 'Used to control blood sugar', 8),
('Omeprazole', 300, 6.00, '2026-10-05', 'SafePharm', 'O74125', 'Acid Reducer', 'Treats heartburn and acid reflux', 9),
('Metformin', 500, 8.50, '2027-04-20', 'QuickMeds', 'M96325', 'Diabetes', 'Lowers blood sugar levels', 10);

INSERT INTO stock (medicine_id, quantity_in_stock, reorder_level, last_updated) VALUES
(1, 500, 50, '2025-03-30'),
(2, 300, 40, '2025-03-30'),
(3, 400, 50, '2025-03-30'),
(4, 250, 30, '2025-03-30'),
(5, 600, 50, '2025-03-30'),
(6, 150, 20, '2025-03-30'),
(7, 700, 60, '2025-03-30'),
(8, 100, 15, '2025-03-30'),
(9, 300, 40, '2025-03-30'),
(10, 500, 50, '2025-03-30');

INSERT INTO orders (customer_id, employee_id, order_type, total_amount, order_date) VALUES
(1, 1, 'In-Store', 25.50, '2025-03-28 10:30:00'),
(2, 2, 'Online', 15.00, '2025-03-27 14:15:00'),
(3, 3, 'In-Store', 32.80, '2025-03-26 11:45:00'),
(4, 4, 'Online', 18.90, '2025-03-25 09:10:00'),
(5, 5, 'In-Store', 42.50, '2025-03-24 16:20:00'),
(6, 6, 'Online', 12.00, '2025-03-23 12:05:00'),
(7, 7, 'In-Store', 30.75, '2025-03-22 15:30:00'),
(8, 8, 'Online', 22.40, '2025-03-21 13:40:00'),
(9, 9, 'In-Store', 28.00, '2025-03-20 10:50:00'),
(10, 10, 'Online', 19.95, '2025-03-19 08:25:00');

INSERT INTO order_items (order_id, medicine_id, quantity, unit_price, subtotal) VALUES
(1, 1, 2, 2.50, 5.00),
(2, 3, 1, 3.20, 3.20),
(3, 5, 3, 2.00, 6.00),
(4, 2, 1, 5.00, 5.00),
(5, 7, 2, 2.80, 5.60),
(6, 4, 1, 1.80, 1.80),
(7, 6, 1, 4.50, 4.50),
(8, 8, 1, 25.00, 25.00),
(9, 9, 2, 6.00, 12.00),
(10, 10, 1, 8.50, 8.50);

INSERT INTO prescriptions (customer_id, doctor_name, doctor_license, issue_date, expiry_date, notes) VALUES
(1, 'Dr. Smith', 'D12345', '2025-03-15', '2025-06-15', 'Take after meals'),
(2, 'Dr. Johnson', 'D54321', '2025-03-14', '2025-06-14', 'Avoid alcohol'),
(3, 'Dr. Williams', 'D67890', '2025-03-13', '2025-06-13', 'Take before bed'),
(4, 'Dr. Brown', 'D98765', '2025-03-12', '2025-06-12', 'With plenty of water'),
(5, 'Dr. Green', 'D24680', '2025-03-11', '2025-06-11', 'Do not exceed dosage'),
(6, 'Dr. Adams', 'D13579', '2025-03-10', '2025-06-10', 'Store in a cool place'),
(7, 'Dr. Carter', 'D86420', '2025-03-09', '2025-06-09', 'Take on an empty stomach'),
(8, 'Dr. Miller', 'D19283', '2025-03-08', '2025-06-08', 'Monitor blood pressure'),
(9, 'Dr. Roberts', 'D47592', '2025-03-07', '2025-06-07', 'Reduce salt intake'),
(10, 'Dr. Anderson', 'D38475', '2025-03-06', '2025-06-06', 'Increase fluid intake');

INSERT INTO prescription_items (prescription_id, medicine_id, quantity, dosage, instructions) VALUES
(1, 1, 20, '500mg', 'Take twice daily'),
(2, 3, 10, '200mg', 'Once daily before bed'),
(3, 5, 15, '1000mg', 'Take with food'),
(4, 2, 7, '250mg', 'Complete full course'),
(5, 7, 30, '300mg', 'One tablet every morning'),
(6, 4, 5, '10mg', 'Avoid driving'),
(7, 6, 10, '15ml', 'Shake well before use'),
(8, 8, 3, 'Units as needed', 'Monitor blood sugar'),
(9, 9, 6, '40mg', 'Take before meals'),
(10, 10, 14, '500mg', 'Take twice daily with meals');