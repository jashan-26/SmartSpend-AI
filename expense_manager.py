import re
import pandas as pd
from data_handler import load_data, save_expense

CATEGORIES = ["Food", "Travel", "Shopping", "Bills", "Others"]

KEYWORD_MAPPING = {
    "Food": ["food", "lunch", "dinner", "breakfast", "grocery", "groceries", "restaurant", "cafe", "coffee", "snack", "pizza", "burger", "mcdonalds", "kfc", "starbucks"],
    "Travel": ["travel", "gas", "fuel", "uber", "lyft", "taxi", "bus", "train", "flight", "ticket", "metro", "subway"],
    "Shopping": ["shopping", "clothes", "shoes", "amazon", "electronics", "mall", "phone", "laptop", "gift"],
    "Bills": ["bill", "electricity", "water", "gas", "internet", "wifi", "rent", "mortgage", "subscription", "netflix", "spotify"]
}

def auto_categorize(description: str) -> str:
    """
    Categorizes the expense based on keywords in the description.
    """
    desc_lower = description.lower()
    
    # Split description into words and check
    words = re.findall(r'\b\w+\b', desc_lower)
    
    for word in words:
        for category, keywords in KEYWORD_MAPPING.items():
            if word in keywords:
                return category
    
    # Check for direct substring matches if no word match
    for category, keywords in KEYWORD_MAPPING.items():
        for keyword in keywords:
            if keyword in desc_lower:
                return category
                
    return "Others"

def get_category_totals(username):
    """
    Returns total expenses grouped by category
    """
    df = load_data(username)
    if df.empty:
        return {}
    totals = df.groupby('Category')['Amount'].sum().to_dict()
    return totals

def get_monthly_totals(username):
    """
    Returns monthly spending trends
    """
    df = load_data(username)
    if df.empty:
        return {}
        
    df['Date'] = pd.to_datetime(df['Date'])
    # Format as YYYY-MM
    df['Month'] = df['Date'].dt.to_period('M').dt.strftime('%b %Y')
    totals = df.groupby('Month')['Amount'].sum().to_dict()
    return totals

def get_highest_spending_category(username):
    df = load_data(username)
    if df.empty:
        return None, 0
    
    cat_totals = df.groupby('Category')['Amount'].sum()
    if cat_totals.empty:
        return None, 0
        
    highest_cat = cat_totals.idxmax()
    highest_amt = cat_totals.max()
    return highest_cat, highest_amt
