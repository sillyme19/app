import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
from datetime import datetime

# File name for saving CSV
DEFAULT_CSV_FILE = "expenses.csv"

# Function to load CSV data
def load_csv(file_name):
    if os.path.exists(file_name):
        return pd.read_csv(file_name)
    else:
        return pd.DataFrame(columns=["Date", "Reason", "Amount"])

# Function to save CSV data
def save_csv(df, file_name):
    df.to_csv(file_name, index=False)

# Function to display expenses for a selected month
def display_expenses(df, month, year):
    date_filter = (df['Date'].str.startswith(f'{year}-{month:02d}'))
    filtered_expenses = df[date_filter]
    
    if filtered_expenses.empty:
        st.write("No expenses recorded for this month.")
    else:
        st.write(f"Expenses for {month}-{year}:")
        st.dataframe(filtered_expenses)

# Function to plot the expense graph
def plot_expense_graph(df, option):
    if df.empty:
        st.warning("No data available to plot.")
        return

    df['Date'] = pd.to_datetime(df['Date'])
    if option == "Daily":
        grouped_data = df.groupby('Date')['Amount'].sum()
        title = "Daily Expense"
    elif option == "Monthly":
        grouped_data = df.groupby(df['Date'].dt.to_period('M'))['Amount'].sum()
        grouped_data.index = grouped_data.index.to_timestamp()
        title = "Monthly Expense"
    elif option == "Yearly":
        grouped_data = df.groupby(df['Date'].dt.year)['Amount'].sum()
        title = "Yearly Expense"
    else:
        st.error("Invalid option selected.")
        return

    plt.figure(figsize=(10, 6))
    plt.plot(grouped_data.index, grouped_data.values, marker='o')
    plt.title(title, fontsize=16)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Amount', fontsize=12)
    plt.grid()
    st.pyplot(plt)

# Streamlit App
st.title("Monthly Expense Management")

# User Options
st.sidebar.title("Options")
action = st.sidebar.selectbox(
    "What do you want to do?",
    ["Create New CSV", "Upload Existing CSV"]
)

# Expense data management
df_expenses = pd.DataFrame(columns=["Date", "Reason", "Amount"])

if action == "Create New CSV":
    if st.sidebar.button("Create CSV File"):
        save_csv(df_expenses, DEFAULT_CSV_FILE)
        st.success(f"New CSV file '{DEFAULT_CSV_FILE}' created successfully!")

elif action == "Upload Existing CSV":
    uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])
    if uploaded_file:
        df_expenses = pd.read_csv(uploaded_file)
        st.success("CSV file uploaded successfully!")


# Load existing data if file exists
if os.path.exists(DEFAULT_CSV_FILE) and action != "Upload Existing CSV":
    df_expenses = load_csv(DEFAULT_CSV_FILE)
    

# Input Section
if not df_expenses.empty or action == "Create New CSV":
    st.header("Add Expenses")

    # Calendar popup to select a date
    selected_date = st.date_input("Select Date", datetime.today())

    # Get the month and year of the selected date
    selected_month = selected_date.month
    selected_year = selected_date.year

    # Input fields for expense details
    expense_reason = st.text_input("Reason for expenditure", "")
    expense_amount = st.number_input("Amount", min_value=0.0, step=0.01)

    # Submit button to add the expense
    if st.button("Add Expense"):
        if expense_reason and expense_amount > 0:
            new_expense = {
                'Date': selected_date.strftime('%Y-%m-%d'),
                'Reason': expense_reason,
                'Amount': expense_amount
            }
            df_expenses = pd.concat([df_expenses, pd.DataFrame([new_expense])], ignore_index=True)
            st.success(f"Expense of {expense_amount} added successfully for {selected_date.strftime('%Y-%m-%d')}.")
            save_csv(df_expenses, DEFAULT_CSV_FILE)
        else:
            st.warning("Please provide both reason and amount.")

    # Display the expenses for the selected month
    display_expenses(df_expenses, selected_month, selected_year)

    # Graph options
    st.header("Expense Tracker Graph")
    graph_option = st.selectbox("Select Graph Option", ["Daily", "Monthly", "Yearly"])

    if st.button("Show Graph"):
        plot_expense_graph(df_expenses, graph_option)

    # Save updated CSV
    st.header("Save Updated Data")
    save_csv(df_expenses, DEFAULT_CSV_FILE)
    st.download_button(
        label="Download Updated CSV",
        data=df_expenses.to_csv(index=False),
        file_name="updated_expenses.csv",
        mime="text/csv"
    )
else:
    st.warning("No expense data available. Please create or upload a CSV file.")
