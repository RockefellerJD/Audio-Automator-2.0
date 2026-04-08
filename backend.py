import asyncio
import edge_tts
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import sqlite3
import os
import time
import subprocess # THƯ VIỆN GỌI HỆ THỐNG MAC
from text_processor import chuan_hoa_am_thanh

app = FastAPI()

DB_FILE = "automator.db"
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tasks
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT, status TEXT, error_msg TEXT)''')
    conn.commit()
    conn.close()

init_db()

class JobRequest(BaseModel):
    urls: list[str]
    token: str

def get_clean_text(html, lang):
    if not html: return ""
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(separator='\n', strip=True)
    
    trigger = "Tổng quan về lịch sử:" if lang == "vi" else "Historical overview:"
    if trigger in text:
        text = text.split(trigger)[1]
    
    cutoffs = ["Giờ mở cửa:", "Giá vé:", "Địa chỉ:", "Opening hours:", "Ticket price:", "Address:"]
    for cutoff in cutoffs:
        if cutoff in text:
            part = text.split(cutoff)[0].strip()
            if len(part) > 20: text = part
            
    return chuan_hoa_am_thanh(text.strip(), lang)

# HÀM MIX NHẠC NỀN BẰNG FFMPEG (SIÊU NHANH & KHÔNG Error)
def mix_background_music(speech_file, bgm_file="bgm.mp3"):
    if not os.path.exists(bgm_file):
        print(f"CẢNH BÁO: Không tìm thấy file {bgm_file} trong thư mục. Bỏ qua lồng nhạc.", flush=True)
        return speech_file
        
    print("Đang mix nhạc nền (Volume 10%) bằng FFmpeg...", flush=True)
    output_file = speech_file.replace(".mp3", "_mixed.mp3")
    
    # Lệnh FFmpeg: Lặp vô hạn nhạc nền, giảm âm lượng 10%, cắt bằng đúng độ dài giọng đọc
    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-i", speech_file,
        "-stream_loop", "-1", "-i", bgm_file,
        "-filter_complex", "[1:a]volume=0.1[bg];[0:a][bg]amix=inputs=2:duration=first:dropout_transition=0",
        output_file
    ]
    
    try:
        subprocess.run(cmd, check=True)
        os.remove(speech_file) # Xóa file cũ chưa có nhạc
        os.rename(output_file, speech_file) # Đổi tên file đã mix thành file gốc
        print("-> Mix nhạc nền Success!", flush=True)
    except Exception as e:
        print(f"-> Error khi mix nhạc: {e}. Vẫn giữ nguyên file gốc.", flush=True)
        if os.path.exists(output_file):
            os.remove(output_file)
            
    return speech_file

async def process_single_url(task_id: int, cms_url: str, token: str):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        print(f"\n[{task_id}] === BẮT ĐẦU V11 (FFMPEG MIXER) ===", flush=True)
        c.execute("UPDATE tasks SET status='Processing' WHERE id=?", (task_id,))
        conn.commit()

        dest_id = cms_url.strip('/').split('/')[-1]
        api_url = f"https://api.tatinta.com/v1/destination/destination/{dest_id}"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "User-Agent": "Mozilla/5.0",
            "X-Requested-With": "XMLHttpRequest"
        }

        # 1. LẤY DỮ LIỆU TỪ SERVER
        res = requests.get(api_url, headers=headers, timeout=15)
        res.raise_for_status()
        full_data = res.json().get('data', {})

        text_vi = get_clean_text(full_data.get('content') or full_data.get('description'), "vi")
        
        translations_block = full_data.get('translations', {})
        en_data = translations_block.get('en', {})
        text_en = get_clean_text(en_data.get('content') or en_data.get('description'), "en")

        link_vi = ""
        link_en = ""

        # 2. XỬ LÝ AUDIO TIẾNG VIỆT
        if len(text_vi) > 15:
            print(f"[{task_id}] Đang làm Audio Tiếng Việt...", flush=True)
            file_vi = f"vi_{task_id}.mp3"
            await edge_tts.Communicate(text_vi, "vi-VN-HoaiMyNeural").save(file_vi)
            
            # Gọi lệnh lồng nhạc
            mix_background_music(file_vi, "bgm.mp3")
            
            with open(file_vi, 'rb') as f:
                b = f.read()
                if not b.startswith(b'ID3'): b = b'ID3\x03\x00\x00\x00\x00\x00\x00' + b
                up_res = requests.post("https://api.tatinta.com/v1/extra/upload/audio", headers=headers, files={'faudio': (f"vi-{int(time.time())}.mp3", b, 'audio/mpeg')})
                up_data = up_res.json().get('data', {})
                raw_link = up_data.get('url') or up_data.get('path') or up_data.get('filename') or ''
                link_vi = raw_link.replace('/uploads/', '/').replace('uploads/', '').lstrip('/')
            if os.path.exists(file_vi): os.remove(file_vi)

        # 3. XỬ LÝ AUDIO TIẾNG ANH
        if len(text_en) > 15:
            print(f"[{task_id}] Đang làm Audio Tiếng Anh...", flush=True)
            file_en = f"en_{task_id}.mp3"
            await edge_tts.Communicate(text_en, "en-US-JennyNeural").save(file_en)
            
            # Gọi lệnh lồng nhạc
            mix_background_music(file_en, "bgm.mp3")
            
            with open(file_en, 'rb') as f:
                b = f.read()
                if not b.startswith(b'ID3'): b = b'ID3\x03\x00\x00\x00\x00\x00\x00' + b
                up_res = requests.post("https://api.tatinta.com/v1/extra/upload/audio", headers=headers, files={'faudio': (f"en-{int(time.time())}.mp3", b, 'audio/mpeg')})
                up_data = up_res.json().get('data', {})
                raw_link = up_data.get('url') or up_data.get('path') or up_data.get('filename') or ''
                link_en = raw_link.replace('/uploads/', '/').replace('uploads/', '').lstrip('/')
            if os.path.exists(file_en): os.remove(file_en)

        # 4. GỬI LÊN CMS
        print(f"[{task_id}] Đang gắn link lên CMS bằng Minimal Patch...", flush=True)
        patch_payload = {}
        
        if link_vi: patch_payload['audio'] = link_vi
        if link_en:
            if 'en' not in translations_block: translations_block['en'] = {}
            translations_block['en']['audio'] = link_en
            patch_payload['translations'] = translations_block

        if patch_payload:
            patch_res = requests.patch(api_url, headers=headers, json=patch_payload, timeout=15)
            patch_res.raise_for_status()
            print(f"[{task_id}] === Success RỰC RỠ! ===", flush=True)
        else:
            raise ValueError("Không tạo được link Audio nào.")

        c.execute("UPDATE tasks SET status='Success', error_msg='' WHERE id=?", (task_id,))
        conn.commit()

    except Exception as e:
        c.execute("UPDATE tasks SET status='Failed', error_msg=? WHERE id=?", (str(e)[:250], task_id))
        conn.commit()
        print(f"[{task_id}] [Error]: {e}", flush=True)
    finally:
        conn.close()

async def process_urls_background(task_ids: list[int], urls: list[str], token: str):
    for task_id, url in zip(task_ids, urls):
        await process_single_url(task_id, url, token)

@app.post("/start-job")
async def start_job(data: JobRequest, background_tasks: BackgroundTasks):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    task_ids = []
    for url in data.urls:
        c.execute("INSERT INTO tasks (url, status, error_msg) VALUES (?, 'Waiting', '')", (url,))
        task_ids.append(c.lastrowid)
    conn.commit()
    conn.close()
    background_tasks.add_task(process_urls_background, task_ids, data.urls, data.token)
    return {"message": "Job đang chạy", "total_urls": len(data.urls)}

@app.get("/status")
def get_status():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT url, status, error_msg FROM tasks")
    rows = c.fetchall()
    conn.close()
    return [{"Tên bài/URL": r[0], "Status": r[1], "Error": r[2]} for r in rows]