import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Electric Meter & Bill Dashboard",
    page_icon="⚡",
    layout="wide",
)

# ----------------- SECURITY LOCK -----------------
# Yahan apna pasandida password set karein (Jaise: "Ravinder@123")
APP_PASSWORD = "Ravi@2026" 

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Security Lock")
    st.markdown("Is app ko kholne ke liye password darj karein:")
    
    pwd = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if pwd == APP_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Galat Password! Kripya sahi password dalein.")
    st.stop() # Agar password galat hai to app yahi ruk jayegi
# -------------------------------------------------

# (Neeche aapka purana app ka code hai)
DATA_FILE = "meter_data.csv"

def load_data():
  if os.path.exists(DATA_FILE):
    return pd.read_csv(DATA_FILE)
  else:
    df = pd.DataFrame(columns=[
        "Date",
        "Meter_Reading",
        "Units_Consumed",
        "Rate_Per_Unit",
        "Daily_Bill_Amount",
        "Notes",
    ])
    return df

df = load_data()

st.title("⚡ Daily Electric Meter & Bill Tracker")
st.markdown("Roz apni meter reading bhariye aur automatic bill analysis dekhiye!")

st.sidebar.header("📝 Nayi Entry Karein")

with st.sidebar.form("entry_form", clear_on_submit=True):
  selected_date = st.date_input("Date")
  current_reading = st.number_input("Aaj ki Meter Reading", min_value=0.0, format="%.2f")
  rate_per_unit = st.number_input("Rate Per Unit (₹)", min_value=0.0, value=8.50, format="%.2f")
  notes = st.text_input("Notes (Optional)", "Regular entry")
  submit_button = st.form_submit_button(label="Save Entry")

if submit_button:
  if not df.empty:
    last_row = df.iloc[-1]
    last_reading = float(last_row["Meter_Reading"])
    units_consumed = current_reading - last_reading
    if units_consumed < 0:
      units_consumed = 0
      st.error("Reading pichli se kam nahi ho sakti!")
  else:
    last_reading = 0.0
    units_consumed = 0.0

  daily_bill = units_consumed * rate_per_unit

  new_data = {
      "Date": str(selected_date),
      "Meter_Reading": current_reading,
      "Units_Consumed": round(units_consumed, 2),
      "Rate_Per_Unit": rate_per_unit,
      "Daily_Bill_Amount": round(daily_bill, 2),
      "Notes": notes,
  }

  df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
  df.to_csv(DATA_FILE, index=False)
  st.sidebar.success("✅ Entry successfully save ho gayi!")
  st.rerun()

if not df.empty:
  st.sidebar.divider()
  if st.sidebar.button("❌ Delete Last Entry"):
    df = df.iloc[:-1] 
    df.to_csv(DATA_FILE, index=False)
    st.sidebar.success("🗑️ Aakhri entry delete ho gayi!")
    st.rerun()

  total_units = df["Units_Consumed"].sum()
  total_bill = df["Daily_Bill_Amount"].sum()
  last_recorded_reading = df.iloc[-1]["Meter_Reading"]

  col1, col2, col3 = st.columns(3)
  col1.metric("📊 Total Units Consumed", f"{total_units:.2f} Units")
  col2.metric("💰 Total Bill Amount", f"₹ {total_bill:.2f}")
  col3.metric("📈 Latest Meter Reading", f"{last_recorded_reading:.2f}")

  st.divider()

  st.subheader("📊 Daily Consumption Trend")
  if len(df) > 1:
    chart_data = df.set_index("Date")[["Units_Consumed"]]
    st.line_chart(chart_data)
  else:
    st.info("Chart dekhne ke liye kam se kam 2 entries honi chahiye.")

  st.subheader("📋 Saari Entries ka Record")
  st.dataframe(df, use_container_width=True)

  csv = df.to_csv(index=False).encode("utf-8")
  st.download_button(
      label="📥 Download Excel/CSV Backup",
      data=csv,
      file_name="electricity_bill_backup.csv",
      mime="text/csv",
  )
else:
  st.warning("Abhi tak koi entry nahi hai. Left sidebar se apni pehli reading add karein!")
