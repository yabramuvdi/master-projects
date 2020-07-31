import psycopg2
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime

#################
#### Extract ####
#################


#Connect to the data base using the connector from psycopg2
conn = psycopg2.connect(database = "extracts", user = "postgres", host = "localhost")
#Create a cursor
cur = conn.cursor()

#Define function for extraction
def extract(table):
	"""This functions gets as an input the name of a table in Postgres and 
		returns as an output the content of the table as a Pandas DataFrame"""
	#Get columns names
	sql_names = """SELECT column_name FROM information_schema.columns WHERE table_name = %s;"""
	cur.execute(sql_names,(table,))
	names = cur.fetchall()
	col_names = []
	for n in names: col_names.append(n[0]) 
	#Get content
	sql_content = """SELECT * FROM %s;"""
	cur.execute(sql_content % (table,))
	content = cur.fetchall()
	return(pd.DataFrame(content, columns = col_names))


orders_df = extract('orders')
products_df = extract('products')
offices_df = extract('offices')
employees_df = extract('employees')
customers_df = extract('customers')
orders_consolidated_df = extract('orders_con')


###################
#### Transform ####
###################


#### Fact Table

#Create order code
orders_df['order_code'] = orders_df.order_number.map(str) + orders_df.order_line_number.map(str)
#Check uniqueness
orders_df.order_code.nunique() == len(orders_df)

#Add the price at which each product sold was bought
orders_df = pd.merge(orders_df, products_df[['buy_price', 'product_code']], on = 'product_code', how = 'left')

#Pre-compute the profit for each order line
orders_df['profit'] = orders_df.quantity_ordered * (orders_df.price_each - orders_df.buy_price) 

#Add date into the table
orders_df = pd.merge(orders_df, orders_consolidated_df[['order_number', 'order_date']], on = 'order_number', how = 'left')

#Add the employee that acted as sales representative for the order line
orders_df = pd.merge(orders_df, customers_df[['customer_number', 'sales_rep_employee_number']], on = 'customer_number', how = 'left')

#Add the office in charged of the order line
orders_df = pd.merge(orders_df, employees_df[['employee_number', 'office_code']], how = 'left', left_on = ['sales_rep_employee_number'], right_on = ['employee_number'])

#Re arrange the order of the columns and delete unnecessary ones
orders_df = orders_df[['order_code', 'quantity_ordered', 'price_each', 'buy_price', 'profit' ,'product_code', 'order_number' ,'customer_number', 'order_date', 'office_code', 'employee_number']]

#### Dimension tables

#Employees
employees_df = employees_df[['employee_number', 'last_name', 'first_name']]

#Customers
customers_df = customers_df[['customer_number', 'country', 'city']]

#Offices
offices_df = offices_df[['office_code', 'country', 'city']]

#Dates
dates_df = pd.DataFrame(orders_consolidated_df.order_date.unique(), columns = ['order_date'])
dates_df['order_date']= pd.to_datetime(dates_df.order_date, format = '%Y-%m-%d')
 
dates_df['year'] = dates_df.order_date.dt.year
dates_df['quarter'] = dates_df.order_date.dt.quarter
dates_df['month'] = dates_df.order_date.dt.month
dates_df['weekday'] = dates_df.order_date.dt.weekday_name


##############
#### Load ####
##############

#Create engine to connect to the database using Postgres
engine = create_engine('postgresql://postgres:@localhost:5432/analytics_db')

#### Dimension tables
employees_df.to_sql('employees', engine , if_exists='append', index=False)
customers_df.to_sql('customers', engine , if_exists='append', index=False)
offices_df.to_sql('offices', engine , if_exists='append', index=False)
dates_df.to_sql('dates', engine , if_exists='append', index=False)

#### Fact Table: order_lines
orders_df.to_sql('order_lines', engine , if_exists='append', index=False)
