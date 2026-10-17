import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="Electricity Meter Reading App", page_icon="⚡", layout="centered")

st.title("⚡ Electricity Meter Reading Tracker")

DATA_FILE = "meter_data.csv"
CONFIG_FILE = "rate_config.txt"

# Function to get saved rate per unit
def get_rate_per_unit():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                content = f.read().strip()
                if content:
                    return float(content)
        except:
            pass
    return 7.0  # Default rate if not set

# Function to save rate per unit permanently
def save_rate_per_unit(rate):
    with open(CONFIG_FILE, "w") as f:
        f.write(str(rate))

CURRENT_RATE = get_rate_per_unit()

# Load or Initialize Data
expected_cols = ["Date", "Reading", "Units Consumed", "Estimated Bill (₹)", "Notes"]
if os.path.exists(DATA_FILE):
    try:
        df = pd.read_csv(DATA_FILE)
        for col in expected_cols:
            if col not in df.columns:
                df = pd.DataFrame(columns=expected_cols)
                break
    except Exception:
        df = pd.DataFrame(columns=expected_cols)
else:
    df = pd.DataFrame(columns=expected_cols)

# Ensure Date is datetime and sort properly
if not df.empty and "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
    df = df.sort_values(by="Date", ascending=True).reset_index(drop=True)
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

# Sidebar Menu
menu = st.sidebar.selectbox("Menu", ["📊 Dashboard & Records", "➕ Add New Reading", "⚙️ Rate Calculator Settings"])

if menu == "📊 Dashboard & Records":
    st.header("📊 Reading Records & History")
    
    if not df.empty and len(df) > 0:
        # Recalculate units and bills using the saved custom rate
        df["Reading"] = pd.to_numeric(df["Reading"], errors="coerce")
        df["Units Consumed"] = df["Reading"].diff().fillna(0)
        df.loc[df["Units Consumed"] < 0, "Units Consumed"] = 0
        df["Estimated Bill (₹)"] = df["Units Consumed"] * CURRENT_RATE
        
        df.to_csv(DATA_FILE, index=False)
        
        latest_reading = df.iloc[-1]["Reading"]
        total_units = df["Units Consumed"].sum()
        total_bill = df["Estimated Bill (₹)"].sum()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("📌 Latest Reading", f"{int(latest_reading) if pd.notnull(latest_reading) else 0} units")
        col2.metric("⚡ Total Units", f"{int(total_units)} units")
        col3.metric("💰 Total Est. Bill", f"₹ {total_bill:,.2f}")
        
        st.divider()
        st.info(f"ℹ️ Current Calculation Rate: **₹ {CURRENT_RATE} / unit**")
        
        display_df = df.sort_values(by="Date", ascending=False).reset_index(drop=True)
        st.dataframe(display_df, use_container_width=True)
        
        csv_data = display_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Data as CSV",
            data=csv_data,
            file_name="electricity_records.csv",
            mime="text/csv"
        )
    else:
        st.info("📭 Abhi tak koi reading add nahi ki gayi hai. 'Add New Reading' par click karke pehli entry dalein.")

elif menu == "➕ Add New Reading":
    st.header("➕ Add Meter Reading")
    
    with st.form("reading_form", clear_on_submit=True):
        reading_date = st.date_input("Reading Date", value=datetime.today())
        current_reading = st.number_input("Current Meter Reading (Units)", min_value=0.0, step=1.0)
        notes = st.text_input("Notes (Optional - e.g., Month name)")
        
        submit_btn = st.form_submit_button("💾 Save Reading")
        
        if submit_btn:
            date_str = reading_date.strftime("%Y-%m-%d")
            
            if not df.empty and "Date" in df.columns:
                df = df[df["Date"] != date_str]
                
            new_row = {
                "Date": date_str,
                "Reading": current_reading,
                "Units Consumed": 0.0,
                "Estimated Bill (₹)": 0.0,
                "Notes": notes
            }
            
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            
            df["Date"] = pd.to_datetime(df["Date"])
            df = df.sort_values(by="Date", ascending=True).reset_index(drop=True)
            
            df["Reading"] = pd.to_numeric(df["Reading"], errors="coerce")
            df["Units Consumed"] = df["Reading"].diff().fillna(0)
            df.loc[df["Units Consumed"] < 0, "Units Consumed"] = 0
            df["Estimated Bill (₹)"] = df["Units Consumed"] * CURRENT_RATE
            
            df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
            df.to_csv(DATA_FILE, index=False)
            
            st.success("✅ Reading saved and calculated successfully!")

elif menu == "⚙️ Rate Calculator Settings":
    st.header("⚙️ Rate Calculator Settings")
    st.write(f"Current saved rate per unit is: **₹ {CURRENT_RATE} / unit**")
    
    with st.form("rate_form"):
        new_rate = st.number_input("Enter New Rate per Unit (₹)", min_value=0.1, value=float(CURRENT_RATE), step=0.5)
        save_rate_btn = st.form_submit_button("💾 Save Permanent Rate")
        
        if save_rate_btn:
            save_rate_per_unit(new_rate)
            st.success(f"✅ Rate successfully updated to ₹ {new_rate} per unit! Yeh ab permanent save ho gaya hai.")
            st.rerun()
