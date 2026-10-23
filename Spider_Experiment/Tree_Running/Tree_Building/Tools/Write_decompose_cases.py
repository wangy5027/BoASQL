import re
import json
import os

current_file_path = os.path.dirname(os.path.abspath(__file__))
cases_file = os.path.join(current_file_path, 'Decompose_cases.json')

data1 = {
    'filtering': 1,
    'multiple tables joining' : 1,
    'father task': "I want to see the open price of stock 000002 at the day of 2022-10-11, and also its factor_1 data at that day.",
    'children tasks':["1. Join the table 'stock_data','factor_1' on the 'stock_id' column.","2. Select the 'open price', 'data' columns from the joined table where time = '2022-10-11'."]
}

data2 = {
    'multiple tables joining': 1,
    'father task': "Join the 'factor_1', 'factor_2', 'factor_3', 'factor_4', 'factor_5' on the 'stock_id' column.",
    'children tasks':["1. Join the table 'factor_1', 'factor_2', 'factor_3' on the 'stock_id' column.",
                      "2. Join the table of 1 with the tables 'factor_4', 'factor_5' on the 'stock_id' column."]
}
data3 = {
  "filtering": 1,
  "aggregating": 1,
  "father task": "Find the total revenue generated from sales in the 'Electronics' category during 2022.",
  "children tasks": [
    "1. Filter the 'sales' table to include records from the 'Electronics' category and the year 2022.",
    "2. Aggregate these records to calculate the total revenue."
  ]
}
data4 = {
  "filtering": 1,
  "sorting": 1,
  "father task": "I need to find the top 5 employees by sales in March 2021.",
  "children tasks": [
    "1. Filter the 'employee_sales' table to include only sales made in March 2021.",
    "2. Sort the filtered results by 'sales_amount' in descending order and select the top 5 records."
  ]
}
data5 = {
  "grouping": 1,
  "filtering": 1,
  "indexing": 1,
  "father task": "Identify the most popular product in each category for the year 2022 and ensure efficient querying by creating an index.",
  "children tasks": [
    "1. Filter the 'sales_data' table for records in the year 2022.",
    "2. Group the filtered data by 'product_category' and aggregate to find the product with the highest sales in each category.",
    "3. Create an index on the 'product_category' and 'sales' columns to optimize the query."
  ]
}
data6 = {
  "merging": 1,
  "partitioning": 1,
  "father task": "Merge quarterly sales data into a single table and partition it by quarter for faster data retrieval.",
  "children tasks": [
    "1. Merge the 'Q1_sales', 'Q2_sales', 'Q3_sales', and 'Q4_sales' tables into a single 'yearly_sales' table.",
    "2. Partition the 'yearly_sales' table by the 'quarter' column."
  ]
}
data7 = {
  "multiple tables joining": 1,
  "sorting": 1,
  "father task": "List the top 10 products by sales quantity in 2022, including product details from a separate product information table.",
  "children tasks": [
    "1. Join the 'sales' table with the 'product_info' table on the 'product_id' column to combine sales data with product details.",
    "2. Sort the result by 'sales_quantity' in descending order and select the top 10."
  ]
}
data = {
    "data1": data1, 
    "data2": data2,
    "data3": data3,
    "data4": data4,
    "data5": data5,
    "data6": data6,
    "data7": data7
}

json_data = json.dumps(data,indent=4)

with open(cases_file, 'w') as file:
    file.write(json_data)