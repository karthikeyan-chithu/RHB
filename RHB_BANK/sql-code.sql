create database rhb;
use rhb;

CREATE TABLE customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    date_of_birth DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE accounts (
    account_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    card_number VARCHAR(16) UNIQUE NOT NULL,
    card_type ENUM('Visa', 'MasterCard', 'Amex') NOT NULL,
    credit_limit DECIMAL(10,2),
    balance DECIMAL(10,2),
    opened_date DATE,
    status ENUM('Active', 'Closed', 'Suspended') DEFAULT 'Active',
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
CREATE TABLE transactions (
    transaction_id INT PRIMARY KEY AUTO_INCREMENT,
    account_id INT NOT NULL,
    transaction_date DATETIME,
    merchant_name VARCHAR(100),
    category VARCHAR(50),
    amount DECIMAL(10,2),
    currency VARCHAR(10) DEFAULT 'MYR',
    description TEXT,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);
CREATE TABLE rewards (
    reward_id INT PRIMARY KEY AUTO_INCREMENT,
    account_id INT NOT NULL,
    reward_points INT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);


INSERT INTO customers (full_name, email, phone, address, date_of_birth)
VALUES 
('Alice Tan', 'alice.tan@example.com', '0123456789', '123 Jalan Ampang, Kuala Lumpur', '1990-05-20'),
('John Lee', 'john.lee@example.com', '0198765432', '88 Jalan Tun Razak, Kuala Lumpur', '1985-08-15');
INSERT INTO accounts (customer_id, card_number, card_type, credit_limit, balance, opened_date)
VALUES 
(1, '4567123412341234', 'Visa', 10000.00, 3500.50, '2021-04-01'),
(2, '5432123412341234', 'MasterCard', 15000.00, 7800.00, '2022-01-10');
-- Transactions for Alice (account_id = 1)
INSERT INTO transactions (account_id, transaction_date, merchant_name, category, amount, description)
VALUES 
(1, '2025-04-01 10:15:00', 'Shopee', 'Online Shopping', 150.00, 'Electronics purchase'),
(1, '2025-04-02 14:20:00', 'Starbucks', 'Food & Beverage', 18.50, 'Latte and muffin'),
(1, '2025-04-03 09:00:00', 'Petronas', 'Fuel', 90.00, 'Petrol refill'),
(1, '2025-04-05 20:30:00', 'Lazada', 'Online Shopping', 250.75, 'Fashion items'),
(1, '2025-04-06 16:45:00', 'Watsons', 'Health & Beauty', 72.90, 'Skincare products');

-- Transactions for John (account_id = 2)
INSERT INTO transactions (account_id, transaction_date, merchant_name, category, amount, description)
VALUES 
(2, '2025-04-01 12:10:00', 'Giant', 'Groceries', 320.20, 'Weekly grocery shopping'),
(2, '2025-04-02 18:50:00', 'McDonalds', 'Food & Beverage', 25.90, 'Dinner combo meal'),
(2, '2025-04-04 15:30:00', 'Zalora', 'Clothing', 180.00, 'Shirt and pants'),
(2, '2025-04-06 10:00:00', 'Tesco', 'Groceries', 215.45, 'Monthly essentials'),
(2, '2025-04-07 21:10:00', 'TGV Cinemas', 'Entertainment', 45.00, 'Movie tickets');

INSERT INTO rewards (account_id, reward_points)
VALUES 
(1, 1200),
(2, 2050);

