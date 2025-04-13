import streamlit as st
import pandas as pd

st.set_page_config(page_title="نظام إدارة المهام", layout="wide")

st.markdown(
    """
    <style>
    .sidebar .sidebar-content {
        background-color: #1f1f2e;
        color: white;
    }
    .css-18e3th9 {
        padding: 2rem 1rem 2rem 1rem;
    }
    .stButton > button {
        color: white;
        background: #f48024;
        font-weight: bold;
    }
    .header {
        font-size: 30px;
        font-weight: bold;
        margin-bottom: 20px;
        color: #333;
    }
    .task-table td {
        padding: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# الشريط الجانبي
st.sidebar.title("نظام إدارة المهام")
menu = st.sidebar.radio("القائمة الرئيسية", ["لوحة التحكم", "المهام", "التقويم", "المستخدمين", "الإعدادات"])

# بيانات المهام التجريبية
df = pd.DataFrame([
    {"رقم": "ZWA-T8", "المهمة": "دليل مرئي", "الموظف": "أحمد", "الحالة": "جارية", "الأولوية": "متوسطة", "تاريخ البدء": "2024-04-10", "تاريخ النهاية": "2024-04-20"},
    {"رقم": "ZWA-T9", "المهمة": "تخطيط الواجهة", "الموظف": "سارة", "الحالة": "متأخرة", "الأولوية": "عالية", "تاريخ البدء": "2024-04-01", "تاريخ النهاية": "2024-04-15"},
    {"رقم": "ZWA-T10", "المهمة": "تصميم UI", "الموظف": "خالد", "الحالة": "منجزة", "الأولوية": "منخفضة", "تاريخ البدء": "2024-03-25", "تاريخ النهاية": "2024-04-05"},
])

def highlight(row):
    color = ""
    if row["الحالة"] == "منجزة":
        color = "background-color: #d4edda;"  # أخضر فاتح
    elif row["الحالة"] == "متأخرة":
        color = "background-color: #f8d7da;"  # أحمر فاتح
    elif row["الحالة"] == "جارية":
        color = "background-color: #fff3cd;"  # أصفر فاتح
    return [color] * len(row)

if menu == "المهام":
    st.markdown('<div class="header">المهام الحالية</div>', unsafe_allow_html=True)
    st.dataframe(df.style.apply(highlight, axis=1), use_container_width=True)
    st.markdown("###")
    st.button("إضافة مهمة جديدة")
    st.button("تعديل")
    st.button("حذف")
    st.button("تصفية")

elif menu == "لوحة التحكم":
    st.markdown('<div class="header">لوحة التحكم</div>', unsafe_allow_html=True)
    st.success("مرحباً بك في لوحة تحكم الإدارة.")
    st.metric("إجمالي المهام", len(df))
    st.metric("عدد المهام الجارية", len(df[df["الحالة"] == "جارية"]))
    st.metric("عدد المهام المنجزة", len(df[df["الحالة"] == "منجزة"]))
    st.metric("عدد المهام المتأخرة", len(df[df["الحالة"] == "متأخرة"]))

elif menu == "التقويم":
    st.markdown('<div class="header">التقويم</div>', unsafe_allow_html=True)
    st.info("سيتم إضافة عرض تقويم المهام قريباً.")

elif menu == "المستخدمين":
    st.markdown('<div class="header">المستخدمين</div>', unsafe_allow_html=True)
    st.info("إدارة المستخدمين قيد التطوير.")

elif menu == "الإعدادات":
    st.markdown('<div class="header">الإعدادات العامة</div>', unsafe_allow_html=True)
    st.info("هنا يمكنك ضبط إعدادات النظام.")