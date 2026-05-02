-- Users table
CREATE TABLE users (
    user_id NUMBER PRIMARY KEY,
    username VARCHAR2(50) UNIQUE NOT NULL,
    password VARCHAR2(100) NOT NULL,
    full_name VARCHAR2(100)
);

-- Categories table
CREATE TABLE categories (
    cat_id NUMBER PRIMARY KEY,
    cat_name VARCHAR2(50) NOT NULL,
    cat_type VARCHAR2(10) CHECK (cat_type IN ('income','expense'))
);

-- Transactions table
CREATE TABLE transactions (
    trans_id NUMBER PRIMARY KEY,
    user_id NUMBER NOT NULL,
    cat_id NUMBER NOT NULL,
    amount NUMBER(10,2) NOT NULL CHECK (amount > 0),
    trans_date DATE DEFAULT SYSDATE,
    note VARCHAR2(200),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (cat_id) REFERENCES categories(cat_id)
);

-- Sequences (for Oracle 11g)
CREATE SEQUENCE users_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE categories_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE transactions_seq START WITH 1 INCREMENT BY 1;

-- Triggers for auto-increment
CREATE OR REPLACE TRIGGER users_trigger
BEFORE INSERT ON users FOR EACH ROW
BEGIN SELECT users_seq.NEXTVAL INTO :NEW.user_id FROM DUAL; END;
/

CREATE OR REPLACE TRIGGER categories_trigger
BEFORE INSERT ON categories FOR EACH ROW
BEGIN SELECT categories_seq.NEXTVAL INTO :NEW.cat_id FROM DUAL; END;
/

CREATE OR REPLACE TRIGGER transactions_trigger
BEFORE INSERT ON transactions FOR EACH ROW
BEGIN SELECT transactions_seq.NEXTVAL INTO :NEW.trans_id FROM DUAL; END;
/

-- Insert default categories
INSERT INTO categories (cat_name, cat_type) VALUES ('Salary', 'income');
INSERT INTO categories (cat_name, cat_type) VALUES ('Freelance', 'income');
INSERT INTO categories (cat_name, cat_type) VALUES ('Gift', 'income');
INSERT INTO categories (cat_name, cat_type) VALUES ('Pocket Money', 'income');
INSERT INTO categories (cat_name, cat_type) VALUES ('Food', 'expense');
INSERT INTO categories (cat_name, cat_type) VALUES ('Transport', 'expense');
INSERT INTO categories (cat_name, cat_type) VALUES ('Shopping', 'expense');
INSERT INTO categories (cat_name, cat_type) VALUES ('Bills', 'expense');
INSERT INTO categories (cat_name, cat_type) VALUES ('Entertainment', 'expense');
INSERT INTO categories (cat_name, cat_type) VALUES ('Medical', 'expense');
COMMIT;