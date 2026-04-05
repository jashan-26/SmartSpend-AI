# SmartSpend AI: Personal Expense Analyzer & Budget SaaS

SmartSpend AI is an offline-first, machine learning-powered personal finance platform built with Python and Streamlit. It has been structurally upgraded into a multi-user environment, featuring context-aware artificial intelligence, intelligent bulk data parsing, and predictive budgeting all without sending your data to external APIs.

## 🚀 Features

* **Multi-User Security**: A built-in authentication system. All user CSV datasets (expenses, bills, profiles) are automatically generated and strictly isolated. 
* **Smart CSV Compiler**: Drag and drop "Wide-Format" bank exports. The parser automatically pieces together corrupt dates, mathematically melts distinct category columns (Food, Travel, Bills) into native database rows, and strips unused metrics.
* **Goal-Oriented Planners**: Set up goals (e.g. `Buy iPhone in 6 months`). The system calculates your active monthly salary, subtracts daily extrapolations of your expenses, and mathematically determines if you are overspending or on-track to reach your goal.
* **Subscription Sentinels**: Input recurring bills and due dates; the dashboard will automatically trigger homepage alerts when any bill is due within 5 days!
* **Predictive ML Modeling**: A `scikit-learn` Linear Regression engine analyzes historical monthly data to forecast your budget ceilings.
* **Context-Aware Offline AI**: An advanced local Chatbot that seamlessly cross-references your active Salary, Goals, and Expenses. Ask *"Am I going to hit my goals?"* and the AI will scan your highest spending category and instruct you to cut it by X percentage!

## 📦 File Ecosystem
* `main.py`: The frontend UI handling routing, authentication, file uploading, and Dashboard visualizations using Plotly's beautiful Mint Green graphics.
* `data_handler.py`: The data backend managing `data/` directory CSV isolation, user registration logic, and the Smart CSV Matrix Melter.
* `expense_manager.py`: The parsing and categorizing algorithms grouping your spending trends.
* `predictor.py`: The Machine Learning modeling and the Heuristics-based Artificial Intelligence context engine.
* `sample_dataset.csv`: An exact "Wide-Format" template you can drag and drop into the app to see the Smart Parser working in action.

## 🛠️ Installation & Execution

1. Clone this repository (or download the files).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Streamlit Dashboard:
   ```bash
   python -m streamlit run main.py
   ```
4. Sign up with a new Username and Password on the landing page, and drag the `sample_dataset.csv` file into the Bulk Uploader to begin analyzing!
