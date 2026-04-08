import streamlit as st
import pandas as pd
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="Audio Automator 2.0", layout="wide")

# --- 2. KHỞI TẠO DỮ LIỆU MẪU (SESSION STATE) ---
if 'tasks' not in st.session_state:
    # Mô phỏng danh sách URL từ CMS
    st.session_state.tasks = [
        {"Tên bài": "Khu phi quân sự Demilitarized Zone", "URL GỐC": "https://cms.tatinta.com/dest/...1", "Status": "Waiting", "Error": ""},
        {"Tên bài": "Trung tâm lặn biển Busan", "URL GỐC": "https://cms.tatinta.com/dest/...2", "Status": "Waiting", "Error": ""},
        {"Tên bài": "Nhà hàng hải sản Porta Marina", "URL GỐC": "https://cms.tatinta.com/dest/...3", "Status": "Waiting", "Error": ""},
        {"Tên bài": "Làng Pháp Petite France", "URL GỐC": "https://cms.tatinta.com/dest/...4", "Status": "Waiting", "Error": ""},
        {"Tên bài": "Covera Cruise - Tiffany 21", "URL GỐC": "https://cms.tatinta.com/dest/...5", "Status": "Waiting", "Error": ""},
    ] * 20 # Nhân bản lên 100 dòng để test

if 'is_running' not in st.session_state:
    st.session_state.is_running = False

# --- 3. HÀM XỬ LÝ LÕI (MÔ PHỎNG TTS/MIX/UPLOAD) ---
def process_audio_task(index, task):
    # Mô phỏng thời gian tải và xử lý audio (2-4 giây)
    time.sleep(random.uniform(2, 4)) 
    
    # Random tỷ lệ Success/Failed để test UI
    is_success = random.choice([True, True, True, False]) 
    
    if is_success:
        return index, "Success", ""
    else:
        return index, "Failed", "TTS/Mix/Upload"

# --- 4. GIAO DIỆN CHÍNH ---
st.title("🎧 Dashboard")

# Tính toán các con số thống kê
df = pd.DataFrame(st.session_state.tasks)
total = len(df)
success = len(df[df["Status"] == "Success"])
failed = len(df[df["Status"] == "Failed"])
pending = len(df[df["Status"] == "Waiting"])
progress_pct = int(((success + failed) / total) * 100) if total > 0 else 0

# Cột Layout: Sidebar cho tiến độ, Main cho bảng dữ liệu
col_sidebar, col_main = st.columns([1, 3])

with col_sidebar:
    st.markdown("### 📊 Theo Dõi Tiến Độ")
    
    if st.session_state.is_running:
        st.info("🔄 Đang chạy 2 luồng song song...")
    else:
        st.write("Sẵn sàng chạy.")

    # Thanh tiến trình
    st.progress(progress_pct / 100)
    st.markdown(f"<h1 style='color: #ff4b4b;'>{progress_pct}%</h1>", unsafe_allow_html=True)
    
    # Thống kê chi tiết
    st.write(f"📌 **{success + failed} / {total}** đã xử lý")
    st.write(f"✅ **{success}** Success | ❌ **{failed}** Error | ⏳ **{pending}** Waiting")
    
    st.markdown("---")
    
    # Nút điều khiển
    start_btn = st.button("🚀 Bắt đầu Deploy", use_container_width=True)
    
    st.markdown("### 📋 Copy URLs")
    st.button(f"Copy {pending} URL đang Waiting", use_container_width=True)
    st.button(f"Copy {success} URL Success", use_container_width=True)
    st.button(f"Copy {failed} URL Failed", use_container_width=True)

with col_main:
    # Hiển thị bảng dữ liệu trực tiếp cập nhật
    table_placeholder = st.empty()
    table_placeholder.dataframe(df, use_container_width=True, height=600)

# --- 5. LOGIC CHẠY ĐA LUỒNG ---
if start_btn and not st.session_state.is_running:
    st.session_state.is_running = True
    st.rerun() # Refresh UI để hiện Status "Đang chạy"

if st.session_state.is_running:
    pending_tasks = [(i, task) for i, task in enumerate(st.session_state.tasks) if task["Status"] == "Waiting"]
    
    # Sử dụng ThreadPoolExecutor để chạy 2 luồng song song
    with ThreadPoolExecutor(max_workers=2) as executor:
        # Gửi task vào pool
        futures = {executor.submit(process_audio_task, i, task): i for i, task in pending_tasks}
        
        for future in as_completed(futures):
            idx = futures[future]
            try:
                index, status, error_msg = future.result()
                # Cập nhật Status
                st.session_state.tasks[index]["Status"] = status
                st.session_state.tasks[index]["Error"] = error_msg
                
                # Update UI realtime (ở mức cơ bản của Streamlit)
                # Streamlit reruns liên tục có thể gây giật, nên ở thực tế ta update batch hoặc dùng placeholder
            except Exception as e:
                st.session_state.tasks[idx]["Status"] = "Failed"
                st.session_state.tasks[idx]["Error"] = "Error hệ thống"
            
            # Buộc giao diện tải lại để cập nhật số liệu
            st.rerun()

    # Hoàn thành
    st.session_state.is_running = False
    st.success("Hoàn thành toàn bộ tiến trình!")
    time.sleep(2)
    st.rerun()