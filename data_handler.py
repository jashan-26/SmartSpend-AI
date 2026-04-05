import os
import json
import pandas as pd
from datetime import datetime

DATA_DIR = "data"

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

USERS_FILE = os.path.join(DATA_DIR, "users.csv")

def authenticate_user(username, password):
    if not os.path.exists(USERS_FILE):
        return False
    df = pd.read_csv(USERS_FILE, dtype=str)
    
    # Secure string formatting and whitespace stripping
    df['username'] = df['username'].astype(str).str.strip()
    df['password'] = df['password'].astype(str).str.strip()
    username = str(username).strip()
    password = str(password).strip()
    
    user = df[(df['username'] == username) & (df['password'] == password)]
    return len(user) > 0

def register_user(username, password):
    username = str(username).strip()
    password = str(password).strip()
    
    if not os.path.exists(USERS_FILE):
        df = pd.DataFrame(columns=["username", "password"])
        df.to_csv(USERS_FILE, index=False)
        
    df = pd.read_csv(USERS_FILE, dtype=str)
    df['username'] = df['username'].astype(str).str.strip()
    
    if username in df['username'].values:
        return False, "Username already exists!"
        
    new_user = pd.DataFrame([{"username": username, "password": password}])
    df = pd.concat([df, new_user], ignore_index=True)
    df.to_csv(USERS_FILE, index=False)
    
    # Initialize basic files
    clear_all_data(username)
    
    return True, "Registered successfully!"

def get_user_file(username, file_type):
    return os.path.join(DATA_DIR, f"{username}_{file_type}.csv")

def get_user_profile(username):
    profile_path = os.path.join(DATA_DIR, f"{username}_profile.json")
    if os.path.exists(profile_path):
        with open(profile_path, 'r') as f:
            return json.load(f)
    return {"salary": 0}

def save_user_profile(username, salary):
    profile_path = os.path.join(DATA_DIR, f"{username}_profile.json")
    with open(profile_path, 'w') as f:
        json.dump({"salary": float(salary)}, f)

def init_db(username):
    f = get_user_file(username, "expenses")
    if not os.path.exists(f):
        df = pd.DataFrame(columns=["Date", "Amount", "Category", "Description"])
        df.to_csv(f, index=False)
        return True
    return False

def load_data(username):
    f = get_user_file(username, "expenses")
    if not os.path.exists(f):
        init_db(username)
    df = pd.read_csv(f)
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"]).dt.date
    return df

def save_expense(username, date, amount, category, description):
    df = load_data(username)
    new_data = pd.DataFrame([{
        "Date": date,
        "Amount": amount,
        "Category": category,
        "Description": description
    }])
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(get_user_file(username, "expenses"), index=False)

def clear_all_data(username):
    """Wipes all data from the database by storing an empty frame."""
    df = pd.DataFrame(columns=["Date", "Amount", "Category", "Description"])
    df.to_csv(get_user_file(username, "expenses"), index=False)
    
    pd.DataFrame(columns=["GoalName", "TargetAmount", "MonthsLeft"]).to_csv(get_user_file(username, "goals"), index=False)
    pd.DataFrame(columns=["BillName", "Amount", "DueDay"]).to_csv(get_user_file(username, "bills"), index=False)
    save_user_profile(username, 0)
    return True

def save_bulk_expenses(username, new_df):
    """
    Validates and saves a dataframe of expenses.
    Smart parser handles both Standard-Long and Wide-Format (Month, Year, Categories).
    """
    df = load_data(username)
    f = get_user_file(username, "expenses")
    
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
            
            df = pd.concat([df, melted_df[["Date", "Amount", "Category", "Description"]]], ignore_index=True)
            df.to_csv(f, index=False)
            return True, "Smart CSV Compilation Successful!"
            
    # Default standard validation
    required_cols = ["Date", "Amount", "Category", "Description"]
    
    for col in required_cols:
        if col not in new_df.columns:
            return False, f"Missing required column: {col}"
            
    new_df['Amount'] = pd.to_numeric(new_df['Amount'], errors='coerce').fillna(0)
    
    df = pd.concat([df, new_df[required_cols]], ignore_index=True)
    df.to_csv(f, index=False)
    return True, "Expenses appended successfully"

def get_csv_content(username):
    f = get_user_file(username, "expenses")
    if not os.path.exists(f):
        return ""
    with open(f, "r") as fs:
        return fs.read()

# --------------- NEW FEATURES FOR GOALS AND BILLS ---------------

def load_goals(username):
    f = get_user_file(username, "goals")
    if not os.path.exists(f):
        pd.DataFrame(columns=["GoalName", "TargetAmount", "MonthsLeft"]).to_csv(f, index=False)
    return pd.read_csv(f)

def save_goal(username, name, target, months):
    f = get_user_file(username, "goals")
    df = load_goals(username)
    new_data = pd.DataFrame([{"GoalName": name, "TargetAmount": float(target), "MonthsLeft": int(months)}])
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(f, index=False)

def delete_goal(username, index):
    f = get_user_file(username, "goals")
    df = load_goals(username)
    df = df.drop(index)
    df.to_csv(f, index=False)

def load_bills(username):
    f = get_user_file(username, "bills")
    if not os.path.exists(f):
        pd.DataFrame(columns=["BillName", "Amount", "DueDay"]).to_csv(f, index=False)
    return pd.read_csv(f)

def save_bill(username, name, amount, day):
    f = get_user_file(username, "bills")
    df = load_bills(username)
    new_data = pd.DataFrame([{"BillName": name, "Amount": float(amount), "DueDay": int(day)}])
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(f, index=False)

def delete_bill(username, index):
    f = get_user_file(username, "bills")
    df = load_bills(username)
    df = df.drop(index)
    df.to_csv(f, index=False)
