import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="Electricity Meter Reading App", page_icon="⚡", layout="centered")

st.title("⚡ Electricity Meter Reading Tracker")

DATA_FILE = "meter_data.csv"

# Load or Initialize Data
if os.path.exists(DATA_FILE):
    try:
        df = pd.read_csv(DATA_FILE)
    except Exception as e:
        df = pd.DataFrame(columns=["Date", "Reading", "Units Consumed", "Estimated Bill (₹)", "Notes"])
else:
    df = pd.DataFrame(columns=["Date", "Reading", "Units Consumed", "Estimated Bill (₹)", "Notes"])

# Sidebar Menu
menu = st.sidebar.selectbox("Menu", ["📊 Dashboard & Records", "➕ Add New Reading", "⚙️ Rate Calculator Settings"])

# Rate per unit (Default assumption e.g., ₹7 per unit)
RATE_PER_UNIT = 7.0

if menu == "📊 Dashboard & Records":
    st.header("📊 Reading Records & History")
    
    if not df.empty:
        # Show metrics
        latest_reading = df.iloc[-1]["Reading"]
        total_units = df["Units Consumed"].sum()
        total_bill = df["Estimated Bill (₹)"].sum()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("📌 Latest Reading", f"{latest_reading} units")
        col2.metric("⚡ Total Units", f"{total_units} units")
        col3.metric("💰 Total Est. Bill", f"₹ {total_bill:,.2f}")
        
        st.divider()
        st.dataframe(df, use_container_width=True)
        
        # Download button for CSV
        csv_data = df.to_csv(index=False).encode('utf-8')
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
            # Calculate units consumed from last entry
            if not df.empty:
                last_reading = df.iloc[-1]["Reading"]
                units_consumed = current_reading - last_reading
                if units_consumed < 0:
                    units_consumed = 0 # Safety check if meter resets
            else:
                units_consumed = current_reading # First entry
                
            est_bill = units_consumed * RATE_PER_UNIT
            
            new_row = {
                "Date": reading_date.strftime("%Y-%m-%d"),
                "Reading": current_reading,
                "Units Consumed": units_consumed,
                "Estimated Bill (₹)": est_bill,
                "Notes": notes
            }
            
            # Append and save
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            
            st.success(f"✅ Reading saved successfully! Consumed: {units_consumed} units | Est. Bill: ₹{est_bill:.2f}")

elif menu == "⚙️ Rate Calculator Settings":
    st.header("⚙️ Settings & Info")
    st.write(f"**Current Rate per Unit:** ₹ {RATE_PER_UNIT} / unit")
    st.info("Aap yahan apne bijli ke slab ke hisaब se rate customize bhi kar sakte hain.")
