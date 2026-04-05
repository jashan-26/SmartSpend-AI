import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import io
import base64

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_app_background():
    try:
        bin_str = get_base64_of_bin_file('money_background.png')
        page_bg_img = f'''
        <style>
        .stApp {{
          background-image: url("data:image/png;base64,{bin_str}");
          background-size: cover;
          background-position: center;
          background-repeat: no-repeat;
          background-attachment: fixed;
          background-color: rgba(255, 255, 255, 0.82) !important; /* Forces 82% white overlay for high text legibility */
          background-blend-mode: screen !important;
        }}
        </style>
        '''
        st.markdown(page_bg_img, unsafe_allow_html=True)
    except:
        pass

from data_handler import authenticate_user, register_user, get_user_profile, save_user_profile, load_goals, save_goal, delete_goal, load_bills, save_bill, delete_bill, load_data, save_expense, save_bulk_expenses, clear_all_data, get_csv_content
from expense_manager import auto_categorize, get_category_totals, get_monthly_totals, get_highest_spending_category, CATEGORIES
from predictor import predict_next_month_budget, get_budget_alerts, generate_financial_advice, chatbot_response

st.set_page_config(page_title="SmartSpend AI", page_icon="💰", layout="wide")

custom_style = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       
       /* Mathy 'Calculative' Vibe */
       @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&family=Inter:wght@400;600;800&display=swap');
       
       h1, h2, h3 {
           font-family: 'Inter', sans-serif;
           color: #1E1E1E;
       }
       
       [data-testid="stMetric"] {
           background-color: #F1FFF6 !important; 
           border: 1px solid #C8E6C9 !important;
           border-left: 5px solid #3EB489 !important; 
           border-radius: 8px;
           padding: 15px !important;
           box-shadow: 0px 4px 6px rgba(62,180,137,0.1);
       }
       
       [data-testid="stMetricValue"] {
           font-family: 'Fira Code', monospace;
           color: #3EB489 !important; 
           font-size: 2.5rem !important;
           text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
       }
       
       [data-testid="stMetricLabel"] {
           font-weight: bold;
           color: #2F4F4F !important;
           font-family: 'Inter', sans-serif;
           font-size: 1.1rem;
       }
       </style>
"""
st.markdown(custom_style, unsafe_allow_html=True)
set_app_background()

# ----------------- LOGIN SYSTEM -----------------
if 'user' not in st.session_state:
    st.markdown("<div style='text-align: center; padding: 50px;'><h1 style='color: #3EB489; font-size: 3.5rem;'>SmartSpend AI</h1><p>Plan Smart. Spend Smarter.</p></div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h3 style='text-align: center; color: #2F4F4F;'>🔐 Security & Access</h3>", unsafe_allow_html=True)
        
        st.markdown("#### Login")
        u_login = st.text_input("Username", key="login_u")
        p_login = st.text_input("Password", type="password", key="login_p")
        
        if st.button("Access Dashboard"):
            if authenticate_user(u_login, p_login):
                st.session_state['user'] = u_login
                st.rerun()
            else:
                st.error("Invalid credentials or user doesn't exist!")
                
        st.markdown("<hr style='margin: 30px 0;'>", unsafe_allow_html=True)
        st.markdown("#### New User?")
        with st.expander("Click here to Sign Up & Create Account"):
            u_reg = st.text_input("Choose Username", key="reg_u")
            p_reg = st.text_input("Choose Password", type="password", key="reg_p")
            
            if st.button("Create Account"):
                if not u_reg or not p_reg:
                    st.error("Please enter a username and password!")
                else:
                    success, msg = register_user(u_reg, p_reg)
                    if success:
                        st.success(msg + " You can now log in above!")
                    else:
                        st.error(msg)
    st.stop()

# ----------------- AUTHENTICATED SYSTEM -----------------
USERNAME = st.session_state['user']

st.sidebar.markdown(f"## 👤 Hi, {USERNAME}")
if st.sidebar.button("Log out"):
    del st.session_state['user']
    st.rerun()

st.sidebar.markdown("## 🧭 Features Menu")
menu = st.sidebar.radio("Go to:", ["📊 Dashboard", "🎯 Goals & Profile", "📅 Bills & Subs", "📈 AI Budget Predictor", "💬 AI Financial Advisor"])

st.sidebar.markdown("---")
st.sidebar.markdown("### ➕ Quick Add Expense")
with st.sidebar.form("quick_expense_form", clear_on_submit=True):
    date = st.date_input("Date", value=datetime.today())
    amount = st.number_input("Amount (₹)", min_value=0.01, format="%.2f")
    description = st.text_input("Description (e.g. Starbucks)")
    
    st.caption("Auto-categorized by AI")
    manual_cat = st.selectbox("Cat Override", ["Auto-Detect"] + CATEGORIES)
    submit = st.form_submit_button("Add & Update Charts")
    
if submit:
    if description.strip() == "":
        st.sidebar.error("Description required!")
    else:
        final_cat = auto_categorize(description) if manual_cat == "Auto-Detect" else manual_cat
        save_expense(USERNAME, date, amount, final_cat, description)
        st.sidebar.success(f"Added ₹{amount:.2f} for {final_cat}!")
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 📂 Bulk Upload (.csv)")
with st.sidebar.form("bulk_upload_form", clear_on_submit=True):
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
    st.caption("Auto-parses standard or wide matrices.")
    bulk_submit = st.form_submit_button("Upload & Process")
    
if bulk_submit and uploaded_file is not None:
    try:
        new_data = pd.read_csv(uploaded_file)
        is_wide_format = "Month" in new_data.columns and "Year" in new_data.columns
        
        if not is_wide_format:
            if "Category" not in new_data.columns and "Description" in new_data.columns:
                new_data["Category"] = new_data["Description"].astype(str).apply(auto_categorize)
            elif "Category" not in new_data.columns:
                new_data["Category"] = "Others"
                
            if "Date" not in new_data.columns:
                new_data["Date"] = datetime.today().date()
                
            if "Amount" not in new_data.columns:
                st.sidebar.error("Standard CSV must contain an 'Amount' column.")
            else:
                required = ["Date", "Amount", "Category", "Description"]
                for col in required:
                    if col not in new_data.columns:
                        new_data[col] = "Unknown"
                        
        if is_wide_format or "Amount" in new_data.columns:
            success, msg = save_bulk_expenses(USERNAME, new_data)
            if success:
                st.sidebar.success("Data ingested successfully!")
                st.rerun()
            else:
                st.sidebar.error(msg)
                
    except Exception as e:
        st.sidebar.error(f"Error reading CSV: {e}")

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚠️ Danger Zone")
if st.sidebar.button("🗑️ Reset Profile"):
    clear_all_data(USERNAME)
    st.sidebar.success("All data wiped securely.")
    st.rerun()

# ----------------- PAGES -----------------

if menu == "📊 Dashboard":
    st.header("📊 Spending Analysis")
    
    # Bill Reminders Logic
    bills_df = load_bills(USERNAME)
    if not bills_df.empty:
        today_day = datetime.today().day
        for idx, bill in bills_df.iterrows():
            diff = bill['DueDay'] - today_day
            if 0 <= diff <= 5:
                st.warning(f"💳 **BILL DUE SOON:** Your ₹{bill['Amount']:,.2f} {bill['BillName']} subscription is due in {diff} days (on the {bill['DueDay']}th)!")
            elif diff < 0 and diff > -5:
                st.error(f"💳 **BILL OVERDUE:** Your ₹{bill['Amount']:,.2f} {bill['BillName']} was due {-diff} days ago!")

    df = load_data(USERNAME)
    
    if df.empty:
        st.info("No expenses recorded yet. Start adding manually or upload a CSV!")
    else:
        st.success("🤖 **AI Advice:** " + generate_financial_advice(USERNAME))
        
        # Determine actual savings rate
        profile = get_user_profile(USERNAME)
        salary = profile.get("salary", 0)
        
        total_spent = df['Amount'].sum()
        highest_cat, highest_amt = get_highest_spending_category(USERNAME)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Spending", f"₹{total_spent:,.2f}")
        col2.metric("Highest Category", f"{highest_cat}")
        col3.metric("Highest Category Total", f"₹{highest_amt:,.2f}")
        
        if salary > 0:
            st.metric("Logged Monthly Net Profit", f"₹{(salary - total_spent):,.2f}")
            
        st.markdown("---")
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.subheader("Category Breakdown")
            cat_totals = get_category_totals(USERNAME)
            if cat_totals:
                fig_pie = px.pie(values=list(cat_totals.values()), names=list(cat_totals.keys()), hole=0.4, 
                                 color_discrete_sequence=px.colors.sequential.algae)
                fig_pie.update_layout(transition_duration=500)
                st.plotly_chart(fig_pie, use_container_width=True)
                
        with col_chart2:
            st.subheader("Monthly Trends")
            mon_totals = get_monthly_totals(USERNAME)
            if mon_totals:
                mon_df = pd.DataFrame(list(mon_totals.items()), columns=["Month", "Amount"])
                fig_line = px.line(mon_df, x="Month", y="Amount", text="Amount", markers=True)
                fig_line.update_traces(textposition='top center', texttemplate='₹%{text:.2s}', line_color='#3EB489', marker=dict(size=10, color='#2F4F4F'))
                fig_line.update_layout(transition_duration=500, plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(showgrid=True, gridcolor='#E8F5E9'), xaxis=dict(showgrid=False))
                st.plotly_chart(fig_line, use_container_width=True)
                
        st.markdown("---")
        st.subheader("All Expenses")
        st.dataframe(df.sort_values(by=["Date", "Category"], ascending=[True, True]), use_container_width=True, height=350)
        
        csv_data = get_csv_content(USERNAME)
        st.download_button("Download Report (CSV)", data=csv_data, file_name="smartspend_report.csv", mime="text/csv")


elif menu == "🎯 Goals & Profile":
    st.header("🎯 Goals & Profile Configuration")
    profile = get_user_profile(USERNAME)
    
    st.subheader("💰 Monthly Income")
    s_col1, s_col2 = st.columns([1, 2])
    with s_col1:
        current_salary = profile.get("salary", 0)
        new_salary = st.number_input("Average Monthly Salary (₹)", value=float(current_salary), step=1000.0)
        if st.button("Save Income"):
            save_user_profile(USERNAME, new_salary)
            st.success("Income synced!")
            st.rerun()
            
    st.markdown("---")
    st.subheader("🏆 Savings Goals")
    
    with st.expander("Add New Item Goal"):
        with st.form("goal_form"):
            g_name = st.text_input("Goal Name (e.g. iPhone 15)")
            g_cost = st.number_input("Target Amount (₹)", min_value=1.0, step=1000.0)
            g_months = st.number_input("Target Duration (Months from now)", min_value=1, step=1)
            submit_g = st.form_submit_button("Start Saving")
            if submit_g:
                save_goal(USERNAME, g_name, g_cost, g_months)
                st.success("Goal initiated!")
                st.rerun()

    goals_df = load_goals(USERNAME)
    if not goals_df.empty:
        for idx, g in goals_df.iterrows():
            monthly_req = g['TargetAmount'] / g['MonthsLeft']
            st.info(f"**{g['GoalName']}**: You need to save **₹{monthly_req:,.2f}/mo** to hit your goal of ₹{g['TargetAmount']:,.2f} in {g['MonthsLeft']} months.")
            if st.button(f"Delete {g['GoalName']}", key=f"delg_{idx}"):
                delete_goal(USERNAME, idx)
                st.rerun()
    else:
        st.caption("No goals active.")

elif menu == "📅 Bills & Subs":
    st.header("📅 Subscription Tracker")
    st.markdown("Add recurring bills and the dashboard will warn you 5 days before they are due!")
    
    with st.form("bill_form"):
        b_name = st.text_input("Service (e.g. Netflix, Electricity)")
        b_amt = st.number_input("Fixed Amount (₹)", min_value=1.0)
        b_day = st.slider("Day of the Month Due", min_value=1, max_value=31, value=15)
        submit_b = st.form_submit_button("Track Bill")
        if submit_b:
            save_bill(USERNAME, b_name, b_amt, b_day)
            st.success("Bill tracked!")
            st.rerun()

    bills_df = load_bills(USERNAME)
    if not bills_df.empty:
        st.table(bills_df)
        st.caption("To delete a bill, use the exact index. (WIP UI feature)")

elif menu == "📈 AI Budget Predictor":
    st.header("📈 AI Budget Predictor")
    
    budget, msg = predict_next_month_budget(USERNAME)
    
    st.markdown("### Next Month's Budget Estimate")
    st.metric(label="Predicted Target Budget", value=f"₹{budget:,.2f}")
    st.caption(msg)
    
    st.markdown("---")
    st.subheader("Current Month Status")
    
    df = load_data(USERNAME)
    if not df.empty:
        df['Date'] = pd.to_datetime(df['Date'])
        current_month = datetime.today().strftime('%Y-%m')
        df['YearMonth'] = df['Date'].dt.strftime('%Y-%m')
        current_spending = df[df['YearMonth'] == current_month]['Amount'].sum()
        
        st.metric("Total Spent This Month", f"₹{current_spending:,.2f}")
        alert_msg, alert_status = get_budget_alerts(current_spending, budget)
        
        if alert_msg:
            if alert_status == "error":
                st.error(alert_msg)
            elif alert_status == "warning":
                st.warning(alert_msg)
            else:
                st.success(alert_msg)
    else:
        st.info("No data available to calculate current status.")

elif menu == "💬 AI Financial Advisor":
    st.header("💬 Context-Aware AI Advisor")
    st.markdown("This enhanced AI natively monitors your goals, salary bounds, and active expenses.")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    if prompt := st.chat_input("Ask: 'Am I overspending for my goals?'"):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        response = chatbot_response(USERNAME, prompt)
        
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
