-- Creates a small table with three values

USE cyberrange;

CREATE TABLE users 
(
ID INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
uuid VARCHAR(128),
email VARCHAR(128),
emailid VARCHAR(128),
gtoken VARCHAR(128)
);

CREATE TABLE status
(
ID INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
labnumber VARCHAR(32),    
grade FLOAT(3, 2)
);
