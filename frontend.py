import streamlit as st
import pandas as pd
import requests
import time

# FIX TRỊ TẬN GỐC Error MAC: Dùng thẳng IP 127.0.0.1 thay vì localhost
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Audio Automator 2.0", layout="wide")
st.title("🎧 Dashboard")

token_input = st.text_input("🔑 Import Bearer Token (from CMS):", type="password")

with st.expander("Add new URL", expanded=True):
    url_input = st.text_area("Import a list of URLs (one URL per line):", height=150)
    if st.button("🚀 Deploy"):
        if not token_input:
            st.error("⚠️ You forgot to input the Token!")
        else:
            urls = [url.strip() for url in url_input.split('\n') if url.strip()]
            if urls:
                try:
                    payload = {"urls": urls, "token": token_input.strip()}
                    response = requests.post(f"{API_URL}/start-job", json=payload, timeout=5)
                    if response.status_code == 200:
                        st.success("Job successfully pushed to Backend!")
                        time.sleep(1)
                except Exception as e:
                    st.error(f"Job submission error (Backend not enabled or incorrect port): {e}")

st.markdown("---")

api_data = None
api_error = None

try:
    status_response = requests.get(f"{API_URL}/status", timeout=10)
    if status_response.status_code == 200:
        api_data = status_response.json()
    else:
        api_error = f"Error HTTP {status_response.status_code}"
except Exception as e:
    api_error = str(e)

if api_error:
    # HIỂN THỊ CHÍNH XÁC Error RA MÀN HÌNH ĐỂ KHÔNG PHẢI ĐOÁN MÒ
    st.error(f"⚠️ Mất kết nối Backend. Lý do: {api_error}")
    st.info("Vui lòng đảm bảo uvicorn đang chạy ở Terminal.")
else:
    if api_data:
        df = pd.DataFrame(api_data)
        total = len(df)
        success = len(df[df["Status"] == "Success"])
        failed = len(df[df["Status"] == "Failed"])
        pending = len(df[df["Status"] == "Waiting"])
        processing = len(df[df["Status"] == "Processing"])
        
        progress_pct = int(((success + failed) / total) * 100) if total > 0 else 0

        col_sidebar, col_main = st.columns([1, 3])

        with col_sidebar:
            st.markdown("### 📊 Progress")
            if processing > 0 or pending > 0:
                st.info("🔄 Backend processing...")
            else:
                st.success("Completed!")

            st.progress(progress_pct / 100)
            st.markdown(f"<h1 style='color: #ff4b4b;'>{progress_pct}%</h1>", unsafe_allow_html=True)
            
            st.write(f"✅ **{success}** Success")
            st.write(f"❌ **{failed}** Error")
            st.write(f"⏳ **{pending + processing}** Waiting/Processing")

        with col_main:
            st.dataframe(df, use_container_width=True, height=500)
            
        if processing > 0 or pending > 0:
            time.sleep(2)
            if hasattr(st, 'rerun'):
                st.rerun()
            else:
                st.experimental_rerun()
    else:
        st.info("No data. Please add URL to begin.")