#Import packages
import psycopg2
import pandas as pd 
from sqlalchemy import create_engine

####################################
#### Putting data into Postgres ####
####################################

#Read csv files
products = pd.read_csv('Desktop/BGSE/term1/data_warehousing/warehousing-operational-databases/homework/extracts/products.csv')
orders = pd.read_csv('Desktop/BGSE/term1/data_warehousing/warehousing-operational-databases/homework/extracts/orders.csv')
employees = pd.read_csv('Desktop/BGSE/term1/data_warehousing/warehousing-operational-databases/homework/extracts/employees.csv')

#Create engine to connect to the "extracts" database using Postgres
engine = create_engine('postgresql://postgres:@localhost:5432/extracts')
#Create "products" table
products.to_sql('products', engine, index = False)
#Create "orders" table
orders.to_sql('orders', engine, index = False)
#Create "employees" table
employees.to_sql('employees', engine, index = False)

##############################
#### Normalizing the data ####
##############################

#Connect to the data base using the connector from psycopg2
conn = psycopg2.connect(database = "extracts", user = "postgres", host = "localhost")
#CCreate a cursor
cur = conn.cursor()

#### Products database ####

#Add primary key
cur.execute(
	"""
	ALTER TABLE products 
		ADD PRIMARY KEY (product_code);
	"""
	)


#### Employees database

employees_querries = [
#Add primary key
"ALTER TABLE employees ADD PRIMARY KEY (employee_number);", 
#Create new table containing information related to the offices
"CREATE TABLE offices AS SELECT DISTINCT(office_code), city, state, country, office_location FROM employees;", 
#Add primary key
"ALTER TABLE offices ADD PRIMARY KEY (office_code);",
#Add reference
"ALTER TABLE employees ADD CONSTRAINT office_code FOREIGN KEY (office_code) REFERENCES offices (office_code);",
#Drop variables exported to the new table
"ALTER TABLE employees DROP COLUMN city, DROP COLUMN state, DROP COLUMN country, DROP COLUMN office_location;"]

#Execute querries
for eq in employees_querries: cur.execute(eq)


#### Orders database ####

orders_querries =  [
#Add primary key to the orders table
"ALTER TABLE orders ADD CONSTRAINT order_code PRIMARY KEY (order_number,order_line_number);",
#Create new table that consolidates the data for orders made by each customer
"CREATE TABLE orders_con AS SELECT DISTINCT (order_number), customer_number, order_date, required_date, shipped_date, status, comments FROM orders;", 
#Add primary key to the consolidated table
"ALTER TABLE orders_con ADD PRIMARY KEY (order_number);",
#Create table that contains customer's information
"CREATE TABLE customers AS SELECT DISTINCT(customer_number), customer_name, contact_last_name, contact_first_name, city, state, country, sales_rep_employee_number, credit_limit, customer_location FROM orders;",
#Add primary key to the customers table
"ALTER TABLE customers ADD PRIMARY KEY (customer_number);",
#Add references
"ALTER TABLE customers ADD CONSTRAINT sales_rep_employee_number FOREIGN KEY (sales_rep_employee_number) REFERENCES employees (employee_number);",
"ALTER TABLE orders ADD CONSTRAINT customer_number FOREIGN KEY (customer_number) REFERENCES customers (customer_number);",
"ALTER TABLE orders ADD CONSTRAINT order_number FOREIGN KEY (order_number) REFERENCES orders_con (order_number);",
"ALTER TABLE orders ADD CONSTRAINT product_code FOREIGN KEY (product_code) REFERENCES products (product_code);",
"ALTER TABLE orders_con ADD CONSTRAINT customer_number FOREIGN KEY (customer_number) REFERENCES customers (customer_number);",
#Drop variables sent to other tables
"ALTER TABLE orders DROP COLUMN order_date, DROP COLUMN required_date, DROP COLUMN status, DROP COLUMN comments, DROP COLUMN shipped_date;",
"ALTER TABLE orders DROP COLUMN customer_name, DROP COLUMN contact_last_name, DROP COLUMN contact_first_name, DROP COLUMN city, DROP COLUMN state, DROP COLUMN country, DROP COLUMN sales_rep_employee_number, DROP COLUMN credit_limit ,DROP COLUMN customer_location;"]

#Execute querries
for oq in orders_querries: cur.execute(oq)

#Close cursor
cur.close()
#Commit changes made to database
conn.commit()