🎧 Audio Automator 2.0 (macOS Edition)
Audio Automator là một công cụ tự động hóa mạnh mẽ dành cho các nhà sáng tạo nội dung và quản trị viên CMS (như Tatinta). Công cụ này giúp chuyển đổi văn bản từ URL bài viết thành file Audio chuyên nghiệp có lồng nhạc nền và đẩy trực tiếp lên server.

✨ Tính năng nổi bật
Automatic TTS: Tự động quét nội dung Tiếng Việt & Tiếng Anh từ link CMS.

Smart Audio Mixing: Sử dụng FFmpeg để lồng nhạc nền (bgm.mp3) với âm lượng 10% cực mượt.

FastAPI Backend: Xử lý bất đồng bộ (Async), hỗ trợ hàng đợi (Queue) chống nghẽn mạng.

Streamlit Dashboard: Giao diện trực quan, theo dõi tiến độ theo thời gian thực.

Bypass ORB/CORS: Tích hợp trình phát nhạc "vượt rào" bảo mật trình duyệt Chrome/Edge.

🛠 Bộ công cụ kỹ thuật (Tech Stack)
Ngôn ngữ: Python 3.9+

Backend: FastAPI, Uvicorn, HTTPX.

Frontend: Streamlit.

Xử lý Audio: Edge TTS (Microsoft), FFmpeg.

Database: SQLite (Lưu trữ trạng thái task).

📥 Cài đặt (Dành cho macOS)
1. Cài đặt FFmpeg (Bắt buộc để mix nhạc)
Mở Terminal và cài đặt thông qua Homebrew:

Bash
brew install ffmpeg
2. Cài đặt thư viện Python
Bash
pip install fastapi uvicorn streamlit httpx edge-tts beautifulsoup4 pandas
3. Chuẩn bị file nhạc nền
Đảm bảo bạn có file nhạc nền tên là bgm.mp3 nằm cùng thư mục với file code backend.

🚀 Cách vận hành
Hệ thống cần chạy song song hai cửa sổ Terminal:

Bước 1: Khởi động Backend
Bash
python server.py
Backend sẽ chạy tại cổng http://localhost:8000

Bước 2: Khởi động Dashboard
Bash
streamlit run app.py
Giao diện sẽ tự động mở trên trình duyệt tại http://localhost:8501

📖 Hướng dẫn sử dụng
Cấu hình: Nhập Token Bearer (lấy từ hệ thống CMS) để xác thực.
Nhập dữ liệu: Dán danh sách URL bài viết từ CMS vào ô văn bản.

Deploy: Nhấn nút 🚀 Bắt đầu Deploy. Hệ thống sẽ tự động làm mọi khâu (TTS -> Mix nhạc -> Upload -> Gắn link).

⚠️ Lưu ý quan trọng
Token: Token CMS thường có thời hạn. Nếu gặp lỗi 401 Unauthorized, hãy cập nhật Token mới.
Mạng: Đảm bảo máy tính có kết nối Internet ổn định để gọi API Microsoft Edge TTS.

Bảo mật: Không đẩy file automator.db hoặc Token thật lên GitHub (Sử dụng .gitignore).
-----------------------------------
Developed by Lộc (LocNT) - Video Editor & Technical Content Manager