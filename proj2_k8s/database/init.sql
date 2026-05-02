CREATE DATABASE IF NOT EXISTS `phase2-mysql-database`;
USE `phase2-mysql-database`;

CREATE TABLE users (
    user_id INT NOT NULL AUTO_INCREMENT,
    username VARCHAR(20),
    password VARCHAR(20),
    role VARCHAR(30),
    PRIMARY KEY (user_id)
);

CREATE TABLE tables (
    table_id INT NOT NULL AUTO_INCREMENT,
    table_num INT,
    user_id INT,
    available_seats INT,
    PRIMARY KEY (table_id)
);

CREATE TABLE claims (
    claim_id INT NOT NULL AUTO_INCREMENT,
    user_id INT,
    table_id INT,
    PRIMARY KEY (claim_id)
);