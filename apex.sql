-- =============================================
-- 1. DATABASE INITIALIZATION
-- =============================================
CREATE DATABASE IF NOT EXISTS ApexFinancialSentinel;
USE ApexFinancialSentinel;

-- =============================================
-- 2. TABLE STRUCTURES (Clean Slate)
-- =============================================

-- We drop child tables first to avoid Foreign Key constraint errors
DROP TABLE IF EXISTS Deleted_Transactions_Log;
DROP TABLE IF EXISTS Transactions;
DROP TABLE IF EXISTS CurrencyExchange;
DROP TABLE IF EXISTS Users;

CREATE TABLE Users (
    SSN VARCHAR(15) PRIMARY KEY,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    PasswordHash VARCHAR(255) NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE CurrencyExchange (
    CurrencyCode VARCHAR(3) PRIMARY KEY,
    RateToPKR DECIMAL(10, 4) NOT NULL
);

-- Resetting basic rates
INSERT INTO CurrencyExchange (CurrencyCode, RateToPKR) 
VALUES ('USD', 278.50), ('EUR', 300.15), ('PKR', 1.00);

CREATE TABLE Transactions (
    TransactionID INT AUTO_INCREMENT PRIMARY KEY,
    SSN VARCHAR(15),
    CurrencyCode VARCHAR(3),
    AmountUser DECIMAL(15, 2) NOT NULL, 
    AmountBase DECIMAL(15, 2) NOT NULL, 
    Type ENUM('Income', 'Expense') NOT NULL,
    Category VARCHAR(50),
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (SSN) REFERENCES Users(SSN) ON DELETE CASCADE,
    FOREIGN KEY (CurrencyCode) REFERENCES CurrencyExchange(CurrencyCode)
);

CREATE TABLE Deleted_Transactions_Log (
    LogID INT AUTO_INCREMENT PRIMARY KEY,
    Original_TransactionID INT,
    SSN VARCHAR(15),
    Category VARCHAR(50),
    AmountBase DECIMAL(15, 2),
    DeletedBy_SSN VARCHAR(15),
    DeletedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- 3. STORED PROCEDURES
-- =============================================
DELIMITER //

DROP PROCEDURE IF EXISTS SecureSignup //
CREATE PROCEDURE SecureSignup(
    IN p_SSN VARCHAR(15), 
    IN p_FirstName VARCHAR(50), 
    IN p_LastName VARCHAR(50), 
    IN p_Email VARCHAR(100), 
    IN p_PassHash VARCHAR(255)
)
BEGIN
    IF p_SSN REGEXP '[a-zA-Z]' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Security Violation: ID must be numeric.';
    ELSEIF p_Email NOT LIKE '%_@__%.__%' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Alert: Invalid Email Format.';
    ELSEIF EXISTS (SELECT 1 FROM Users WHERE SSN = p_SSN OR Email = p_Email) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Alert: SSN or Email already registered.';
    ELSE
        INSERT INTO Users (SSN, FirstName, LastName, Email, PasswordHash)
        VALUES (p_SSN, p_FirstName, p_LastName, p_Email, p_PassHash);
    END IF;
END //

DROP PROCEDURE IF EXISTS ProcessRapidTransaction //
CREATE PROCEDURE ProcessRapidTransaction(
    IN p_SSN VARCHAR(15),
    IN p_FName VARCHAR(50),
    IN p_LName VARCHAR(50),
    IN p_Email VARCHAR(100),
    IN p_PassHash VARCHAR(255),
    IN p_Currency VARCHAR(3),
    IN p_AmountUser DECIMAL(15,2),
    IN p_Type ENUM('Income', 'Expense'),
    IN p_Category VARCHAR(50)
)
BEGIN
    DECLARE current_rate DECIMAL(10,4);
    START TRANSACTION;
    INSERT IGNORE INTO Users (SSN, FirstName, LastName, Email, PasswordHash)
    VALUES (p_SSN, p_FName, p_LName, p_Email, p_PassHash);
    
    SELECT RateToPKR INTO current_rate FROM CurrencyExchange WHERE CurrencyCode = p_Currency;
    
    IF current_rate IS NOT NULL THEN
        INSERT INTO Transactions (SSN, CurrencyCode, AmountUser, AmountBase, Type, Category)
        VALUES (p_SSN, p_Currency, p_AmountUser, (p_AmountUser * current_rate), p_Type, p_Category);
        COMMIT;
    ELSE
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Currency Rate Not Found';
    END IF;
END //

DROP PROCEDURE IF EXISTS GetUserTransactions //
CREATE PROCEDURE GetUserTransactions(IN p_SSN VARCHAR(15))
BEGIN
    SELECT * FROM Transactions WHERE SSN = p_SSN;
END //

DROP PROCEDURE IF EXISTS SecureDeleteTransaction //
CREATE PROCEDURE SecureDeleteTransaction(IN input_TransID INT, IN input_SSN VARCHAR(15))
BEGIN
    DELETE FROM Transactions 
    WHERE TransactionID = input_TransID AND SSN = input_SSN;
    IF ROW_COUNT() = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Unauthorized Deletion Attempt.';
    END IF;
END //

DROP PROCEDURE IF EXISTS DeleteLastUserTransaction //
CREATE PROCEDURE DeleteLastUserTransaction(IN p_SSN VARCHAR(15))
BEGIN
    DECLARE target_id INT;
    SET target_id = (SELECT TransactionID FROM Transactions 
                      WHERE SSN = p_SSN 
                      ORDER BY CreatedAt DESC LIMIT 1);
    IF target_id IS NOT NULL THEN
        CALL SecureDeleteTransaction(target_id, p_SSN);
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No transactions found.';
    END IF;
END //

DROP PROCEDURE IF EXISTS BulkDeleteUserTransactions //
CREATE PROCEDURE BulkDeleteUserTransactions(IN input_SSN VARCHAR(15))
BEGIN
    DELETE FROM Transactions WHERE SSN = input_SSN;
END //

DELIMITER ;

-- =============================================
-- 4. TRIGGERS
-- =============================================
DELIMITER //

DROP TRIGGER IF EXISTS Before_User_Registration //
CREATE TRIGGER Before_User_Registration
BEFORE INSERT ON Users
FOR EACH ROW
BEGIN
    SET NEW.FirstName = UPPER(NEW.FirstName);
    SET NEW.LastName = UPPER(NEW.LastName);
    SET NEW.Email = LOWER(NEW.Email);
END //

DROP TRIGGER IF EXISTS Archive_On_Delete //
CREATE TRIGGER Archive_On_Delete
BEFORE DELETE ON Transactions
FOR EACH ROW
BEGIN
    INSERT INTO Deleted_Transactions_Log (
        Original_TransactionID, SSN, Category, AmountBase, DeletedBy_SSN, DeletedAt
    )
    VALUES (
        OLD.TransactionID, OLD.SSN, OLD.Category, OLD.AmountBase, 'UI_USER', NOW()
    );
END //

DELIMITER ;

-- =============================================
-- 5. ANALYTICAL VIEWS
-- =============================================

CREATE OR REPLACE VIEW Global_Financial_Stats AS
SELECT
    Class_Boundary,
    Frequency,
    Midpoint,
    SUM(Frequency) OVER (ORDER BY Midpoint ASC) AS Cumulative_Frequency
FROM (
    SELECT 
        CASE 
            WHEN (AmountBase) BETWEEN 0 AND 10000 THEN '0 - 10k PKR'
            WHEN (AmountBase) BETWEEN 10001 AND 20000 THEN '10k - 20k PKR'
            WHEN (AmountBase) BETWEEN 20001 AND 30000 THEN '20k - 30k PKR'
            WHEN (AmountBase) BETWEEN 30001 AND 40000 THEN '30k - 40k PKR'
            ELSE '40k+ PKR' 
        END AS Class_Boundary,
        COUNT(*) AS Frequency,
        CASE 
            WHEN (AmountBase) BETWEEN 0 AND 10000 THEN 5000
            WHEN (AmountBase) BETWEEN 10001 AND 20000 THEN 15000
            WHEN (AmountBase) BETWEEN 20001 AND 30000 THEN 25000
            WHEN (AmountBase) BETWEEN 30001 AND 40000 THEN 35000
            ELSE 45000 
        END AS Midpoint
    FROM Transactions
    GROUP BY Class_Boundary, Midpoint
) AS StatisticalTable;