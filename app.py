
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# إعداد صفحة Streamlit
st.set_page_config(page_title="نظام إدارة المهام", layout="wide")

# بيانات المستخدمين التجريبية
if "users" not in st.session_state:
    st.session_state.users = {
        "ahmed": {"الاسم": "أحمد", "الدور": "موظف", "كلمة_المرور": "1234"},
        "sara": {"الاسم": "سارة", "الدور": "مشرف", "كلمة_المرور": "1234"},
        "khaled": {"الاسم": "خالد", "الدور": "مدير", "كلمة_المرور": "1234"},
    }

users = st.session_state.users

# تسجيل الخروج
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

def logout():
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.experimental_rerun()

# تسجيل الدخول
if not st.session_state.logged_in:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Example.jpg/800px-Example.jpg", width=150)
    st.title("تسجيل الدخول إلى نظام المهام")
    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        if username in users and password == users[username]["كلمة_المرور"]:
            st.session_state.logged_in = True
            st.session_state.current_user = users[username]
            st.success("تم تسجيل الدخول بنجاح!")
            st.markdown("<audio autoplay><source src='https://www.soundjay.com/buttons/sounds/button-29.mp3' type='audio/mpeg'></audio>", unsafe_allow_html=True)
            st.experimental_rerun()
        else:
            st.error("بيانات الدخول غير صحيحة")
else:
    user = st.session_state.current_user
    st.sidebar.markdown(f"مرحباً، **{user['الاسم']}** ({user['الدور']})")
    if st.sidebar.button("تسجيل الخروج"):
        logout()

    if "tasks" not in st.session_state:
        st.session_state.tasks = pd.DataFrame([
            {"الموظف": "أحمد", "المهمة": "جرد الأصول", "الحالة": "جارية", "النسبة": 50, "تاريخ النهاية": "2025-04-18"},
            {"الموظف": "سارة", "المهمة": "رفع تقرير", "الحالة": "منجزة", "النسبة": 100, "تاريخ النهاية": "2025-04-10"},
            {"الموظف": "خالد", "المهمة": "تحديث البيانات", "الحالة": "متأخرة", "النسبة": 30, "تاريخ النهاية": "2025-04-14"},
        ])
    tasks = st.session_state.tasks
    tasks["تاريخ النهاية"] = pd.to_datetime(tasks["تاريخ النهاية"])

    # شاشة المدير
    if user["الدور"] == "مدير":
        st.title("لوحة معلومات المدير")
        col1, col2, col3 = st.columns(3)
        col1.metric("المهام الجارية", len(tasks[tasks["الحالة"] == "جارية"]))
        col2.metric("المهام المنجزة", len(tasks[tasks["الحالة"] == "منجزة"]))
        col3.metric("المهام المتأخرة", len(tasks[tasks["الحالة"] == "متأخرة"]))
        st.markdown("---")
        st.subheader("جميع المهام")
        def highlight_status(row):
            color = ""
            if row["الحالة"] == "منجزة":
                color = "background-color: lightgreen"
            elif row["الحالة"] == "متأخرة":
                color = "background-color: lightcoral"
            elif row["الحالة"] == "جارية":
                color = "background-color: lightyellow"
            return [color]*len(row)
        st.dataframe(tasks.style.apply(highlight_status, axis=1))

    # شاشة الموظف
    elif user["الدور"] == "موظف":
        st.title("مهامي")
        user_tasks = tasks[tasks["الموظف"] == user["الاسم"]]
        st.subheader("المهام الواجب تنفيذها")
        st.dataframe(user_tasks[user_tasks["الحالة"] == "جارية"])
        st.subheader("المهام المتأخرة")
        st.dataframe(user_tasks[user_tasks["الحالة"] == "متأخرة"])
        st.subheader("المهام المنجزة")
        st.dataframe(user_tasks[user_tasks["الحالة"] == "منجزة"])

    # شاشة المشرف
    else:
        st.title("لوحة المشرف")
        st.subheader("كل المهام")
        st.dataframe(tasks)

