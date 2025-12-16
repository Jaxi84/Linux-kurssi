CREATE DATABASE IF NOT EXISTS weatherdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE weatherdb;

CREATE TABLE IF NOT EXISTS weather_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    temperature DECIMAL(5,2) NOT NULL,
    description VARCHAR(200),
    timestamp DATETIME NOT NULL,
    INDEX (city),
    INDEX (timestamp)
);
