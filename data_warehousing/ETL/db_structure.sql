DROP DATABASE analytics_db;
CREATE DATABASE analytics_db;
\c analytics_db;

/*------------------------------------
---- Create the Dimensions Tables ---- 
*/------------------------------------

CREATE TABLE employees(
	employee_number INTEGER PRIMARY KEY,
	first_name VARCHAR,
	last_name VARCHAR
);

CREATE TABLE customers(
	customer_number INTEGER PRIMARY KEY,
	country VARCHAR,
	city VARCHAR
);

CREATE TABLE offices(
	office_code INTEGER PRIMARY KEY,
	country VARCHAR,
	city VARCHAR
);

CREATE TABLE dates(
	order_date DATE PRIMARY KEY,
	year INTEGER,
	quarter INTEGER,
	month INTEGER,
	weekday VARCHAR
);


/*------------------------------
---- Create the Facts Table ---- 
*/------------------------------

CREATE TABLE order_lines (
	--Measures
	order_code INTEGER PRIMARY KEY,
	quantity_ordered INTEGER NOT NULL,
	price_each NUMERIC NOT NULL,
	buy_price NUMERIC NOT NULL,
	profit NUMERIC NOT NULL,
	product_code VARCHAR NOT NULL,
	order_number INTEGER NOT NULL,
	--Keys for joining with dimensions
	customer_number INTEGER REFERENCES customers(customer_number),
	order_date DATE REFERENCES dates(order_date),
	office_code INTEGER REFERENCES offices (office_code),
	employee_number INTEGER REFERENCES employees(employee_number)
);
