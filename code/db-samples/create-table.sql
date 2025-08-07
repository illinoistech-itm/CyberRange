-- Creates a small table with three values

USE cyberrange;

CREATE TABLE users 
(
ID INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
uuid VARCHAR(128),
email VARCHAR(128),
email_id VARCHAR(128),
g_token VARCHAR(128),
created_at TIMESTAMP
);

CREATE TABLE status
(
ID INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
lab_number VARCHAR(32),    
grade FLOAT(3, 2),
created_at TIMESTAMP
);
