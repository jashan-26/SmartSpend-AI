import streamlit as st
import pandas as pd
from datetime import datetime

# --------------------------------------------------------------------------
# IN-MEMORY DATABASE HANDLER (No .csv / File I/O required)
# --------------------------------------------------------------------------

def authenticate_user(username, password):
    if 'users_db' not in st.session_state:
        st.session_state['users_db'] = {}
    db = st.session_state['users_db']
    
    username = str(username).strip()
    password = str(password).strip()
    
    if username in db and db[username]['password'] == password:
        return True
    return False

def register_user(username, password):
    if 'users_db' not in st.session_state:
        st.session_state['users_db'] = {}
    db = st.session_state['users_db']
    
    username = str(username).strip()
    password = str(password).strip()
    
    if username in db:
        return False, "Username already exists in this session!"
        
    db[username] = {"password": password}
    # Initialize basic files for this user in session state
    clear_all_data(username)
    return True, "Registered successfully!"

def get_user_profile(username):
    key = f'{username}_profile'
    if key not in st.session_state:
        st.session_state[key] = {"salary": 0}
    return st.session_state[key]

def save_user_profile(username, salary):
    st.session_state[f'{username}_profile'] = {"salary": float(salary)}

def init_db(username):
    if f'{username}_expenses' not in st.session_state:
        st.session_state[f'{username}_expenses'] = pd.DataFrame(columns=["Date", "Amount", "Category", "Description"])

def load_data(username):
    init_db(username)
    df = st.session_state[f'{username}_expenses'].copy()
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"]).dt.date
    return df

def save_expense(username, date, amount, category, description):
    init_db(username)
    df = st.session_state[f'{username}_expenses']
    new_data = pd.DataFrame([{
        "Date": pd.to_datetime(date).date(),
        "Amount": amount,
        "Category": category,
        "Description": description
    }])
    st.session_state[f'{username}_expenses'] = pd.concat([df, new_data], ignore_index=True)

def clear_all_data(username):
    """Wipes all data from the database by storing an empty frame."""
    st.session_state[f'{username}_expenses'] = pd.DataFrame(columns=["Date", "Amount", "Category", "Description"])
    st.session_state[f'{username}_goals'] = pd.DataFrame(columns=["GoalName", "TargetAmount", "MonthsLeft"])
    st.session_state[f'{username}_bills'] = pd.DataFrame(columns=["BillName", "Amount", "DueDay"])
    save_user_profile(username, 0)
    return True

def save_bulk_expenses(username, new_df):
    """
    Validates and saves a dataframe of expenses.
    Smart parser handles both Standard-Long and Wide-Format (Month, Year, Categories).
    """
    init_db(username)
    df = st.session_state[f'{username}_expenses']
    
    # Check if this is the Wide Format layout
    if "Month" in new_df.columns and "Year" in new_df.columns:
        new_df['DateStr'] = "1 " + new_df['Month'].astype(str) + " " + new_df['Year'].astype(str)
        new_df['Date'] = pd.to_datetime(new_df['DateStr'], format="%d %B %Y", errors="coerce").dt.date
        
        potential_categories = ["Food", "Transport", "Shopping", "Bills", "Health", "Entertainment", "Others"]
        melt_categories = [c for c in potential_categories if c in new_df.columns]
        
        if len(melt_categories) > 0:
            melted_df = new_df.melt(id_vars=["Date"], value_vars=melt_categories, var_name="Category", value_name="Amount")
            melted_df["Description"] = "Bulk Upload"
            melted_df = melted_df.dropna(subset=["Amount", "Date"])
            melted_df['Amount'] = pd.to_numeric(melted_df['Amount'], errors='coerce').fillna(0)
            melted_df = melted_df[melted_df['Amount'] > 0]
            
            st.session_state[f'{username}_expenses'] = pd.concat([df, melted_df[["Date", "Amount", "Category", "Description"]]], ignore_index=True)
            return True, "Smart CSV Compilation Successful!"
            
    # Default standard validation
    required_cols = ["Date", "Amount", "Category", "Description"]
    
    for col in required_cols:
        if col not in new_df.columns:
            return False, f"Missing required column: {col}"
            
    new_df['Amount'] = pd.to_numeric(new_df['Amount'], errors='coerce').fillna(0)
    st.session_state[f'{username}_expenses'] = pd.concat([df, new_df[required_cols]], ignore_index=True)
    return True, "Expenses appended successfully"

def get_csv_content(username):
    df = load_data(username)
    if df.empty:
        return ""
    return df.to_csv(index=False)

# --------------- NEW FEATURES FOR GOALS AND BILLS ---------------

def load_goals(username):
    key = f'{username}_goals'
    if key not in st.session_state:
        st.session_state[key] = pd.DataFrame(columns=["GoalName", "TargetAmount", "MonthsLeft"])
    return st.session_state[key]

def save_goal(username, name, target, months):
    df = load_goals(username)
    new_data = pd.DataFrame([{"GoalName": name, "TargetAmount": float(target), "MonthsLeft": int(months)}])
    st.session_state[f'{username}_goals'] = pd.concat([df, new_data], ignore_index=True)

def delete_goal(username, index):
    df = load_goals(username)
    df = df.drop(index)
    st.session_state[f'{username}_goals'] = df

def load_bills(username):
    key = f'{username}_bills'
    if key not in st.session_state:
        st.session_state[key] = pd.DataFrame(columns=["BillName", "Amount", "DueDay"])
    return st.session_state[key]

def save_bill(username, name, amount, day):
    df = load_bills(username)
    new_data = pd.DataFrame([{"BillName": name, "Amount": float(amount), "DueDay": int(day)}])
    st.session_state[f'{username}_bills'] = pd.concat([df, new_data], ignore_index=True)

def delete_bill(username, index):
    df = load_bills(username)
    df = df.drop(index)
    st.session_state[f'{username}_bills'] = df
