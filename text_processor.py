import re

def roman_to_int(s):
    roman_val = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    int_val = 0
    for i in range(len(s)):
        if i > 0 and roman_val.get(s[i], 0) > roman_val.get(s[i - 1], 0):
            int_val += roman_val.get(s[i], 0) - 2 * roman_val.get(s[i - 1], 0)
        else:
            int_val += roman_val.get(s[i], 0)
    return int_val

def xu_ly_tu_ngoai_lai(text):
    g2p_dict = {
        r'\baudio guide\b': 'o-đi-ô gai',
        r'\bguide\b': 'gai',
        r'\btour\b': 'tua',
        r'\bIcon\b': 'Ai-cơn',
        r'\bSarcophagus\b': 'Xác-cô-pha-gớt',
        r'\bMuseum\b': 'Miu-zi-ừm',
        r'\bcephalopod\b': 'xê-pha-lô-pốt',
        r'\bforaminifera\b': 'phô-ra-mi-ni-phê-ra',
        r'\banthozoa\b': 'an-thô-dô-a',
        r'\bPerge\b': 'Péc-giơ',
        r'\bAspendos\b': 'Át-pen-đốt',
        r'\bPatara\b': 'Pa-ta-ra',
        r'\bKarain\b': 'Ca-ra-in',
        r'\bMyra\b': 'Mi-ra',
        r'\bAntalya\b': 'An-ta-li-a',
        r'\bKonyaaltı\b': 'Côn-da-an-tư',
        r'\bHacılar\b': 'Ha-chi-la',
        r'\bHöyük\b': 'Hô-dúc',
        r'\bKarataş\b': 'Ca-ra-tát',
        r'\bSemayük\b': 'Xê-ma-dúc',
        r'\bLykia\b': 'Li-ki-a',
        r'\bLycia\b': 'Li-xi-a',
        r'\bZeus\b': 'Dớt',
        r'\bAthena\b': 'A-thê-na',
        r'\bHeracles\b': 'Hê-ra-clét',
        r'\bHercules\b': 'Héc-quyn',
        r'\bThe\b': 'Đờ',
        r'\bU.S\b': 'Diu et'
    }
    for pattern, pronunciation in g2p_dict.items():
        text = re.sub(pattern, pronunciation, text, flags=re.IGNORECASE)
    return text

def chuan_hoa_am_thanh(text, lang="vi"):
    if not text:
        return ""

    if lang == "vi":
        # 0. ÉP NGẮT NHỊP KHI XUỐNG DÒNG (DẤU ENTER SẼ BIẾN THÀNH DẤU CHẤM)
        text = re.sub(r'\n+', '. ', text)
        text = re.sub(r'[•\-\+]\s+', '; ', text)

        # 1. TRỊ Error VẦN ÂN BỊ ĐỌC THÀNH AN
        loi_van_an = ["chân", "dân", "nhân", "thần", "trần", "phân", "lân", "tân", "mẫn", "cận", "tuân", "huân", "quân", "xuân"]
        for w in loi_van_an:
            text = re.sub(rf'(?i)\b{w}\b', w, text)

        # 2. TỪ NGOẠI LAI (VIETSUB)
        text = xu_ly_tu_ngoai_lai(text)

        # 3. XÓA SẠCH DẤU NGOẶC KÉP / NGOẶC ĐƠN ĐỂ KHÔNG BỊ KHỰNG NHỊP
        text = re.sub(r'[“”"‘’]', '', text)
        text = re.sub(r'\(\s*([^\)]+)\s*\)', r', \1, ', text)

        # =========================================================
        # 4. THUẬT TOÁN TỐI ƯU CON SỐ HÀNG LOẠT (KHÔNG HARDCODE)
        # =========================================================
        # Vòng lặp này sẽ hút sạch mọi dấu chấm ngăn cách hàng nghìn, hàng triệu
        # Ví dụ: 1.500.000 -> 1500000; 30.000 -> 30000. AI sẽ tự động đọc cực mượt!
        while re.search(r'(?<=\d)\.(?=\d{3}\b)', text):
            text = re.sub(r'(?<=\d)\.(?=\d{3}\b)', '', text)
            
        # Xử lý dấu phẩy thập phân (VD: 1,5 -> 1 phẩy 5)
        text = re.sub(r'(?<=\d),(?=\d)', ' phẩy ', text) 
        # Xử lý gạch ngang thời gian (VD: 1990-1995 -> 1990 đến 1995)
        text = re.sub(r'(?<=\d)\s*[-–]\s*(?=\d)', ' đến ', text)
        
        # 5. NIÊN ĐẠI LỊCH SỬ
        text = re.sub(r'\bTCN\b', 'Trước Công nguyên', text)
        text = re.sub(r'\bSCN\b', 'Sau Công nguyên', text)
        text = re.sub(r'\bTr\.CN\b', 'Trước Công nguyên', text)

        # 6. ĐƠN VỊ ĐO LƯỜNG
        units = {
            r'\bm²\b': 'mét vuông',
            r'\bkm²\b': 'ki lô mét vuông',
            r'\bm³\b': 'mét khối',
            r'\bkm/h\b': 'ki lô mét trên giờ',
            r'\bkm\b': 'ki lô mét',
            r'\bcm\b': 'xen ti mét',
            r'\bmm\b': 'mi li mét',
            r'\bkg\b': 'ki lô gam',
            r'\bg\b': 'gam',
            r'\bha\b': 'héc ta',
            r'°C': 'độ C',
            r'\bUSD\b': 'đô la Mỹ',
        }
        for pattern, replacement in units.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        # 7. SỐ LA MÃ
        def replace_century(match):
            roman = match.group(2).upper()
            try:
                number = roman_to_int(roman)
                return f"{match.group(1)} {number}"
            except:
                return match.group(0)
        text = re.sub(r'(?i)(thế kỷ)\s+([IVXLCDM]+)\b', replace_century, text)

        # 8. KÝ HIỆU & VIẾT TẮT CHUNG
        text = text.replace('&', 'và')
        text = text.replace('%', ' phần trăm')
        abbreviations = {
            r'\bTP\.HCM\b': 'Thành phố Hồ Chí Minh',
            r'\bTP\.\s*HCM\b': 'Thành phố Hồ Chí Minh',
            r'\bUBND\b': 'Ủy ban nhân dân',
            r'\bUNESCO\b': 'U nét cô',
            r'\bVNĐ\b': 'Việt Nam đồng',
        }
        for pattern, replacement in abbreviations.items():
            text = re.sub(pattern, replacement, text)

        # 9. FIX Error DẤU CÂU LỘN XỘN DO CODE TẠO RA
        text = re.sub(r'\.{2,}', '.', text)
        text = text.replace(':.', ': ').replace(',.', ', ').replace(';.', '; ')

    # DỌN DẸP CUỐI CÙNG
    text = re.sub(r'\s+', ' ', text).strip()
    text = text.replace(', ,', ',').replace(' ,', ',')
    
    return text