import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import google.generativeai as genai

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Hệ thống Pháp luật Cá nhân", layout="wide")

# --- CẤU HÌNH AI (Thay bằng API Key của bạn) ---
genai.configure(api_key="CHÈN_API_KEY_CỦA_BẠN_VÀO_ĐÂY")
model = genai.GenerativeModel('gemini-1.5-flash')

# --- KẾT NỐI DỮ LIỆU (Google Sheets) ---
# Link Google Sheet của bạn (Phải để ở chế độ "Anyone with the link can view")
url = "LINK_GOOGLE_SHEET_CỦA_BẠN"

conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    return conn.read(spreadsheet=url, usecols=[0, 1, 2, 3, 4])

# Khởi tạo hoặc tải dữ liệu
df = load_data()

st.title("⚖️ Trợ lý Văn bản Pháp luật Vĩnh viễn")

# --- PHẦN 1: AI PHÂN TÍCH NHANH ---
st.subheader("🤖 Trợ lý AI Phân tích")
with st.expander("Dán nội dung văn bản để AI đọc giúp bạn"):
    raw_text = st.text_area("Nội dung (Phần hiệu lực thi hành):", height=150)
    if st.button("Phân tích bằng AI"):
        prompt = f"Phân tích văn bản sau và trả về các thông tin: Số hiệu, Tên, Tình trạng hiệu lực, Văn bản thay thế, Ghi chú. Nội dung: {raw_text}"
        response = model.generate_content(prompt)
        st.write(response.text)

st.divider()

# --- PHẦN 2: QUẢN LÝ DANH MỤC ---
col_form, col_view = st.columns([1, 2])

with col_form:
    st.header("Cập nhật mới")
    with st.form("add_form", clear_on_submit=True):
        s_hieu = st.text_input("Số hiệu")
        ten = st.text_input("Tên văn bản")
        t_trang = st.selectbox("Tình trạng", ["Còn hiệu lực", "Hết hiệu lực một phần", "Hết hiệu lực toàn bộ"])
        thay_the = st.text_input("Văn bản liên quan")
        ghi_chu = st.text_area("Ghi chú")
        
        submit = st.form_submit_button("Lưu dữ liệu")
        
        if submit:
            # Tạo dòng mới
            new_row = pd.DataFrame([[s_hieu, ten, t_trang, thay_the, ghi_chu]], 
                                    columns=["Số hiệu", "Tên", "Tình trạng", "Thay thế bởi", "Ghi chú"])
            updated_df = pd.concat([df, new_row], ignore_index=True)
            
            # Cập nhật trực tiếp lên Google Sheets
            conn.update(spreadsheet=url, data=updated_df)
            st.success("Đã cập nhật lên Google Sheets thành công!")
            st.cache_data.clear() # Xóa cache để load lại dữ liệu mới

with col_view:
    st.header("Tra cứu văn bản")
    search = st.text_input("Tìm kiếm số hiệu hoặc tên...")
    
    display_df = df.copy()
    if search:
        display_df = display_df[display_df['Số hiệu'].str.contains(search, case=False) | 
                                display_df['Tên'].str.contains(search, case=False)]
    
    # Định dạng bảng màu sắc
    def style_status(row):
        color = 'background-color: #d4edda' if row['Tình trạng'] == 'Còn hiệu lực' else \
                'background-color: #fff3cd' if row['Tình trạng'] == 'Hết hiệu lực một phần' else \
                'background-color: #f8d7da'
        return [color] * len(row)

    st.dataframe(display_df.style.apply(style_status, axis=1), use_container_width=True)

# Nút làm mới dữ liệu
if st.button("🔄 Làm mới dữ liệu từ Sheets"):
    st.cache_data.clear()
    st.rerun()
