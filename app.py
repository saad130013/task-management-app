
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from io import BytesIO
from fpdf import FPDF

# بيانات المستخدمين (تُخزن مؤقتاً داخل الجلسة)
if "users" not in st.session_state:
    st.session_state.users = {
        "ahmed": {"الاسم": "أحمد", "الدور": "موظف", "كلمة_المرور": "1234"},
        "sara": {"الاسم": "سارة", "الدور": "مشرف", "كلمة_المرور": "1234"},
        "khaled": {"الاسم": "خالد", "الدور": "مدير", "كلمة_المرور": "1234"},
    }

users = st.session_state.users

# واجهة تسجيل الدخول
st.sidebar.title("تسجيل الدخول")
username = st.sidebar.text_input("اسم المستخدم")
password = st.sidebar.text_input("كلمة المرور", type="password")

if username in users and password == users[username]["كلمة_المرور"]:
    user = users[username]
    st.sidebar.success(f"مرحباً {user['الاسم']}! ({user['الدور']})")

    # اختيار الصفحة بعد تسجيل الدخول
    page = st.sidebar.radio("اختر الصفحة", [
        "لوحة المهام", "لوحة الإدارة", "إضافة مهمة", "تحليلات", "تصدير",
        "تقويم المهام", "أرشفة", "تقييم", "سجل النشاط", "تغيير كلمة المرور"
    ])

    if "tasks" not in st.session_state:
        st.session_state.tasks = pd.DataFrame(columns=["الموظف", "المهمة", "الحالة", "نسبة", "تاريخ النهاية", "مرفق"])
    if "logs" not in st.session_state:
        st.session_state.logs = []

    tasks = st.session_state.tasks

    def log_action(text):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.logs.append(f"{timestamp} - {user['الاسم']} - {text}")

    if page == "لوحة المهام":
        st.title("لوحة المهام الخاصة بك")
        employee_tasks = tasks[tasks["الموظف"] == user["الاسم"]]
        st.dataframe(employee_tasks.drop(columns=["مرفق"]))
        for i, row in employee_tasks.iterrows():
            if row["مرفق"]:
                st.markdown(f"**مرفق:** [{row['المهمة']}]({row['مرفق'].name})")

    elif page == "لوحة الإدارة" and user["الدور"] in ["مشرف", "مدير"]:
        st.title("لوحة تحكم الإدارة")
        st.dataframe(tasks.drop(columns=["مرفق"]))
        st.metric("إجمالي المهام", len(tasks))
        if not tasks.empty:
            st.metric("نسبة الإنجاز الكلية", f"{tasks['نسبة'].mean():.2f}%")

    elif page == "إضافة مهمة" and user["الدور"] in ["مشرف", "مدير"]:
        st.title("إضافة مهمة جديدة")
        with st.form("task_form"):
            الموظف = st.selectbox("اختر الموظف", [u["الاسم"] for u in users.values()])
            المهمة = st.text_input("عنوان المهمة")
            الحالة = st.selectbox("الحالة", ["جارية", "منجزة", "متأخرة"])
            النسبة = st.slider("نسبة الإنجاز", 0, 100, 0)
            تاريخ_النهاية = st.date_input("تاريخ نهاية المهمة")
            المرفق = st.file_uploader("أرفق ملف للمهمة (اختياري)")
            submitted = st.form_submit_button("إضافة")
            if submitted:
                new_task = {
                    "الموظف": الموظف,
                    "المهمة": المهمة,
                    "الحالة": الحالة,
                    "نسبة": النسبة,
                    "تاريخ النهاية": pd.to_datetime(تاريخ_النهاية),
                    "مرفق": المرفق
                }
                st.session_state.tasks = pd.concat([st.session_state.tasks, pd.DataFrame([new_task])], ignore_index=True)
                log_action(f"أضاف مهمة جديدة للموظف {الموظف}: {المهمة}")
                st.success("تمت إضافة المهمة!")

    elif page == "تغيير كلمة المرور":
        st.title("تغيير كلمة المرور")
        old_pw = st.text_input("كلمة المرور الحالية", type="password")
        new_pw = st.text_input("كلمة المرور الجديدة", type="password")
        confirm_pw = st.text_input("تأكيد كلمة المرور الجديدة", type="password")
        if st.button("تغيير"):
            if old_pw != users[username]["كلمة_المرور"]:
                st.error("كلمة المرور الحالية غير صحيحة.")
            elif new_pw != confirm_pw:
                st.error("كلمتا المرور الجديدتان غير متطابقتين.")
            elif len(new_pw) < 4:
                st.warning("يجب أن تتكون كلمة المرور من 4 أحرف أو أكثر.")
            else:
                users[username]["كلمة_المرور"] = new_pw
                st.success("تم تغيير كلمة المرور بنجاح.")

    elif page == "سجل النشاط":
        st.title("سجل النشاط")
        for log in st.session_state.logs[::-1]:
            st.text(log)

    elif page == "تقييم":
        st.title("تقييم الموظفين حسب الإنجاز")
        if not tasks.empty:
            rating = tasks.groupby("الموظف")["نسبة"].mean().reset_index()
            rating = rating.sort_values(by="نسبة", ascending=False)
            st.dataframe(rating)

    elif page == "أرشفة":
        st.title("أرشفة المهام المنجزة أو القديمة")
        archived = tasks[(tasks["الحالة"] == "منجزة") | (tasks["تاريخ النهاية"] < datetime.today())]
        st.dataframe(archived.drop(columns=["مرفق"]))

    elif page == "تقويم المهام":
        st.title("المهام لهذا الأسبوع")
        today = datetime.today()
        end_week = today + timedelta(days=7)
        week_tasks = tasks[(tasks["تاريخ النهاية"] >= today) & (tasks["تاريخ النهاية"] <= end_week)]
        st.dataframe(week_tasks.drop(columns=["مرفق"]))

    elif page == "تحليلات":
        st.title("تحليلات")
        if not tasks.empty:
            chart1 = px.pie(tasks, names="الحالة", title="نسبة المهام حسب الحالة")
            st.plotly_chart(chart1)
            chart2 = px.bar(tasks, x="الموظف", y="نسبة", color="الموظف", title="مقارنة الإنجاز")
            st.plotly_chart(chart2)

    elif page == "تصدير":
        st.title("تصدير المهام")
        export_data = tasks.drop(columns=["مرفق"])
        excel_buffer = BytesIO()
        export_data.to_excel(excel_buffer, index=False)
        st.download_button("تحميل كـ Excel", data=excel_buffer.getvalue(), file_name="المهام.xlsx")
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="تقرير المهام", ln=1, align="C")
        pdf.ln(10)
        for index, row in export_data.iterrows():
            line = f"{row['الموظف']} - {row['المهمة']} - {row['الحالة']} - {row['نسبة']}% - {row['تاريخ النهاية'].date()}"
            pdf.cell(200, 10, txt=line, ln=1, align="R")
        pdf_buffer = BytesIO()
        pdf.output(pdf_buffer)
        st.download_button("تحميل كـ PDF", data=pdf_buffer.getvalue(), file_name="المهام.pdf")

else:
    st.sidebar.warning("يرجى إدخال اسم المستخدم وكلمة المرور الصحيحة.")
