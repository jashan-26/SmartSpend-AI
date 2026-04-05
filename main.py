import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import io

from data_handler import authenticate_user, register_user, get_user_profile, save_user_profile, load_goals, save_goal, delete_goal, load_bills, save_bill, delete_bill, load_data, save_expense, save_bulk_expenses, clear_all_data, get_csv_content
from expense_manager import auto_categorize, get_category_totals, get_monthly_totals, get_highest_spending_category, CATEGORIES
from predictor import predict_next_month_budget, get_budget_alerts, generate_financial_advice, chatbot_response

st.set_page_config(page_title="SmartSpend AI", page_icon="🌌", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM THEME (Galaxy / Glassmorphism) ---
custom_style = """
<style>
/* Base Dark Theme Overrides */
.stApp {
    background: linear-gradient(135deg, #090312 0%, #1A0B2E 50%, #2B0B3F 100%);
    color: #E2D9F3;
    font-family: 'Inter', sans-serif;
}

/* Hide Default Headers */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {background: transparent !important;}

/* Glassmorphism Containers (Cards, Forms) */
.glass-card {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    margin-bottom: 20px;
}

/* Stylish Gradient Buttons */
div.stButton > button:first-child {
    background: linear-gradient(90deg, #8E2DE2 0%, #4A00E0 100%);
    color: white;
    border: none;
    border-radius: 30px;
    padding: 8px 16px;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(142, 45, 226, 0.4);
    white-space: nowrap;
}
div.stButton > button:first-child:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(142, 45, 226, 0.6);
    background: linear-gradient(90deg, #4A00E0 0%, #8E2DE2 100%);
    color: white;
}

/* Text Inputs Dark Glass */
div[data-baseweb="input"] {
    background-color: rgba(0, 0, 0, 0.4) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 8px !important;
}

/* Headings */
h1, h2, h3, h4 {
    color: #FFFFFF !important;
    font-weight: 700 !important;
    letter-spacing: -0.5px;
}

/* Gradients for major titles */
.gradient-text {
    background: linear-gradient(90deg, #FF007F, #8E2DE2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 4.5rem;
    font-weight: 800;
    line-height: 1.2;
}

/* Metrics Glass */
[data-testid="stMetric"] {
    background: rgba(43, 11, 63, 0.5) !important;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-left: 4px solid #FF007F !important;
    border-radius: 12px;
    padding: 20px !important;
}
[data-testid="stMetricValue"] {
    color: #FFFFFF !important;
    font-size: 2.2rem !important;
}
[data-testid="stMetricLabel"] {
    color: #A991D4 !important;
}

/* Dataframe header styling */
th {
    background-color: #2B0B3F !important;
    color: white !important;
}

</style>
"""
st.markdown(custom_style, unsafe_allow_html=True)

# ----------------- SESSION STATE ROUTER -----------------
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'landing'
if 'user' not in st.session_state:
    st.session_state['user'] = None

def navigate_to(page_name):
    st.session_state['current_page'] = page_name
    st.rerun()

# ----------------- NAVIGATION BAR -----------------
def render_navbar():
    # Top navigation layout
    col_logo, col_space, col_nav1, col_nav2 = st.columns([2, 4.5, 1.5, 1.5])
    
    with col_logo:
        # Clickable logo simulation
        st.markdown("<h3 style='margin-top:0; color:white;'>🌌 SmartSpend AI</h3>", unsafe_allow_html=True)
        
    if st.session_state['user'] is None:
        with col_nav1:
            if st.button("Login"):
                navigate_to("login")
        with col_nav2:
            if st.button("Sign Up"):
                navigate_to("signup")
    else:
        with col_nav1:
            if st.button("Dashboard"):
                navigate_to("dashboard")
        with col_nav2:
            if st.button("Logout"):
                st.session_state['user'] = None
                navigate_to("landing")
    st.markdown("---")

# ----------------- VIEW: LANDING -----------------
def render_landing():
    st.markdown("<div style='text-align: center; padding: 10px 0;'>", unsafe_allow_html=True)
    st.markdown("<h1 class='gradient-text'>SmartSpend AI</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #E2D9F3; font-weight: 400; margin-bottom: 30px;'>Spend Smart. Plan Smarter.</h3>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class='glass-card' style='max-width: 800px; margin: 0 auto; text-align: center;'>
            <h3>Welcome to the Future of Finance</h3>
            <p style='color: #E2D9F3; font-size: 1.1rem; line-height: 1.6;'>
            SmartSpend AI leverages contextual machine learning and heuristic analysis to transform your financial habits. 
            Experience an isolated, secure, and beautiful ecosystem designed for wealth growth.
            </p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Feature Grid
    st.markdown("<h2 style='text-align: center; margin-bottom: 30px;'>Core Architecture</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class='glass-card'>
            <h4>🤖 AI-Powered Guidance</h4>
            <p style='color:#A991D4;'>Context-aware chatbots analyze your goals and burns rates.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class='glass-card'>
            <h4>🎯 Goal-Oriented Planning</h4>
            <p style='color:#A991D4;'>Set timelines for gadgets, cars, or trips and track monthly targets.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class='glass-card'>
            <h4>📈 Expense Predictor</h4>
            <p style='color:#A991D4;'>Predict next month's budget using Time-Series Linear Regression.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class='glass-card'>
            <h4>📅 Subscription Tracker</h4>
            <p style='color:#A991D4;'>Never let an auto-renewal catch you off guard again.</p>
        </div>
        """, unsafe_allow_html=True)

# ----------------- VIEW: AUTHENTICATION -----------------
def render_auth(mode="login"):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
        
        if mode == "login":
            st.markdown("<h2 style='text-align: center;'>Welcome Back</h2>", unsafe_allow_html=True)
            u_login = st.text_input("Username")
            p_login = st.text_input("Password", type="password")
            
            st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
            if st.button("Access Engine"):
                if authenticate_user(u_login, p_login):
                    st.session_state['user'] = u_login
                    st.success("Authentication successful!")
                    navigate_to("dashboard")
                else:
                    st.error("Invalid credentials or user doesn't exist.")
                    
            st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #A991D4;'>Don't have an account?</p>", unsafe_allow_html=True)
            
            # Center the secondary button perfectly
            col_b1, col_b2, col_b3 = st.columns([1, 1.5, 1])
            with col_b2:
                if st.button("Create Account safely"):
                    navigate_to("signup")
                
        elif mode == "signup":
            st.markdown("<h2 style='text-align: center;'>Create User Profile</h2>", unsafe_allow_html=True)
            u_reg = st.text_input("Choose Username")
            p_reg = st.text_input("Choose Password", type="password")
            
            st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
            if st.button("Register & Initialize"):
                if not u_reg or not p_reg:
                    st.error("Fields cannot be empty!")
                else:
                    success, msg = register_user(u_reg, p_reg)
                    if success:
                        st.session_state['user'] = u_reg
                        st.success(msg)
                        navigate_to("dashboard")
                    else:
                        st.error(msg)
                        
            st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #A991D4;'>Already highly ranked?</p>", unsafe_allow_html=True)
            
            col_b1, col_b2, col_b3 = st.columns([1, 1.3, 1])
            with col_b2:
                if st.button("Log In safely"):
                    navigate_to("login")
                


# ----------------- VIEW: DASHBOARD -----------------
def render_dashboard():
    USERNAME = st.session_state['user']
    
    st.sidebar.markdown(f"### 👤 Agent {USERNAME}")
    st.sidebar.markdown("---")
    menu = st.sidebar.radio("Navigation Engine", ["📊 Nexus Dashboard", "🎯 Goals & Profile", "📅 Bills & Subs", "📈 AI Budget Predictor", "💬 AI Context Advisor"])
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("#### ➕ Add Expense")
    with st.sidebar.form("quick_expense_form", clear_on_submit=True):
        date = st.date_input("Date", value=datetime.today())
        amount = st.number_input("Amount (₹)", min_value=0.01, format="%.2f")
        description = st.text_input("Description")
        manual_cat = st.selectbox("Category Override", ["Auto-Detect"] + CATEGORIES)
        submit = st.form_submit_button("Log Transaction")
        
    if submit:
        if description.strip() == "":
            st.sidebar.error("Description required!")
        else:
            final_cat = auto_categorize(description) if manual_cat == "Auto-Detect" else manual_cat
            save_expense(USERNAME, date, amount, final_cat, description)
            st.sidebar.success(f"Tracked ₹{amount:.2f}")
            st.rerun()

    st.sidebar.markdown("#### 📂 Bulk Uplink")
    with st.sidebar.form("bulk_upload_form", clear_on_submit=True):
        uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
        bulk_submit = st.form_submit_button("Process Data")
        
    if bulk_submit and uploaded_file is not None:
        try:
            new_data = pd.read_csv(uploaded_file)
            is_wide = "Month" in new_data.columns and "Year" in new_data.columns
            if not is_wide:
                if "Category" not in new_data.columns and "Description" in new_data.columns:
                    new_data["Category"] = new_data["Description"].astype(str).apply(auto_categorize)
                elif "Category" not in new_data.columns:
                    new_data["Category"] = "Others"
                if "Date" not in new_data.columns:
                    new_data["Date"] = datetime.today().date()
                if "Amount" not in new_data.columns:
                    st.sidebar.error("CSV requires an 'Amount' column.")
                else:
                    for col in ["Date", "Amount", "Category", "Description"]:
                        if col not in new_data.columns:
                            new_data[col] = "Unknown"
                            
            if is_wide or "Amount" in new_data.columns:
                success, msg = save_bulk_expenses(USERNAME, new_data)
                if success:
                    st.sidebar.success(msg)
                    st.rerun()
                else:
                    st.sidebar.error(msg)
        except Exception as e:
            st.sidebar.error("Error processing file")

    if st.sidebar.button("🗑️ Wipe Sector Data"):
        clear_all_data(USERNAME)
        st.rerun()

    # Dashboard Sub-Routing
    if menu == "📊 Nexus Dashboard":
        st.markdown("<h2 style='color:#FF007F;'>Nexus Dashboard</h2>", unsafe_allow_html=True)
        
        bills_df = load_bills(USERNAME)
        if not bills_df.empty:
            today_day = datetime.today().day
            for idx, bill in bills_df.iterrows():
                diff = bill['DueDay'] - today_day
                if 0 <= diff <= 5:
                    st.warning(f"💳 BILL DUE: ₹{bill['Amount']:,.2f} for {bill['BillName']} in {diff} days!")
                elif diff < 0 and diff > -5:
                    st.error(f"💳 OVERDUE: ₹{bill['Amount']:,.2f} for {bill['BillName']} was due {-diff} days ago!")

        df = load_data(USERNAME)
        if df.empty:
            st.info("System Empty: Logging required.")
        else:
            st.success("🤖 " + generate_financial_advice(USERNAME))
            
            profile = get_user_profile(USERNAME)
            salary = profile.get("salary", 0)
            total_spent = df['Amount'].sum()
            highest_cat, highest_amt = get_highest_spending_category(USERNAME)
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Burn", f"₹{total_spent:,.2f}")
            c2.metric("Apex Category", f"{highest_cat}")
            c3.metric("Apex Burn", f"₹{highest_amt:,.2f}")
            
            if salary > 0:
                st.metric("Net Retention", f"₹{(salary - total_spent):,.2f}")
                
            ch1, ch2 = st.columns(2)
            with ch1:
                st.markdown("### Spending Matrix")
                cat_totals = get_category_totals(USERNAME)
                if cat_totals:
                    fig_pie = px.pie(values=list(cat_totals.values()), names=list(cat_totals.keys()), hole=0.5,
                                     color_discrete_sequence=px.colors.sequential.Purp)
                    # Transparent Plotly background for glassmorphism
                    fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
                    st.plotly_chart(fig_pie, use_container_width=True)
            with ch2:
                st.markdown("### Temporal Velocity")
                mon_totals = get_monthly_totals(USERNAME)
                if mon_totals:
                    mon_df = pd.DataFrame(list(mon_totals.items()), columns=["Month", "Amount"])
                    fig_line = px.line(mon_df, x="Month", y="Amount", markers=True)
                    fig_line.update_traces(line_color='#FF007F', marker=dict(size=10, color='#8E2DE2'))
                    fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
                    st.plotly_chart(fig_line, use_container_width=True)
                    
            st.markdown("### Transaction Ledger")
            st.dataframe(df.sort_values(by=["Date"]), use_container_width=True)
            st.download_button("Export Data Matrix", data=get_csv_content(USERNAME), file_name="export.csv")

    elif menu == "🎯 Goals & Profile":
        st.markdown("<h2 style='color:#FF007F;'>Objective Configurations</h2>", unsafe_allow_html=True)
        profile = get_user_profile(USERNAME)
        
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            new_salary = st.number_input("Monthly Influx (₹)", value=float(profile.get("salary", 0)))
            if st.button("Sync Income"):
                save_user_profile(USERNAME, new_salary)
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            
        with st.expander("Register New Objective"):
            with st.form("goal_form"):
                g_name = st.text_input("Designation")
                g_cost = st.number_input("Required Capital (₹)", min_value=1.0)
                g_months = st.number_input("Cycle Duration (Months)", min_value=1)
                if st.form_submit_button("Initiate Protocol"):
                    save_goal(USERNAME, g_name, g_cost, g_months)
                    st.rerun()

        goals_df = load_goals(USERNAME)
        if not goals_df.empty:
            for idx, g in goals_df.iterrows():
                monthly_req = g['TargetAmount'] / g['MonthsLeft']
                st.info(f"**{g['GoalName']}**: Retention of **₹{monthly_req:,.2f}/mo** required to acquire by {g['MonthsLeft']} cycles.")
                if st.button(f"Terminate {g['GoalName']}", key=f"delg_{idx}"):
                    delete_goal(USERNAME, idx)
                    st.rerun()

    elif menu == "📅 Bills & Subs":
        st.markdown("<h2 style='color:#FF007F;'>Subscription Sentinels</h2>", unsafe_allow_html=True)
        with st.form("bill_form"):
            b_name = st.text_input("Service Identifier")
            b_amt = st.number_input("Cyclic Cost (₹)", min_value=1.0)
            b_day = st.slider("Billing Day", 1, 31, 15)
            if st.form_submit_button("Deploy Sentinel"):
                save_bill(USERNAME, b_name, b_amt, b_day)
                st.rerun()
        bills_df = load_bills(USERNAME)
        if not bills_df.empty:
            st.dataframe(bills_df, use_container_width=True)

    elif menu == "📈 AI Budget Predictor":
        st.markdown("<h2 style='color:#FF007F;'>Prediction Engine</h2>", unsafe_allow_html=True)
        budget, msg = predict_next_month_budget(USERNAME)
        
        st.metric("Forecasted Target", f"₹{budget:,.2f}")
        st.caption(msg)
        
        df = load_data(USERNAME)
        if not df.empty:
            df['Date'] = pd.to_datetime(df['Date'])
            df['YearMonth'] = df['Date'].dt.strftime('%Y-%m')
            curr = df[df['YearMonth'] == datetime.today().strftime('%Y-%m')]['Amount'].sum()
            
            st.metric("Current Cycle Burn", f"₹{curr:,.2f}")
            alert_msg, status = get_budget_alerts(curr, budget)
            if alert_msg:
                if status == "error": st.error(alert_msg)
                elif status == "warning": st.warning(alert_msg)
                else: st.success(alert_msg)

    elif menu == "💬 AI Context Advisor":
        st.markdown("<h2 style='color:#FF007F;'>Context Engine Active</h2>", unsafe_allow_html=True)
        
        if "messages" not in st.session_state:
            st.session_state.messages = []
            
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
        if prompt := st.chat_input("Query the system..."):
            st.chat_message("user").markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})
            resp = chatbot_response(USERNAME, prompt)
            with st.chat_message("assistant"):
                st.markdown(resp)
            st.session_state.messages.append({"role": "assistant", "content": resp})

# ----------------- MAIN EXECUTION ENGINE -----------------

render_navbar()

if st.session_state['user'] is not None:
    st.session_state['current_page'] = 'dashboard'
    render_dashboard()
else:
    page = st.session_state['current_page']
    if page == 'landing':
        render_landing()
    elif page == 'login':
        render_auth("login")
    elif page == 'signup':
        render_auth("signup")
