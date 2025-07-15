CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(255),
    email VARCHAR(255),
    password_hash VARCHAR(255),
    created_at DATETIME
);

CREATE TABLE speeches (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    title VARCHAR(255),
    created_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE questions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    speech_id INT,
    question_text TEXT,
    options JSON,
    answer VARCHAR(255),
    created_at DATETIME,
    FOREIGN KEY (speech_id) REFERENCES speeches(id)
);
