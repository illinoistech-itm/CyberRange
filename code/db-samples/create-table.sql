-- Creates the Cyber Range schema
-- Use UUID compared to an auto increment ID
-- https://copilot.microsoft.com/shares/53BbT7TZNsNYKvGZi2k9z
-- https://copilot.microsoft.com/shares/1X4Dh2AQFfoHt3aAYLyoJ

USE cyrange;

CREATE TABLE users 
(
email VARCHAR(128) PRIMARY KEY,
id CHAR(36) DEFAULT (UUID()),
last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
admin_status TINYINT(1) DEFAULT 0
);

CREATE TABLE labs
(
id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
-- In MySQL, there isn't a native BOOLEAN data type. Instead, BOOLEAN is 
-- treated as a synonym for TINYINT(1), where 0 represents FALSE and 1
-- represents TRUE.
lab_number INT(10) DEFAULT 1,
question_one_passing_indicator TINYINT(1) DEFAULT 0,
question_two_passing_indicator TINYINT(1) DEFAULT 0,
question_three_passing_indicator TINYINT(1) DEFAULT 0,
question_four_passing_indicator TINYINT(1) DEFAULT 0,
grade FLOAT(3,2),
lab_complete TINYINT(1) DEFAULT 0,
last_attempt TIMESTAMP,
email VARCHAR(128),
FOREIGN KEY (email) REFERENCES users(email)
);

CREATE TABLE lab_two
(
id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
-- In MySQL, there isn't a native BOOLEAN data type. Instead, BOOLEAN is 
-- treated as a synonym for TINYINT(1), where 0 represents FALSE and 1
-- represents TRUE.
lab_number INT(10) DEFAULT 2,
question_one_passing_indicator TINYINT(1) DEFAULT 0,
question_two_passing_indicator TINYINT(1) DEFAULT 0,
question_three_passing_indicator TINYINT(1) DEFAULT 0,
question_four_passing_indicator TINYINT(1) DEFAULT 0,
grade FLOAT(3,2),
last_attempt TIMESTAMP,
email VARCHAR(128),
FOREIGN KEY (email) REFERENCES users(email)
);
