# RetailPulse

## AI-Powered Customer Analytics & Demand Forecasting Platform

RetailPulse is a Python-based retail analytics dashboard for sales analysis, demand prediction, inventory insights, and customer analytics.

## Features

- Overview Dashboard
- Product Demand Prediction
- Machine Learning Model Performance
- Sales Analytics
- Inventory Insights
- Customer Analytics

## Technology Stack

- Python
- Streamlit
- Pandas
- NumPy
- Scikit-learn
- Plotly

## Project Structure

- app/app.py
- data/processed/RetailPulse_Processed.csv
- models/demand_model.pkl
- models/demand_feature_columns.pkl
- requirements.txt

## Installation

Install dependencies:

    pip install -r requirements.txt

Run the application:

    streamlit run app/app.py

## Machine Learning

The demand prediction module uses a trained Random Forest regression model.

## Dataset Limitations

- Dataset contains aggregated retail information.
- Customer analytics display existing dataset labels.
- Estimated profit assumes a 25% margin.
- Predictions for bulk orders may be less reliable.
- Currency is GBP (£).

## Project Objective

To demonstrate how data analytics and machine learning can support retail business decisions.

## Author

Developed as a Data Science & Analytics internship project.
