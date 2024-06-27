-- Select all records from a table
SELECT * FROM table_name;
-----------------------------------------------------------

-- Select specific columns from a table
SELECT column1, column2 FROM table_name;
-----------------------------------------------------------

-- Insert a new record into a table
INSERT INTO table_name (column1, column2) VALUES (value1, value2);
-----------------------------------------------------------

-- Create a new table
CREATE TABLE new_table (column1 datatype, column2 datatype);

-- Add a column to an existing table
ALTER TABLE table_name ADD column_name datatype;

-- Drop a table
DROP TABLE table_name;

-- Drop a column from a table
ALTER TABLE table_name DROP COLUMN column_name;

-- Select distinct values from a column
SELECT DISTINCT column_name FROM table_name;

-- Count the number of records in a table
SELECT COUNT(*) FROM table_name;

-- Calculate the sum of a column
SELECT SUM(column_name) FROM table_name;

-- Calculate the average of a column
SELECT AVG(column_name) FROM table_name;

-- Find the minimum value in a column
SELECT MIN(column_name) FROM table_name;

-- Find the maximum value in a column
SELECT MAX(column_name) FROM table_name;

-- Group by aggregation
SELECT column1, SUM(column2) FROM table_name GROUP BY column1;

-- Join tables
SELECT * FROM table1 JOIN table2 ON table1.column_name = table2.column_name;

-- Order by ascending
SELECT * FROM employees ORDER BY salary ASC;

-- Order by descending
SELECT * FROM products ORDER BY price DESC;

-- Union query
SELECT column1 FROM table1 UNION SELECT column2 FROM table2;

-- Full outer join
SELECT * FROM table1 FULL OUTER JOIN table2 ON table1.column_name = table2.column_name;

-- Check if a table exists
SELECT name FROM sqlite_master WHERE type='table' AND name='table_name';

-- Delete all records from a table
DELETE FROM table_name;

-- Create an index on a column
CREATE INDEX idx_column_name ON table_name (column_name);

-- Drop an index
DROP INDEX idx_column_name;

-- Rename a table
-- ALTER TABLE old_table_name RENAME TO new_table_name;

-- Backup a table
-- CREATE TABLE backup_table AS SELECT * FROM table_name;

-- Truncate a table (delete all rows without logging)
DELETE FROM table_name;

-- Concatenate columns
SELECT CONCAT(column1, ' ', column2) AS concatenated_column FROM table_name;

-- Extract year from a date column
SELECT EXTRACT(YEAR FROM date_column) AS year FROM table_name;

-- Check for NULL values in a column
SELECT * FROM table_name WHERE column_name IS NULL;

-- Check for NOT NULL values in a column
SELECT * FROM table_name WHERE column_name IS NOT NULL;

-- Calculate a running total
SELECT column1, SUM(column2) OVER (ORDER BY column1) AS running_total FROM table_name;

-- Find duplicate rows
SELECT column1, column2, COUNT(*) FROM table_name GROUP BY column1, column2 HAVING COUNT(*) > 1;

-- Calculate percentile
SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY column_name) OVER () AS median_value FROM table_name;

-- Calculate cumulative sum
SELECT column1, SUM(column2) OVER (ORDER BY column1 ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum FROM table_name;

-- Generate row numbers
SELECT ROW_NUMBER() OVER (ORDER BY column_name) AS row_num, * FROM table_name;

-- Get current timestamp
SELECT CURRENT_TIMESTAMP;

-- Return unique values from a column
SELECT DISTINCT column_name FROM table_name;

-- Find the length of a string column
SELECT column1, LENGTH(column2) AS string_length FROM table_name;

-- Return rows with values in a list
SELECT * FROM table_name WHERE column_name IN (value1, value2, value3);

-- Return rows with values not in a list
SELECT * FROM table_name WHERE column_name NOT IN (value1, value2, value3);
