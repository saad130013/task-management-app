import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from bidi.algorithm import get_display
import arabic_reshaper
from io import BytesIO

st.set_page_config(page_title="نظام إدارة المهام", layout="wide")

if "tasks" not in st.session_state:
    st.session_state.tasks = pd.DataFrame([
        {"رقم": "T1", "المهمة": "تحليل البيانات", "الموظف": "أحمد", "الحالة": "جارية"},
        {"رقم": "T2", "المهمة": "إعداد التقارير", "الموظف": "سارة", "الحالة": "منجزة"},
    ])

tasks = st.session_state.tasks

st.title("تقرير المهام")
st.dataframe(tasks)

if st.button("تحميل PDF بالعربية"):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50
    pdf.setFont("Helvetica", 14)
    reshaped_title = arabic_reshaper.reshape("تقرير المهام")
    bidi_title = get_display(reshaped_title)
    pdf.drawRightString(550, y, bidi_title)
    y -= 40

    for _, row in tasks.iterrows():
        row_text = f"{row['رقم']} - {row['المهمة']} - {row['الموظف']} - {row['الحالة']}"
        reshaped = arabic_reshaper.reshape(row_text)
        bidi_text = get_display(reshaped)
        pdf.drawRightString(550, y, bidi_text)
        y -= 30

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    st.download_button("تحميل الملف", buffer, file_name="tasks_arabic.pdf")