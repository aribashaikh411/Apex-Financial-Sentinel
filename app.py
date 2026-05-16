
import streamlit as st
from sentinel_engine import ApexFinancialSentinel
from streamlit_autorefresh import st_autorefresh

# 1. Start Auto-refresh (3 seconds)
st_autorefresh(interval=3000, key="sentinel_refresh")

# 2. Setup Engine Connection
sentinel = ApexFinancialSentinel(
    host='localhost',
    user='apex_sentinel_admin',
    password='ApexSecure_2026!'
)

st.set_page_config(page_title="Apex Sentinel", layout="wide", page_icon="🛡️")

# 3. Session State Management
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_ssn" not in st.session_state:
    st.session_state.current_ssn = None

# 4. FIX: AUTOMATED DATABASE INITIALIZATION
# We call the engine's method. No need to define it here.
if "db_initialized" not in st.session_state:
    try:
        sentinel.initialize_system()
        st.session_state.db_initialized = True
    except Exception as e:
        st.error(f"Database System Check Failed: {e}")

# ---------------- SIDEBAR ----------------
st.sidebar.title("🛡️ Apex Sentinel")

if not st.session_state.logged_in:
    page = st.sidebar.radio("Access Mode", ["Login", "Sign Up"])
else:
    page = "Dashboard"
    st.sidebar.success(f"Connected: {st.session_state.current_ssn}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.current_ssn = None
        st.rerun()

# ---------------- SIGNUP ----------------
if page == "Sign Up":
    st.title("Create Account")
    col1, col2 = st.columns(2)
    with col1:
        ssn = st.text_input("SSN (e.g., 42101-XXXXXXX-X)")
        name = st.text_input("Full Name")
    with col2:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

    if st.button("Register", width='stretch'):
        try:
            first, last = name.split(" ", 1) if " " in name else (name, "")
            sentinel.signup_user(ssn, first, last, email, password)
            st.success("Account Created! You can now log in.")
        except Exception as e:
            st.error(f"Registration Failed: {str(e)}")

# ---------------- LOGIN ----------------
elif page == "Login":
    st.title("Secure Login")
    ssn = st.text_input("SSN")
    password = st.text_input("Password", type="password")

    if st.button("Login",width='stretch'):
        if sentinel.verify_login(ssn, password):
            st.session_state.logged_in = True
            st.session_state.current_ssn = ssn
            st.rerun()
        else:
            st.error("Invalid credentials.")

# ---------------- DASHBOARD ----------------
elif page == "Dashboard" and st.session_state.logged_in:
    ssn = st.session_state.current_ssn
    st.title(f"Financial Sentinel - User: {ssn}")

    tab1, tab2, tab3, tab4 = st.tabs([
        " Transactions", 
        " Analytics", 
        " Live Data", 
        " Admin Panel"
    ])

# ================= TAB 1: Transactions =================
    with tab1:
        # --- Column 1: New Transaction Entry ---
        col_entry, col_modify, col_bulk = st.columns([1.2, 1.2, 0.8])

        with col_entry:
            st.subheader(" New Entry")
            with st.form("transaction_form", clear_on_submit=True):
                t_type = st.selectbox("Type", ["Income", "Expense"])
                category = st.text_input("Category")
                amount = st.number_input("Amount", min_value=0.0)
                currency = st.selectbox("Currency", ["PKR", "USD", "EUR"])
                
                if st.form_submit_button("Commit to Ledger", use_container_width=True):
                    sentinel.process_transaction(ssn, "N/A", "N/A", "N/A", "N/A", currency, amount, t_type, category)
                    st.success("Record Added")
                    st.rerun()

        # --- Column 2: Search & Modify Individual Records ---
        # --- Column 2: Search & Modify Individual Records ---
        with col_modify:
            st.subheader(" Manage Records")
            user_records = sentinel.get_user_transactions(ssn)
            
            if user_records:
                # UPDATED: Use AmountUser and CurrencyCode for the label
                # This ensures EUR shows as EUR instead of converted PKR
                record_options = {
                    f"{r['Type']} | {r['Category']} | {r['AmountUser']} {r['CurrencyCode']}": r['TransactionID'] 
                    for r in user_records
                }
                
                selected_label = st.selectbox("Select Transaction:", options=list(record_options.keys()))
                target_id = record_options[selected_label]

                st.write("---")
                # Row 1: Update
                new_val = st.number_input("Update Amount to:", min_value=0.0, key="upd_val")
                if st.button("Update This Transaction", use_container_width=True):
                    # Call your update logic here
                    conn = sentinel.connect()
                    cursor = conn.cursor()
                    cursor.callproc("UpdateTransactionAmount", (target_id, ssn, new_val, "PKR"))
                    conn.commit()
                    conn.close()
                    st.toast("Transaction Updated!")
                    st.rerun()

                # Row 2: Delete
                if st.button("Delete This Transaction", type="primary", use_container_width=True):
                    sentinel.secure_delete_transaction(target_id, ssn)
                    st.rerun()
            else:
                st.info("No records to manage.")

        # --- Column 3: Bulk Actions ---
        with col_bulk:
            st.subheader(" System Actions")
            st.write("Perform bulk operations on your ledger.")
            
            # Restore Data (Logic depends on your 'Deleted# Restore Data
            if st.button(" Restore All Deleted Data"):
                # Use 'sentinel' instead of 'engine'
                success = sentinel.restore_all_user_data(ssn) 
                if success:
                    st.success("Data restored successfully!")
                    st.rerun() # Forces the dashboard to update immediately
                else:
                    st.warning("No data found in the log to restore.")
            # Permanent Wipe
            st.write("**Danger Zone**")
            if st.button("Delete Permanently", help="This wipes all your history forever.", width='stretch'):
                # Logic: TRUNCATE or DELETE where SSN = ssn
                sentinel.hard_wipe_user_data(ssn) # Ensure this exists in engine
                st.warning("All data purged.")
                st.rerun()

    # ================= TAB 2: Analytics =================
    with tab2:
        summary = sentinel.get_summary(ssn)
        if summary:
            data = {row['Type']: row for row in summary}
            c1, c2 = st.columns(2)
            for label, key in [("Income", "Income"), ("Expense", "Expense")]:
                curr = data.get(key, {}).get("Current", 0) or 0
                prev = data.get(key, {}).get("Previous", 0) or 0
                diff = curr - prev
                (c1 if key=="Income" else c2).metric(label, f"{curr:,.2f} PKR", f"{diff:,.2f}")

    # ================= TAB 3: Live Data =================
    with tab3:
        st.subheader("Statistical Intelligence")
        view_choice = st.radio("Filter", ["Expense", "Income"], horizontal=True)
        fig = sentinel.get_financial_stats(ssn, view_choice)
        
        if fig:
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("Add transactions to generate visual intelligence.")

    # ================= TAB 4: Admin Panel =================
    with tab4:
        admin_key = st.text_input("Admin Access Key", type="password")
        if admin_key == "ApexAdmin2026":
            st.success("Authorized")
            metrics = sentinel.get_admin_metrics()
            m1, m2 = st.columns(2)
            m1.metric("Total Users", metrics['Total_Registered_Users'])
            m2.metric("System Transactions", metrics['Total_System_Entries'])
            
            st.divider()
            search = st.text_input("Search Registry (SSN/Name/Email)")
            if search:
                results = sentinel.admin_search_user(search)
                if results:
                    for u in results:
                        with st.expander(f"👤 {u['FirstName']} {u['LastName']}"):
                            st.write(f"SSN: {u['SSN']} | Email: {u['Email']}")
                            if st.button("View User Ledger", key=f"btn_{u['SSN']}"):
                                st.table(sentinel.get_user_transactions(u['SSN']))
                else:
                    st.warning("No matches found.")
        elif admin_key:
            st.error("Invalid Admin Key.")
