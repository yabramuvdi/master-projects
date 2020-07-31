--- Get the top 3 product types that have proven most profitable
SELECT product_code, profit 
FROM order_lines 
ORDER BY profit DESC 
LIMIT 3;

--- Get the top 3 products by most items sold
SELECT product_code, quantity_ordered 
FROM order_lines 
ORDER BY quantity_ordered DESC 
LIMIT 3;

--- Get the top 3 products by items sold per country of customer for: USA, Spain, Belgium
(SELECT product_code, SUM(quantity_ordered) As q_per_country, country
FROM order_lines 
INNER JOIN customers 
ON order_lines.customer_number = customers.customer_number 
WHERE customers.country = 'USA' 
GROUP BY product_code, country
ORDER BY q_per_country DESC
LIMIT 3)
UNION
(SELECT product_code, SUM(quantity_ordered) As q_per_country, country
FROM order_lines 
INNER JOIN customers 
ON order_lines.customer_number = customers.customer_number 
WHERE customers.country = 'Spain' 
GROUP BY product_code, country
ORDER BY q_per_country DESC
LIMIT 3)
UNION
(SELECT product_code, SUM(quantity_ordered) As q_per_country, country
FROM order_lines 
INNER JOIN customers 
ON order_lines.customer_number = customers.customer_number 
WHERE customers.country = 'Belgium' 
GROUP BY product_code, country
ORDER BY q_per_country DESC
LIMIT 3)
ORDER BY country, q_per_country DESC;

--- Get the most profitable day of the week
SELECT SUM(profit) AS total_profit, weekday 
FROM order_lines 
INNER JOIN dates 
ON order_lines.order_date = dates.order_date 
GROUP BY weekday
ORDER BY total_profit DESC
LIMIT 1; 

--- Get the top 3 city-quarters with the highest average profit margin in their sales
SELECT AVG(profit) AS av_profit, city, quarter
FROM order_lines
INNER JOIN offices
ON order_lines.office_code = officeS.office_code
INNER JOIN dates 
ON order_lines.order_date = dates.order_date
GROUP BY city, quarter
ORDER BY av_profit DESC 
LIMIT 3;

-- List the employees who have sold more goods (in $ amount) than the average employee.
SELECT SUM(price_each * quantity_ordered) AS total_sales, employee_number
FROM order_lines
GROUP BY employee_number
HAVING SUM(price_each * quantity_ordered) > (SELECT AVG(subquery1.total_sales) AS av_sales FROM (SELECT SUM(price_each * quantity_ordered) AS total_sales, employee_number FROM order_lines GROUP BY employee_number) AS subquery1)
ORDER BY total_sales DESC;

-- TEST: Just to test my previous result lets see the complete table before filtering
SELECT SUM(price_each * quantity_ordered) AS total_sales, employee_number
FROM order_lines
GROUP BY employee_number
ORDER BY total_sales DESC;

-- List all the orders where the sales amount in the order is in the top 10% of all order sales amounts (BONUS: Add the employee number)
SELECT SUM(quantity_ordered) AS total_quantity, order_number, employee_number
FROM order_lines
GROUP BY order_number, employee_number
ORDER BY total_quantity DESC
LIMIT (SELECT COUNT(DISTINCT(order_number)) * 0.1 FROM order_lines);


