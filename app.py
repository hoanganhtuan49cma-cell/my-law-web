import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Cấu hình trang
st.set_page_config(page_title="Sổ tay Pháp luật Cá nhân", layout="wide")

# Kết nối Google Sheets
# Bạn sẽ dán link sheet vào phần Secrets của Streamlit
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    return conn.read(ttl="0") # ttl="0" để luôn tải dữ liệu mới nhất

df = load_data()

st.title("⚖️ Sổ tay Quản lý Văn bản Pháp luật")

# Chia 2 cột: Nhập liệu và Tra cứu
col_in, col_out = st.columns([1, 2])

with col_in:
    st.header("Thêm văn bản mới")
    with st.form("add_form", clear_on_submit=True):
        s_hieu = st.text_input("Số hiệu văn bản")
        ten = st.text_input("Tên văn bản")
        t_trang = st.selectbox("Tình trạng", ["Còn hiệu lực", "Hết hiệu lực một phần", "Hết hiệu lực toàn bộ"])
        thay_the = st.text_input("Sửa đổi bởi/Thay thế bởi")
        ghi_chu = st.text_area("Ghi chú quan trọng")
        
        if st.form_submit_button("Lưu văn bản"):
            new_row = pd.DataFrame([[s_hieu, ten, t_trang, thay_the, ghi_chu]], 
                                    columns=["Số hiệu", "Tên", "Tình trạng", "Thay thế bởi", "Ghi chú"])
            updated_df = pd.concat([df, new_row], ignore_index=True)
            
            # Ghi đè lại file Google Sheets
            conn.update(data=updated_df)
            st.success("Đã lưu thành công!")
            st.rerun()

with col_out:
    st.header("Danh mục tra cứu")
    search = st.text_input("🔍 Tìm theo số hiệu hoặc tên...")
    
    view_df = df.copy()
    if search:
        view_df = view_df[view_df['Số hiệu'].str.contains(search, case=False) | 
                          view_df['Tên'].str.contains(search, case=False)]
    
    # Hiển thị bảng
    st.dataframe(view_df, use_container_width=True, hide_index=True)
    
    # Hiển thị chi tiết từng mục
    for _, row in view_df.iterrows():
        color = "🟢" if row['Tình trạng'] == "Còn hiệu lực" else "🟠" if row['Tình trạng'] == "Hết hiệu lực một phần" else "🔴"
        with st.expander(f"{color} {row['Số hiệu']} - {row['Tên']}"):
            st.write(f"**Tình trạng:** {row['Tình trạng']}")
            st.write(f"**Liên quan:** {row['Thay thế bởi']}")
            st.info(f"**Ghi chú:** {row['Ghi chú']}")
