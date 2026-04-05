import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from data_handler import load_data, get_user_profile, load_goals
from datetime import datetime

def predict_next_month_budget(username):
    """
    Predicts the recommended budget for next month based on historical monthly spending.
    Uses a simple Linear Regression model on aggregated monthly totals.
    """
    df = load_data(username)
    if df.empty:
        return 0.0, "Not enough data to predict."
        
    # Convert dates to datetime
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Calculate monthly totals
    df['YearMonth'] = df['Date'].dt.to_period('M')
    monthly_totals = df.groupby('YearMonth')['Amount'].sum().reset_index()
    
    if len(monthly_totals) < 2:
        # If we only have 1 month of data, just suggest 110% of that month or average
        return monthly_totals['Amount'].iloc[0] * 1.1, "Based on your single month of data + 10% buffer."
        
    # Sort chronologically just in case
    monthly_totals = monthly_totals.sort_values('YearMonth')
    
    # Create simple time index (0, 1, 2, ...)
    monthly_totals['TimeIndex'] = range(len(monthly_totals))
    
    X = monthly_totals[['TimeIndex']]
    y = monthly_totals['Amount']
    
    model = LinearRegression()
    model.fit(X, y)
    
    # Predict for the next month
    next_month_index = pd.DataFrame({'TimeIndex': [len(monthly_totals)]})
    predicted_amount = model.predict(next_month_index)[0]
    
    # Prevent negative budget predictions (if trend goes steeply down)
    predicted_amount = max(predicted_amount, 0)
    
    budget = round(predicted_amount, 2)
    
    return budget, "Predicted using Linear Regression modeling."

def get_budget_alerts(current_spending, predicted_budget):
    """
    Returns an alert message if current spending is close to or exceeds predicted budget.
    """
    if predicted_budget == 0:
        return None, "success"
        
    ratio = current_spending / predicted_budget
    if ratio >= 1.0:
        return f"ALARM! You have exceeded your predicted budget of ₹{predicted_budget}!", "error"
    elif ratio >= 0.8:
        return f"Warning: You have used {round(ratio*100)}% of your estimated budget (₹{predicted_budget}).", "warning"
    
    return f"You are within safe limits. Current spending: ₹{current_spending} / ₹{predicted_budget}", "success"

def generate_financial_advice(username):
    """
    Analyzes overall spending data and provides pre-calculated advice based on category thresholds.
    """
    df = load_data(username)
    if df.empty:
        return "Not enough data to generate advice."
        
    total_spent = df['Amount'].sum()
    if total_spent == 0:
        return "You have no recorded expenses."
        
    cat_totals = df.groupby('Category')['Amount'].sum()
    if cat_totals.empty:
        return "No categorized expenses found."
        
    highest_cat = cat_totals.idxmax()
    highest_amt = cat_totals.max()
    
    ratio = highest_amt / total_spent
    
    advice = f"You spend the most on **{highest_cat}** (₹{highest_amt:,.2f}), which is {ratio*100:.1f}% of your total spending."
    if ratio > 0.4:
        if highest_cat == "Food":
            advice += " Consider cooking at home more often to save money on dining out!"
        elif highest_cat == "Shopping":
            advice += " Try setting a strict monthly allowance for non-essential items."
        elif highest_cat == "Travel":
            advice += " Look into public transportation passes or carpooling to cut down transit costs."
        elif highest_cat == "Bills":
            advice += " Review your subscriptions and see if there are any idle services you can cancel."
        else:
            advice += " Try to diversify your spending or cut down slightly in this area."
    else:
        advice += " Your spending is relatively well distributed!"
        
    return advice

def chatbot_response(username, user_input):
    """
    Advanced Heuristic-based AI chatbot that correlates Salary, Spending, and Goals
    """
    user_input = user_input.lower()
    df = load_data(username)
    profile = get_user_profile(username)
    salary = profile.get("salary", 0)
    
    # Advanced logic for overspending calculation
    if "overspend" in user_input or "where am i overspending" in user_input or "prevent" in user_input or "help" in user_input:
        if df.empty:
            return "You haven't added any expenses yet for me to analyze!"
            
        cat_totals = df.groupby('Category')['Amount'].sum()
        highest_cat = cat_totals.idxmax()
        highest_amt = cat_totals.max()
        
        goals_df = load_goals(username)
        monthly_goal_burden = 0
        if not goals_df.empty:
            goals_df['MonthlyNeeded'] = goals_df['TargetAmount'] / goals_df['MonthsLeft'].replace(0, 1)
            monthly_goal_burden = goals_df['MonthlyNeeded'].sum()
            
        # Time calculations
        df['Date'] = pd.to_datetime(df['Date'])
        days = max((df['Date'].max() - df['Date'].min()).days, 1)
        total_spent = df['Amount'].sum()
        daily_avg = total_spent / days
        proj_monthly = daily_avg * 30
        
        advice = f"📈 **AI Analysis:** You are making ₹{salary:,.2f}/mo. Currently, your highest burn category is **{highest_cat} (₹{highest_amt:,.2f})**.\n\n"
        
        if monthly_goal_burden > 0:
            advice += f"🎯 **Your Goals:** To hit your planned goals, you need to save ₹{monthly_goal_burden:,.2f}/mo.\n"
            safenet = salary - proj_monthly
            if safenet < monthly_goal_burden:
                advice += f"🚨 **WARNING**: At a projected monthly spend of ₹{proj_monthly:,.2f}, you are only saving ₹{safenet:,.2f}/mo. You will NOT reach your goals. **Recommendation:** You must cut your {highest_cat} spending by at least 30% to course-correct!"
            else:
                advice += f"✅ **ON TRACK**: You are saving ₹{safenet:,.2f}/mo, which perfectly covers your goals! Keep it up!"
        else:
            if proj_monthly > salary and salary > 0:
                advice += f"🚨 **CRITICAL**: You are projected to spend ₹{proj_monthly:,.2f} this month, which puts you in extreme debt against your ₹{salary:,.2f} salary! Cut {highest_cat} right now."
            else:
                advice += "No goals detected. Try adding a goal to get better actionable advice!"
        return advice

    if "save" in user_input or "saving" in user_input:
        return f"Since your salary is logged at ₹{salary:,.2f}, try saving 20% (₹{(salary*0.2):,.2f}) upfront as soon as you get paid."
        
    elif "future" in user_input or "spend" in user_input or "lose" in user_input or "profit" in user_input or "predict" in user_input:
        if df.empty:
            return "I need more data to predict your future spending."
            
        df['Date'] = pd.to_datetime(df['Date'])
        days_active = (df['Date'].max() - df['Date'].min()).days
        if days_active < 1: days_active = 1
        
        total_spend = df['Amount'].sum()
        daily_avg = total_spend / days_active
        monthly_proj = daily_avg * 30
        
        budget, _ = predict_next_month_budget(username)
        budget = max(budget, 1)
        
        if monthly_proj > budget:
            return f"⚠️ **FUTURE PREDICTION:** If you continue spending like this (₹{daily_avg:,.2f}/day), your projected monthly spend will be **₹{monthly_proj:,.2f}**. You will exceed your target budget and face a **loss/overspend** of ₹{(monthly_proj - budget):,.2f}!"
        else:
            return f"✅ **FUTURE PREDICTION:** If you continue spending like this (₹{daily_avg:,.2f}/day), your projected monthly spend is **₹{monthly_proj:,.2f}**. You will stay under your target and **save/profit** ₹{(budget - monthly_proj):,.2f}!"
            
    elif "budget" in user_input:
        budget, _ = predict_next_month_budget(username)
        return f"Based on my AI curve analysis, you should target a budget of ₹{budget:,.2f} for next month."
    elif "food" in user_input or "eat" in user_input:
        if not df.empty and 'Food' in df['Category'].values:
            food_spent = df[df['Category'] == 'Food']['Amount'].sum()
            return f"You've spent ₹{food_spent:,.2f} on Food overall. Meal prepping is a great way to lower this!"
        return "Food is often a huge expense. Try cooking more at home."
    elif "highest" in user_input or "most" in user_input or "top" in user_input:
        if not df.empty:
            cat_totals = df.groupby('Category')['Amount'].sum()
            highest_cat = cat_totals.idxmax()
            return f"Your highest spending category right now is **{highest_cat}**."
        return "I need more data to tell you your highest expense."
    elif "hello" in user_input or "hi" in user_input or "hey" in user_input:
        return "Hello! I am your AI Financial Advisor. Ask me for tips on saving, your highest expenses, or your budget prediction!"
    else:
        return "I'm still learning! Right now, you can ask me about your 'budget', how to 'save' money, or your 'highest' expenses."
