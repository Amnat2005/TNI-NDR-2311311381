import streamlit as st
st.set_page_config(layout="wide")

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from sklearn.linear_model import LinearRegression
import numpy as np

# ใช้ฟอนต์ภาษาไทย
matplotlib.rcParams['font.family'] = 'Tahoma'

# แปลงชื่อเดือนจากไทยเป็นตัวเลข
thai_months = {
    "ม.ค.": "01", "ก.พ.": "02", "มี.ค.": "03", "เม.ย.": "04",
    "พ.ค.": "05", "มิ.ย.": "06", "ก.ค.": "07", "ส.ค.": "08",
    "ก.ย.": "09", "ต.ค.": "10", "พ.ย.": "11", "ธ.ค.": "12"
}

def convert_thai_date(thai_date_str):
    for th, num in thai_months.items():
        if th in thai_date_str:
            day, month_th, year_th = thai_date_str.replace(",", "").split()
            month = thai_months[month_th]
            year = int(year_th) - 543
            return f"{year}-{month}-{int(day):02d}"
    return None

@st.cache_data
def load_data():
    df = pd.read_excel(
        r"C:\Users\LENOVO\OneDrive\เดสก์ท็อป\WEB-TRUE\TRUE-SET-19May2025-6M (1).xlsx", 
        sheet_name="TRUE", skiprows=1
    )
    df.columns = [
        "วันที่", "ราคาเปิด", "ราคาสูงสุด", "ราคาต่ำสุด", "ราคาเฉลี่ย", "ราคาปิด",
        "เปลี่ยนแปลง", "เปลี่ยนแปลง(%)", "ปริมาณ(พันหุ้น)", "มูลค่า(ล้านบาท)",
        "SET Index", "SET เปลี่ยนแปลง(%)"
    ]
    df = df[~df["วันที่"].isna() & ~df["วันที่"].str.contains("วันที่")]
    df["วันที่"] = df["วันที่"].apply(convert_thai_date)
    df["วันที่"] = pd.to_datetime(df["วันที่"])
    df = df.dropna()
    df = df.sort_values("วันที่")
    return df

df = load_data()

st.title("กราฟแนวโน้มราคาปิดหุ้น TRUE (6 เดือนย้อนหลัง)")

X = df["วันที่"].map(pd.Timestamp.toordinal).values.reshape(-1, 1)
y = df["ราคาปิด"].values
model = LinearRegression()
model.fit(X, y)
trend = model.predict(X)

fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(df["วันที่"], y, label="ราคาปิดจริง")
ax.plot(df["วันที่"], trend, label="แนวโน้ม (Linear Regression)", linestyle="--", color="red")
ax.set_xlabel("วันที่")
ax.set_ylabel("ราคาปิด (บาท)")
ax.set_title("แนวโน้มราคาปิดหุ้น TRUE")
ax.legend()
ax.grid(True)
st.pyplot(fig)