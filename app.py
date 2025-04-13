
import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from io import BytesIO

st.set_page_config(page_title="نظام إدارة المهام المتكامل", layout="wide")

# تسجيل الدخول
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "users_db" not in st.session_state:
    st.session_state.users_db = pd.DataFrame([
        {"اسم المستخدم": "admin", "الاسم الكامل": "مدير", "الدور": "مدير", "كلمة المرور": "1234"},
        {"اسم المستخدم": "sara", "الاسم الكامل": "سارة", "الدور": "مشرف", "كلمة المرور": "1234"},
        {"اسم المستخدم": "ahmed", "الاسم الكامل": "أحمد", "الدور": "موظف", "كلمة المرور": "1234"},
    ])
if "tasks" not in st.session_state:
    st.session_state.tasks = pd.DataFrame(columns=["رقم", "المهمة", "الموظف", "الحالة", "الأولوية", "تاريخ البدء", "تاريخ النهاية", "مرفق"])

def logout():
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.rerun()

if not st.session_state.logged_in:
    st.title("تسجيل الدخول")
    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        user_row = st.session_state.users_db[st.session_state.users_db["اسم المستخدم"] == username]
        if not user_row.empty and user_row.iloc[0]["كلمة المرور"] == password:
            st.session_state.logged_in = True
            st.session_state.current_user = user_row.iloc[0].to_dict()
            st.success("تم تسجيل الدخول")
            st.rerun()
        else:
            st.error("بيانات الدخول غير صحيحة")
else:
    user = st.session_state.current_user
    st.sidebar.title("القائمة الرئيسية")
    menu = st.sidebar.radio("اذهب إلى:", ["لوحة التحكم", "المهام", "التقارير", "المستخدمين", "الإعدادات"])
    if st.sidebar.button("تسجيل الخروج"):
        logout()

    tasks = st.session_state.tasks

    def highlight(row):
        color = ""
        if row["الحالة"] == "منجزة":
            color = "background-color: #d4edda"
        elif row["الحالة"] == "متأخرة":
            color = "background-color: #f8d7da"
        elif row["الحالة"] == "جارية":
            color = "background-color: #fff3cd"
        return [color] * len(row)

    if menu == "لوحة التحكم":
        st.title("لوحة تحكم المدير")
        st.metric("عدد المهام", len(tasks))
        st.metric("عدد المهام الجارية", len(tasks[tasks["الحالة"] == "جارية"]))
        st.metric("عدد المهام المنجزة", len(tasks[tasks["الحالة"] == "منجزة"]))
        st.metric("عدد المهام المتأخرة", len(tasks[tasks["الحالة"] == "متأخرة"]))
        st.dataframe(tasks.style.apply(highlight, axis=1), use_container_width=True)

    elif menu == "المهام":
        st.title("إدارة المهام")
        st.dataframe(tasks.style.apply(highlight, axis=1), use_container_width=True)
        with st.form("add_task"):
            col1, col2 = st.columns(2)
            with col1:
                task_name = st.text_input("عنوان المهمة")
                assignee = st.selectbox("اختر الموظف", st.session_state.users_db["الاسم الكامل"])
                priority = st.selectbox("الأولوية", ["عالية", "متوسطة", "منخفضة"])
            with col2:
                status = st.selectbox("الحالة", ["جارية", "منجزة", "متأخرة"])
                start = st.date_input("تاريخ البدء")
                end = st.date_input("تاريخ النهاية")
            attachment = st.file_uploader("أرفق ملف")
            submitted = st.form_submit_button("إضافة")
            if submitted:
                new_task = {
                    "رقم": f"TASK-{len(tasks)+1}",
                    "المهمة": task_name,
                    "الموظف": assignee,
                    "الحالة": status,
                    "الأولوية": priority,
                    "تاريخ البدء": str(start),
                    "تاريخ النهاية": str(end),
                    "مرفق": attachment.name if attachment else ""
                }
                st.session_state.tasks = pd.concat([tasks, pd.DataFrame([new_task])], ignore_index=True)
                st.success("تمت إضافة المهمة")
                st.rerun()

    elif menu == "التقارير":
        st.title("تصدير المهام")
        export_data = tasks.drop(columns=["مرفق"])
        excel_file = BytesIO()
        export_data.to_excel(excel_file, index=False)
        st.download_button("تحميل Excel", data=excel_file.getvalue(), file_name="tasks.xlsx")

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="تقرير المهام", ln=True, align="C")
        for i, row in export_data.iterrows():
            pdf.cell(200, 10, txt=f"{row['رقم']} - {row['المهمة']} - {row['الموظف']} - {row['الحالة']}", ln=True, align="R")
        pdf_output = BytesIO()
        pdf.output(pdf_output)
        st.download_button("تحميل PDF", data=pdf_output.getvalue(), file_name="tasks.pdf")

    elif menu == "المستخدمين" and user["الدور"] == "مدير":
        st.title("إدارة المستخدمين")
        users_df = st.session_state.users_db
        st.dataframe(users_df.drop(columns=["كلمة المرور"]), use_container_width=True)
        with st.form("add_user"):
            st.subheader("إضافة مستخدم جديد")
            u1, u2 = st.columns(2)
            with u1:
                username = st.text_input("اسم المستخدم")
                fullname = st.text_input("الاسم الكامل")
            with u2:
                password = st.text_input("كلمة المرور", type="password")
                role = st.selectbox("الدور", ["موظف", "مشرف", "مدير"])
            if st.form_submit_button("إضافة"):
                if username in users_df["اسم المستخدم"].values:
                    st.warning("اسم المستخدم موجود")
                else:
                    new_user = {"اسم المستخدم": username, "الاسم الكامل": fullname, "كلمة المرور": password, "الدور": role}
                    st.session_state.users_db = pd.concat([users_df, pd.DataFrame([new_user])], ignore_index=True)
                    st.success("تمت إضافة المستخدم")
                    st.rerun()

    elif menu == "الإعدادات":
        st.title("الإعدادات العامة")
        st.info("خيارات الإعداد سيتم إضافتها لاحقًا.")

