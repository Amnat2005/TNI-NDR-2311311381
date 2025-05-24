import streamlit as st

st.set_page_config(layout="wide")

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from sklearn.linear_model import LinearRegression
import numpy as np

# ตั้งค่าฟอนต์ให้รองรับภาษาไทย
matplotlib.rcParams['font.family'] = 'Tahoma'

thai_months = {
    "ม.ค.": "01", "ก.พ.": "02", "มี.ค.": "03", "เม.ย.": "04",
    "พ.ค.": "05", "มิ.ย.": "06", "ก.ค.": "07", "ส.ค.": "08",
    "ก.ย.": "09", "ต.ค.": "10", "พ.ย.": "11", "ธ.ค.": "12"
}

thai_months_full = {
    1: "มกราคม", 2: "กุมภาพันธ์", 3: "มีนาคม", 4: "เมษายน",
    5: "พฤษภาคม", 6: "มิถุนายน", 7: "กรกฎาคม", 8: "สิงหาคม",
    9: "กันยายน", 10: "ตุลาคม", 11: "พฤศจิกายน", 12: "ธันวาคม"
}

def convert_thai_date(thai_date_str):
    for th, num in thai_months.items():
        if th in thai_date_str:
            day, month_th, year_th = thai_date_str.replace(",", "").split()
            month = thai_months[month_th]
            year = int(year_th) - 543
            return f"{year}-{month}-{int(day):02d}"
    return None

def thai_month_name(period):
    month = period.month
    year = period.year + 543
    return f"{thai_months_full[month]} {year}"

@st.cache_data
def load_data():
    df = pd.read_excel(
        r"C:\\Users\\LENOVO\\OneDrive\\เดสก์ท็อป\\WEB-TRUE\\TRUE-SET-19May2025-6M (1).xlsx",
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

def load_css(file_name):
    with open(file_name, encoding="utf-8") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# โหลด CSS จากไฟล์
load_css("style.css")

df = load_data()

st.title("สรุปข้อมูลหุ้น TRUE (6 เดือนย้อนหลัง)")

latest_row = df.iloc[-1]
delta_price = latest_row["เปลี่ยนแปลง"]
delta_percent = latest_row["เปลี่ยนแปลง(%)"]

col1, col2, col3 = st.columns([2, 2, 2])

with col1:
    st.metric(
        label="ราคาปิดล่าสุด",
        value=f"{latest_row['ราคาปิด']:.2f} บาท",
        delta=f"{delta_price:.2f} ({delta_percent:.2f}%)"
    )

with col2:
    st.metric("SET Index", f"{latest_row['SET Index']:.2f}")

with col3:
    st.metric("ปริมาณซื้อขาย", f"{latest_row['ปริมาณ(พันหุ้น)']:.0f} พันหุ้น")

st.subheader("กราฟราคาปิดและแนวโน้ม")

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

df["เดือน"] = df["วันที่"].dt.to_period("M")
all_months = sorted(df["เดือน"].unique())
month_list = all_months[-6:]

if "month_page" not in st.session_state:
    st.session_state.month_page = 0

current_month = month_list[st.session_state.month_page]
df_month = df[df["เดือน"] == current_month]

st.subheader(f"ราคาหุ้นย้อนหลัง: {thai_month_name(current_month)}")
st.dataframe(df_month[["วันที่", "ราคาปิด", "เปลี่ยนแปลง", "ปริมาณ(พันหุ้น)"]], use_container_width=True)

st.markdown("---")
st.markdown("# เลือกเดือน")

def render_pagination():
    current_page = st.session_state.month_page
    total_pages = len(month_list)
    cols = st.columns(total_pages + 2)

    with cols[0]:
        if st.button("⮜", key="prev_btn", disabled=(current_page == 0)):
            if current_page > 0:
                st.session_state.month_page -= 1

    for i in range(total_pages):
        with cols[i + 1]:
            if i == current_page:
                st.markdown(f'<div class="active-button">{i+1}</div>', unsafe_allow_html=True)
            else:
                if st.button(str(i + 1), key=f"month_btn_{i}"):
                    st.session_state.month_page = i

    with cols[-1]:
        if st.button("⮞", key="next_btn", disabled=(current_page == total_pages - 1)):
            if current_page < total_pages - 1:
                st.session_state.month_page += 1

render_pagination()
