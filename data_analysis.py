import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

# Plot settings
sns.set(style="whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)

# Connect to SQLite database
conn = sqlite3.connect("pharmacy_db.sqlite")  # Change the path if needed

# Load data from relevant tables
sales_df = pd.read_sql_query("SELECT * FROM sales", conn)
medicines_df = pd.read_sql_query("SELECT * FROM medicine", conn)
employees_df = pd.read_sql_query("SELECT * FROM employee", conn)

# Merge sales with medicine details
sales_merged = sales_df.merge(medicines_df, left_on='medicine_id', right_on='id')

# --- Analysis 1: Top Selling Medicines ---
top_meds = sales_merged.groupby('name')['quantity'].sum().sort_values(ascending=False).head(10)
top_meds.plot(kind='bar', title='Top 10 Selling Medicines')
plt.xlabel('Medicine')
plt.ylabel('Total Sold')
plt.tight_layout()
plt.savefig("top_medicines.png")
plt.clf()

# --- Analysis 2: Monthly Sales Trend ---
sales_df['date'] = pd.to_datetime(sales_df['date'])
sales_df['month'] = sales_df['date'].dt.to_period('M')
monthly_sales = sales_df.groupby('month')['total_price'].sum()
monthly_sales.plot(kind='line', marker='o', title='Monthly Sales Revenue')
plt.ylabel('Revenue')
plt.xlabel('Month')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("monthly_sales.png")
plt.clf()

# --- Analysis 3: Employee Sales Performance ---
sales_by_emp = sales_df.groupby('employee_id')['total_price'].sum().reset_index()
sales_by_emp = sales_by_emp.merge(employees_df, left_on='employee_id', right_on='id')
sns.barplot(data=sales_by_emp, x='name', y='total_price')
plt.title('Employee Sales Performance')
plt.xlabel('Employee')
plt.ylabel('Total Sales')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("employee_performance.png")
plt.clf()

# --- Analysis 4: Low Stock Medicines ---
low_stock = medicines_df[medicines_df['quantity'] < 20]
print("--- Medicines with Low Stock ---")
print(low_stock[['name', 'quantity']])

# --- Analysis 5: Restock Recommendation System ---
# Filter last 30 days of sales
last_30_days = datetime.today() - timedelta(days=30)
recent_sales = sales_merged[sales_merged['date'] >= pd.to_datetime(last_30_days)]

# Average daily sales per medicine
daily_sales = recent_sales.groupby('medicine_id')['quantity'].sum() / 30

# Join with current stock
restock_df = medicines_df[['id', 'name', 'quantity']].set_index('id').join(daily_sales.rename('avg_daily_sales'))
restock_df = restock_df.fillna(0)

# Estimate days of stock left
restock_df['days_left'] = restock_df['quantity'] / restock_df['avg_daily_sales'].replace(0, 1)

# Recommend reorder if stock < 10 days
restock_df['recommended_reorder'] = restock_df.apply(
    lambda row: max(0, int((30 * row['avg_daily_sales']) - row['quantity'])) if row['days_left'] < 10 else 0,
    axis=1
)

restock_needed = restock_df[restock_df['recommended_reorder'] > 0][['name', 'quantity', 'avg_daily_sales', 'recommended_reorder']]
print("\n--- Restock Recommendations ---")
print(restock_needed)

# Close DB connection
conn.close()

print("\nAnalysis complete. Charts saved and recommendations printed.")
