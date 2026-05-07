CREATE DATABASE IF NOT EXISTS `phase2-mysql-database`;
USE `phase2-mysql-database`;

CREATE TABLE IF NOT EXISTS users (
    user_id INT NOT NULL AUTO_INCREMENT,
    username VARCHAR(20) UNIQUE,
    password VARCHAR(20),
    role VARCHAR(30),
    PRIMARY KEY (user_id)
);

CREATE TABLE IF NOT EXISTS tables (
    table_id INT NOT NULL AUTO_INCREMENT,
    table_num VARCHAR(10) UNIQUE,
    user_id INT,
    available_seats INT DEFAULT 0,
    PRIMARY KEY (table_id)
);

CREATE TABLE IF NOT EXISTS claims (
    claim_id INT NOT NULL AUTO_INCREMENT,
    user_id INT,
    table_id INT,
    PRIMARY KEY (claim_id),
    UNIQUE KEY unique_user_claim (user_id)
);

INSERT INTO users (username, password, role)
VALUES ('admin', 'admin', 'Admin')
ON DUPLICATE KEY UPDATE username = username;