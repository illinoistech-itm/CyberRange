-- Creates the Cyber Range schema
-- Use UUID compared to an auto increment ID
-- https://copilot.microsoft.com/shares/53BbT7TZNsNYKvGZi2k9z


USE cyberrange;

CREATE TABLE users 
(
id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
email VARCHAR(128),
email_id VARCHAR(128),
g_token VARCHAR(128),
created_at TIMESTAMP
);

CREATE TABLE labs
(
id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
-- In MySQL, there isn't a native BOOLEAN data type. Instead, BOOLEAN is 
-- treated as a synonym for TINYINT(1), where 0 represents FALSE and 1
-- represents TRUE.
lab_number INT(10),
question_one_passing_indicator TINYINT(1) DEFAULT 0,
question_two_passing_indicator TINYINT(1) DEFAULT 0,
question_three_passing_indicator TINYINT(1) DEFAULT 0,
question_four_passing_indicator TINYINT(1) DEFAULT 0,
grades FLOAT(3,2),
last_update TIMESTAMP
);
