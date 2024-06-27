-- SQL commands to create a test table if not exists
CREATE TABLE template (
    id INTEGER PRIMARY KEY,
    name TEXT,
    age INTEGER
);

-- Insert initial data into the test table
INSERT INTO template (name, age) VALUES
    ('John Doe', 30),
    ('Jane Smith', 25),
    ('Michael Brown', 40);