import gradio as gr
import pandas as pd
from predictor import predict_expense  # your function

def predict(input_value):
    result = predict_expense(input_value)
    return f"Predicted Expense: ₹{result}"

iface = gr.Interface(
    fn=predict,
    inputs=gr.Number(label="Enter Amount"),
    outputs="text",
    title="SmartSpend AI",
    description="AI-powered expense prediction"
)

iface.launch()
