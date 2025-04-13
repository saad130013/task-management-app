
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="نظام إدارة المهام", layout="wide")

if "users_db" not in st.session_state:
    st.session_state.users_db = pd.DataFrame([
        {"اسم المستخدم": "ahmed", "الاسم الكامل": "أحمد", "الدور": "موظف", "كلمة المرور": "1234"},
        {"اسم المستخدم": "sara", "الاسم الكامل": "سارة", "الدور": "مشرف", "كلمة المرور": "1234"},
        {"اسم المستخدم": "khaled", "الاسم الكامل": "خالد", "الدور": "مدير", "كلمة المرور": "1234"},
    ])

users_df = st.session_state.users_db

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

def logout():
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.rerun()

if not st.session_state.logged_in:
    st.title("تسجيل الدخول")
    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        user_row = users_df[users_df["اسم المستخدم"] == username]
        if not user_row.empty and user_row.iloc[0]["كلمة المرور"] == password:
            st.session_state.logged_in = True
            st.session_state.current_user = user_row.iloc[0].to_dict()
            st.success("تم تسجيل الدخول بنجاح")
            st.rerun()
        else:
            st.error("اسم المستخدم أو كلمة المرور غير صحيحة")
else:
    user = st.session_state.current_user
    st.sidebar.title("نظام إدارة المهام")
    menu = st.sidebar.radio("القائمة", ["لوحة التحكم", "المهام", "المستخدمين", "الإعدادات"])
    if st.sidebar.button("تسجيل الخروج"):
        logout()

    if "tasks" not in st.session_state:
        st.session_state.tasks = pd.DataFrame([
            {"رقم": "ZWA-T1", "المهمة": "مهمة تجريبية", "الموظف": "أحمد", "الحالة": "جارية", "الأولوية": "متوسطة", "تاريخ البدء": "2024-04-10", "تاريخ النهاية": "2024-04-20"},
        ])
    tasks = st.session_state.tasks

    def highlight(row):
        color = ""
        if row["الحالة"] == "منجزة":
            color = "background-color: #d4edda;"
        elif row["الحالة"] == "متأخرة":
            color = "background-color: #f8d7da;"
        elif row["الحالة"] == "جارية":
            color = "background-color: #fff3cd;"
        return [color]*len(row)

    if menu == "لوحة التحكم":
        st.title("لوحة التحكم")
        st.dataframe(tasks.style.apply(highlight, axis=1), use_container_width=True)

    elif menu == "المهام":
        st.title("المهام")
        st.dataframe(tasks.style.apply(highlight, axis=1), use_container_width=True)

    elif menu == "المستخدمين" and user["الدور"] == "مدير":
        st.title("إدارة المستخدمين")
        st.dataframe(users_df.drop(columns=["كلمة المرور"]), use_container_width=True)

        st.subheader("إضافة مستخدم")
        with st.form("add_user"):
            col1, col2 = st.columns(2)
            with col1:
                new_username = st.text_input("اسم المستخدم")
                full_name = st.text_input("الاسم الكامل")
            with col2:
                new_password = st.text_input("كلمة المرور", type="password")
                role = st.selectbox("الدور", ["موظف", "مشرف", "مدير"])
            submitted = st.form_submit_button("إضافة")
            if submitted:
                if new_username in users_df["اسم المستخدم"].values:
                    st.warning("اسم المستخدم موجود مسبقاً.")
                else:
                    new_row = {"اسم المستخدم": new_username, "الاسم الكامل": full_name, "كلمة المرور": new_password, "الدور": role}
                    st.session_state.users_db = pd.concat([users_df, pd.DataFrame([new_row])], ignore_index=True)
                    st.success("تمت إضافة المستخدم.")
                    st.rerun()

        st.subheader("تعديل / حذف مستخدم")
        selected_user = st.selectbox("اختر المستخدم", users_df["اسم المستخدم"])
        user_row = users_df[users_df["اسم المستخدم"] == selected_user].iloc[0]

        with st.form("edit_user"):
            col1, col2 = st.columns(2)
            with col1:
                updated_fullname = st.text_input("الاسم الكامل", user_row["الاسم الكامل"])
                updated_role = st.selectbox("الدور", ["موظف", "مشرف", "مدير"], index=["موظف", "مشرف", "مدير"].index(user_row["الدور"]))
            with col2:
                updated_password = st.text_input("كلمة المرور", user_row["كلمة المرور"])
            col3, col4 = st.columns(2)
            update_btn = col3.form_submit_button("تحديث")
            delete_btn = col4.form_submit_button("حذف")

            if update_btn:
                idx = users_df[users_df["اسم المستخدم"] == selected_user].index[0]
                st.session_state.users_db.at[idx, "الاسم الكامل"] = updated_fullname
                st.session_state.users_db.at[idx, "الدور"] = updated_role
                st.session_state.users_db.at[idx, "كلمة المرور"] = updated_password
                st.success("تم تحديث المستخدم.")
                st.rerun()

            if delete_btn:
                st.session_state.users_db = users_df[users_df["اسم المستخدم"] != selected_user]
                st.warning("تم حذف المستخدم.")
                st.rerun()
