
import mysql.connector
import plotly.graph_objects as go
from mysql.connector import Error

class ApexFinancialSentinel:
    def __init__(self, host, user, password):
        self.config = {
            'host': host,
            'user': user,
            'password': password,
            'database': 'ApexFinancialSentinel',
            'auth_plugin': 'mysql_native_password'
        }

    def connect(self):
        try:
            return mysql.connector.connect(**self.config)
        except Error as e:
            print(f"Error: {e}")
            return None
    def initialize_system(self):
        """Builds the database infrastructure automatically."""
        conn = self.connect()
        if conn:
            try:
                cursor = conn.cursor()
                
                # 1. Create the Metrics View
                cursor.execute("""
                    CREATE OR REPLACE VIEW Admin_Dashboard_Metrics AS
                    SELECT 
                        (SELECT COUNT(*) FROM Users) AS Total_Registered_Users,
                        (SELECT COUNT(*) FROM Transactions) AS Total_System_Entries;
                """)

                # 2. Create the Search Procedure
                cursor.execute("DROP PROCEDURE IF EXISTS AdminSearchUser")
                cursor.execute("""
                    CREATE PROCEDURE AdminSearchUser(IN p_SearchTerm VARCHAR(100))
                    BEGIN
                        SELECT SSN, FirstName, LastName, Email, CreatedAt 
                        FROM Users 
                        WHERE SSN LIKE CONCAT('%', p_SearchTerm, '%')
                           OR FirstName LIKE CONCAT('%', p_SearchTerm, '%')
                           OR LastName LIKE CONCAT('%', p_SearchTerm, '%')
                           OR Email LIKE CONCAT('%', p_SearchTerm, '%');
                    END
                """)
                
                # 3. Optional: Add your Restore/Wipe procedures here too
                
                conn.commit()
            except Exception as e:
                print(f"Auto-Initialization Error: {e}")
                raise e # Pass the error back to Streamlit to display
            finally:
                conn.close()
    # ---------------- SIGNUP ----------------
    def signup_user(self, ssn, fname, lname, email, password_hash):
        conn = self.connect()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.callproc('StrictSignup', (ssn, fname, lname, email, password_hash))
                conn.commit()
            finally:
                conn.close()

    # ---------------- LOGIN ----------------
    def verify_login(self, ssn, password):
        conn = self.connect()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM Users WHERE SSN = %s AND PasswordHash = %s",
                    (ssn, password)
                )
                return cursor.fetchone() is not None
            finally:
                conn.close()
        return False

    # ---------------- TRANSACTION ----------------
    # ---------------- TRANSACTION ----------------
    def process_transaction(self, ssn, fname, lname, email, p_hash, currency, amount, t_type, category):
        """Processes a new transaction and commits it to the database."""
        conn = self.connect()
        if conn:
            try:
                cursor = conn.cursor()
                # Ensure these arguments match your 'ProcessRapidTransaction' stored procedure
                args = (ssn, fname, lname, email, p_hash, currency, amount, t_type, category)
                cursor.callproc('ProcessRapidTransaction', args)
                conn.commit()
                return True
            except Exception as e:
                print(f"Transaction Error: {e}")
                return False
            finally:
                conn.close()
        return False
    # ---------------- TRANSACTIONS ----------------
    
import mysql.connector
import plotly.graph_objects as go
from mysql.connector import Error

class ApexFinancialSentinel:
    def __init__(self, host, user, password):
        self.config = {
            'host': host,
            'user': user,
            'password': password,
            'database': 'ApexFinancialSentinel',
            'auth_plugin': 'mysql_native_password'
        }

    def connect(self):
        try:
            return mysql.connector.connect(**self.config)
        except Error as e:
            print(f"Error: {e}")
            return None
    def initialize_system(self):
        """Builds the database infrastructure automatically."""
        conn = self.connect()
        if conn:
            try:
                cursor = conn.cursor()
                
                # 1. Create the Metrics View
                cursor.execute("""
                    CREATE OR REPLACE VIEW Admin_Dashboard_Metrics AS
                    SELECT 
                        (SELECT COUNT(*) FROM Users) AS Total_Registered_Users,
                        (SELECT COUNT(*) FROM Transactions) AS Total_System_Entries;
                """)

                # 2. Create the Search Procedure
                cursor.execute("DROP PROCEDURE IF EXISTS AdminSearchUser")
                cursor.execute("""
                    CREATE PROCEDURE AdminSearchUser(IN p_SearchTerm VARCHAR(100))
                    BEGIN
                        SELECT SSN, FirstName, LastName, Email, CreatedAt 
                        FROM Users 
                        WHERE SSN LIKE CONCAT('%', p_SearchTerm, '%')
                           OR FirstName LIKE CONCAT('%', p_SearchTerm, '%')
                           OR LastName LIKE CONCAT('%', p_SearchTerm, '%')
                           OR Email LIKE CONCAT('%', p_SearchTerm, '%');
                    END
                """)
                
                # 3. Optional: Add your Restore/Wipe procedures here too
                
                conn.commit()
            except Exception as e:
                print(f"Auto-Initialization Error: {e}")
                raise e # Pass the error back to Streamlit to display
            finally:
                conn.close()
    # ---------------- SIGNUP ----------------
    def signup_user(self, ssn, fname, lname, email, password_hash):
        conn = self.connect()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.callproc('StrictSignup', (ssn, fname, lname, email, password_hash))
                conn.commit()
            finally:
                conn.close()

    # ---------------- LOGIN ----------------
    def verify_login(self, ssn, password):
        conn = self.connect()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM Users WHERE SSN = %s AND PasswordHash = %s",
                    (ssn, password)
                )
                return cursor.fetchone() is not None
            finally:
                conn.close()
        return False

    # ---------------- TRANSACTION ----------------
    # ---------------- TRANSACTION ----------------
    def process_transaction(self, ssn, fname, lname, email, p_hash, currency, amount, t_type, category):
        """Processes a new transaction and commits it to the database."""
        conn = self.connect()
        if conn:
            try:
                cursor = conn.cursor()
                # Ensure these arguments match your 'ProcessRapidTransaction' stored procedure
                args = (ssn, fname, lname, email, p_hash, currency, amount, t_type, category)
                cursor.callproc('ProcessRapidTransaction', args)
                conn.commit()
                return True
            except Exception as e:
                print(f"Transaction Error: {e}")
                return False
            finally:
                conn.close()
        return False
    # ---------------- TRANSACTIONS ----------------
    def get_user_transactions(self, ssn):
        conn = self.connect()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                # UPDATED: Pull AmountUser and CurrencyCode instead of just AmountBase
                cursor.execute("""
                    SELECT TransactionID, Type, Category, AmountUser, CurrencyCode, AmountBase, CreatedAt
                    FROM Transactions
                    WHERE SSN = %s
                    ORDER BY CreatedAt DESC
                """, (ssn,))
                return cursor.fetchall()
            finally:
                conn.close()
        return []

    # ---------------- BULK  DELETE  Transcation----------------
    def bulk_delete_transactions(self, ssn):
        conn = self.connect()
        if conn:
            try:
                cursor = conn.cursor()
                # Calls the procedure that targets the entire SSN record
                cursor.callproc('BulkDeleteUserTransactions', (ssn,))
                conn.commit()
                print(f"All records for {ssn} have been cleared and logged.")
                return True
            except Error as e:
                print(f"Error during bulk delete: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()
    ## ---- DLT last Transcation --##
    def delete_last_transaction(self, ssn):
        conn = self.connect()
        if conn:
            try:
                cursor = conn.cursor()
                # Calls the procedure that finds the latest CreatedAt for this SSN
                cursor.callproc('DeleteLastUserTransaction', (ssn,))
                conn.commit()
                print("Latest transaction removed successfully.")
                return True
            except Error as e:
                print(f"Error during undo: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()
    # ---------------- UPDATE TRANSACTION ----------------
    def update_transaction_amount(self, trans_id, ssn, new_amount):
        """Updates the amount of a specific transaction."""
        conn = self.connect()
        if conn:
            try:
                cursor = conn.cursor()
                # Assuming you have a procedure or direct SQL
                query = "UPDATE Transactions SET AmountBase = %s WHERE TransactionID = %s AND SSN = %s"
                cursor.execute(query, (new_amount, trans_id, ssn))
                conn.commit()
                return True
            except Error as e:
                print(f"Update Error: {e}")
                return False
            finally:
                conn.close()
        return False

    # ---------------- RESTORE DATA ----------------
    def restore_all_user_data(self, ssn):
        conn = self.connect()
        if conn:
            try:
                cursor = conn.cursor()
                # Use explicit column names to prevent "Column Mismatch" errors
                restore_sql = """
                    INSERT INTO Transactions (SSN, Type, Category, AmountBase, CreatedAt)
                    SELECT SSN, Type, Category, AmountBase, CreatedAt 
                    FROM Deleted_Transactions_Log 
                    WHERE SSN = %s
                """
                cursor.execute(restore_sql, (ssn,))
                
                # Only delete from log if the insert actually worked
                if cursor.rowcount > 0:
                    cursor.execute("DELETE FROM Deleted_Transactions_Log WHERE SSN = %s", (ssn,))
                    conn.commit()
                    return True
                return False 
            except Exception as e:
                print(f"Restore Error: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()
        return False
    # ---------------- HARD WIPE ----------------
    def hard_wipe_user_data(self, ssn):
        """Permanently deletes all records for a user from all tables."""
        conn = self.connect()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Transactions WHERE SSN = %s", (ssn,))
                cursor.execute("DELETE FROM Deleted_Transactions_Log WHERE SSN = %s", (ssn,))
                conn.commit()
                return True
            except Error as e:
                print(f"Wipe Error: {e}")
                return False
            finally:
                conn.close()
        return False

    # ---------------- FINANCIAL STATS ----------------
    def get_financial_stats(self, ssn, view_choice):
        conn = self.connect()
        if not conn:
            return None

        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT Category, SUM(AmountBase) AS total, AVG(AmountBase) as midpoint
                FROM Transactions
                WHERE SSN = %s AND Type = %s
                GROUP BY Category
            """, (ssn, view_choice))

            rows = cursor.fetchall()
            if not rows:
                return None

            categories = [r["Category"] for r in rows]
            totals = [float(r["total"]) for r in rows]

            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=categories,
                y=totals,
                marker=dict(
                    color=totals,
                    colorscale='Viridis',
                    showscale=True
                ),
                hovertemplate="<b>Category: %{x}</b><br>Total: %{y} PKR<extra></extra>"
            ))

            fig.update_layout(
                title=f"Live {view_choice} Grid Analytics",
                template="plotly_dark",
                xaxis=dict(showgrid=True, gridwidth=1, gridcolor='DimGray'),
                yaxis=dict(showgrid=True, gridwidth=1, gridcolor='DimGray'),
                bargap=0.1
            )

            return fig
        finally:
            conn.close()

    # ---------------- SUMMARY ----------------
    def get_summary(self, ssn):
        conn = self.connect()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT 
                        Type,
                        SUM(CASE WHEN MONTH(CreatedAt)=MONTH(CURRENT_DATE()) 
                            THEN AmountBase ELSE 0 END) as Current,
                        SUM(CASE WHEN MONTH(CreatedAt)=MONTH(CURRENT_DATE()-INTERVAL 1 MONTH) 
                            THEN AmountBase ELSE 0 END) as Previous
                    FROM Transactions
                    WHERE SSN = %s
                    GROUP BY Type
                """, (ssn,))
                return cursor.fetchall()
            finally:
                conn.close()

        return []
    def get_user_transactions(self, ssn):
        conn = self.connect()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                # Ensure AmountUser and CurrencyCode are included in the SELECT
                cursor.execute("""
                    SELECT TransactionID, Type, Category, AmountUser, CurrencyCode, AmountBase, CreatedAt
                    FROM Transactions
                    WHERE SSN = %s
                    ORDER BY CreatedAt DESC
                """, (ssn,))
                return cursor.fetchall()
            finally:
                conn.close()
        return []

    # ---------------- BULK  DELETE  Transcation----------------
    def bulk_delete_transactions(self, ssn):
        conn = self.connect()
        if conn:
            try:
                cursor = conn.cursor()
                # Calls the procedure that targets the entire SSN record
                cursor.callproc('BulkDeleteUserTransactions', (ssn,))
                conn.commit()
                print(f"All records for {ssn} have been cleared and logged.")
                return True
            except Error as e:
                print(f"Error during bulk delete: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()
    ## ---- DLT last Transcation --##
    def delete_last_transaction(self, ssn):
        conn = self.connect()
        if conn:
            try:
                cursor = conn.cursor()
                # Calls the procedure that finds the latest CreatedAt for this SSN
                cursor.callproc('DeleteLastUserTransaction', (ssn,))
                conn.commit()
                print("Latest transaction removed successfully.")
                return True
            except Error as e:
                print(f"Error during undo: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()

                # ---------------- SECURE DELETE (Targeted) ----------------
    def secure_delete_transaction(self, trans_id, ssn):
        conn = self.connect()
        if conn:
            try:
                cursor = conn.cursor()
                # 🔄 UPDATED NAME HERE TO v2
                cursor.callproc('SecureDeleteTransaction_v2', (trans_id, ssn))
                conn.commit()
                return True
            except Error as e:
                print(f"Deletion Error: {e}")
                return False
            finally:
                conn.close()
        return False
    # ---------------- ADMIN METRICS ----------------
    def get_admin_metrics(self):
        """Fetches data from the View created during initialization."""
        conn = self.connect()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                # This view is created in your initialize_system() method
                cursor.execute("SELECT * FROM Admin_Dashboard_Metrics")
                result = cursor.fetchone()
                return result if result else {'Total_Registered_Users': 0, 'Total_System_Entries': 0}
            except Exception as e:
                print(f"Metrics Error: {e}")
                return {'Total_Registered_Users': 0, 'Total_System_Entries': 0}
            finally:
                conn.close()
        return {'Total_Registered_Users': 0, 'Total_System_Entries': 0}

    # ---------------- ADMIN SEARCH ----------------
    def admin_search_user(self, search_term):
        """Calls the stored procedure for global user search."""
        conn = self.connect()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.callproc('AdminSearchUser', (search_term,))
                results = []
                for result in cursor.stored_results():
                    results.extend(result.fetchall())
                return results
            except Exception as e:
                print(f"Search Error: {e}")
                return []
            finally:
                conn.close()
        return []
     
     


    # ---------------- BULK  DELETE  Transcation----------------
    def bulk_delete_transactions(self, ssn):
        conn = self.connect()
        if conn:
            try:
                cursor = conn.cursor()
                # Calls the procedure that targets the entire SSN record
                cursor.callproc('BulkDeleteUserTransactions', (ssn,))
                conn.commit()
                print(f"All records for {ssn} have been cleared and logged.")
                return True
            except Error as e:
                print(f"Error during bulk delete: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()
    ## ---- DLT last Transcation --##
    def delete_last_transaction(self, ssn):
        conn = self.connect()
        if conn:
            try:
                cursor = conn.cursor()
                # Calls the procedure that finds the latest CreatedAt for this SSN
                cursor.callproc('DeleteLastUserTransaction', (ssn,))
                conn.commit()
                print("Latest transaction removed successfully.")
                return True
            except Error as e:
                print(f"Error during undo: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()
    # ---------------- UPDATE TRANSACTION ----------------
    def update_transaction_amount(self, trans_id, ssn, new_amount):
        """Updates the amount of a specific transaction."""
        conn = self.connect()
        if conn:
            try:
                cursor = conn.cursor()
                # Assuming you have a procedure or direct SQL
                query = "UPDATE Transactions SET AmountBase = %s WHERE TransactionID = %s AND SSN = %s"
                cursor.execute(query, (new_amount, trans_id, ssn))
                conn.commit()
                return True
            except Error as e:
                print(f"Update Error: {e}")
                return False
            finally:
                conn.close()
        return False

    # ---------------- RESTORE DATA ----------------
    def restore_all_user_data(self, ssn):
        conn = self.connect()
        if conn:
            try:
                cursor = conn.cursor()
                # Use explicit column names to prevent "Column Mismatch" errors
                restore_sql = """
                    INSERT INTO Transactions (SSN, Type, Category, AmountBase, CreatedAt)
                    SELECT SSN, Type, Category, AmountBase, CreatedAt 
                    FROM Deleted_Transactions_Log 
                    WHERE SSN = %s
                """
                cursor.execute(restore_sql, (ssn,))
                
                # Only delete from log if the insert actually worked
                if cursor.rowcount > 0:
                    cursor.execute("DELETE FROM Deleted_Transactions_Log WHERE SSN = %s", (ssn,))
                    conn.commit()
                    return True
                return False 
            except Exception as e:
                print(f"Restore Error: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()
        return False
    # ---------------- HARD WIPE ----------------
    def hard_wipe_user_data(self, ssn):
        """Permanently deletes all records for a user from all tables."""
        conn = self.connect()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Transactions WHERE SSN = %s", (ssn,))
                cursor.execute("DELETE FROM Deleted_Transactions_Log WHERE SSN = %s", (ssn,))
                conn.commit()
                return True
            except Error as e:
                print(f"Wipe Error: {e}")
                return False
            finally:
                conn.close()
        return False

    # ---------------- FINANCIAL STATS ----------------
    def get_financial_stats(self, ssn, view_choice):
        conn = self.connect()
        if not conn:
            return None

        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT Category, SUM(AmountBase) AS total, AVG(AmountBase) as midpoint
                FROM Transactions
                WHERE SSN = %s AND Type = %s
                GROUP BY Category
            """, (ssn, view_choice))

            rows = cursor.fetchall()
            if not rows:
                return None

            categories = [r["Category"] for r in rows]
            totals = [float(r["total"]) for r in rows]

            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=categories,
                y=totals,
                marker=dict(
                    color=totals,
                    colorscale='Viridis',
                    showscale=True
                ),
                hovertemplate="<b>Category: %{x}</b><br>Total: %{y} PKR<extra></extra>"
            ))

            fig.update_layout(
                title=f"Live {view_choice} Grid Analytics",
                template="plotly_dark",
                xaxis=dict(showgrid=True, gridwidth=1, gridcolor='DimGray'),
                yaxis=dict(showgrid=True, gridwidth=1, gridcolor='DimGray'),
                bargap=0.1
            )

            return fig
        finally:
            conn.close()

    # ---------------- SUMMARY ----------------
    def get_summary(self, ssn):
        conn = self.connect()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT 
                        Type,
                        SUM(CASE WHEN MONTH(CreatedAt)=MONTH(CURRENT_DATE()) 
                            THEN AmountBase ELSE 0 END) as Current,
                        SUM(CASE WHEN MONTH(CreatedAt)=MONTH(CURRENT_DATE()-INTERVAL 1 MONTH) 
                            THEN AmountBase ELSE 0 END) as Previous
                    FROM Transactions
                    WHERE SSN = %s
                    GROUP BY Type
                """, (ssn,))
                return cursor.fetchall()
            finally:
                conn.close()

        return []


    # ---------------- BULK  DELETE  Transcation----------------
    def bulk_delete_transactions(self, ssn):
        conn = self.connect()
        if conn:
            try:
                cursor = conn.cursor()
                # Calls the procedure that targets the entire SSN record
                cursor.callproc('BulkDeleteUserTransactions', (ssn,))
                conn.commit()
                print(f"All records for {ssn} have been cleared and logged.")
                return True
            except Error as e:
                print(f"Error during bulk delete: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()
    ## ---- DLT last Transcation --##
    def delete_last_transaction(self, ssn):
        conn = self.connect()
        if conn:
            try:
                cursor = conn.cursor()
                # Calls the procedure that finds the latest CreatedAt for this SSN
                cursor.callproc('DeleteLastUserTransaction', (ssn,))
                conn.commit()
                print("Latest transaction removed successfully.")
                return True
            except Error as e:
                print(f"Error during undo: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()

                # ---------------- SECURE DELETE (Targeted) ----------------
    def secure_delete_transaction(self, trans_id, ssn):
        conn = self.connect()
        if conn:
            try:
                cursor = conn.cursor()
                # 🔄 UPDATED NAME HERE TO v2
                cursor.callproc('SecureDeleteTransaction_v2', (trans_id, ssn))
                conn.commit()
                return True
            except Error as e:
                print(f"Deletion Error: {e}")
                return False
            finally:
                conn.close()
        return False
    # ---------------- ADMIN METRICS ----------------
    def get_admin_metrics(self):
        """Fetches data from the View created during initialization."""
        conn = self.connect()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                # This view is created in your initialize_system() method
                cursor.execute("SELECT * FROM Admin_Dashboard_Metrics")
                result = cursor.fetchone()
                return result if result else {'Total_Registered_Users': 0, 'Total_System_Entries': 0}
            except Exception as e:
                print(f"Metrics Error: {e}")
                return {'Total_Registered_Users': 0, 'Total_System_Entries': 0}
            finally:
                conn.close()
        return {'Total_Registered_Users': 0, 'Total_System_Entries': 0}

    # ---------------- ADMIN SEARCH ----------------
    def admin_search_user(self, search_term):
        """Calls the stored procedure for global user search."""
        conn = self.connect()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.callproc('AdminSearchUser', (search_term,))
                results = []
                for result in cursor.stored_results():
                    results.extend(result.fetchall())
                return results
            except Exception as e:
                print(f"Search Error: {e}")
                return []
            finally:
                conn.close()
        return []
     
     
