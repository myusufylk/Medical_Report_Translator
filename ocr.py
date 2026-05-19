import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import os
import fitz
import re

# Sistem yolları
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_PATH = r"C:\poppler\Library\bin"

def clean_text(text: str) -> str:
    """Metni e-Nabız kirliliğinden arındırır."""
    text = text.replace('"', '').replace('$', '').replace('\r', '')
    return text

def extract_text(file_path: str) -> str:
    """PDF veya Görsel kaynaklarından metin çıkarır."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        try:
            doc = fitz.open(file_path)
            text = "".join([page.get_text() for page in doc])
            if text.strip() and len(text) > 100: 
                return clean_text(text)
        except: 
            pass
        images = convert_from_path(file_path, dpi=300, poppler_path=POPPLER_PATH)
        return clean_text("\n".join([pytesseract.image_to_string(img.convert("L"), lang="tur+eng") for img in images]))
    elif ext in [".png", ".jpg", ".jpeg"]:
        image = Image.open(file_path).convert("L")
        return clean_text(pytesseract.image_to_string(image, lang="tur+eng"))
    return ""

def extract_lab_values(text: str) -> dict:
    """Metni parçalara ayırır, sayısal değerleri ve referans aralıklarını eşleştirir."""
    parts = [p.strip() for p in re.split(r'[,\n]', text) if p.strip()]
    results = {}

    def to_float(val_str):
        if not val_str or any(char in val_str for char in ["^", "/", "*"]): 
            return None
        cleaned = re.sub(r"[^\d\.]", "", val_str.replace(",", "."))
        try:
            f_val = float(cleaned)
            return f_val if f_val < 1000000 else None
        except: 
            return None

    ref_pattern = r"(\d+[\.,]?\d*)\s*[-–]\s*(\d+[\.,]?\d*)"

    for i in range(len(parts)):
        val = to_float(parts[i])
        
        # Tarih formatına takılmayan geçerli sayıları yakala
        if val is not None and not re.match(r"\d{2}\.\d{2}\.", parts[i]):
            if i > 0:
                name = parts[i-1].lower()
                # Sadece sayıdan oluşan sahte isimleri atla
                if re.match(r"^[0-9\.,\-\s]+$", name): 
                    continue

                # Referans aralığını bulmak için sonraki 4 parçayı tara
                ref_min, ref_max = None, None
                for offset in range(1, 5):
                    if i + offset < len(parts):
                        match = re.search(ref_pattern, parts[i+offset])
                        if match:
                            ref_min = to_float(match.group(1))
                            ref_max = to_float(match.group(2))
                            break

                # Yasaklı başlıkları filtrele
                if len(name) > 2 and name not in ["sonuç", "referans", "birimi", "tahlil", "tarih", "sayfa"]:
                    # main.py ile tam uyum için durumları BÜYÜK HARF yapıyoruz
                    status = "NORMAL"
                    if ref_min is not None and ref_max is not None:
                        if val < ref_min: 
                            status = "DÜŞÜK"
                        elif val > ref_max: 
                            status = "YÜKSEK"
                    
                    # main.py'nin çapraz kontrol mantığı patlamasın diye ref sınırlarını da teslim ediyoruz
                    results[name] = {
                        "value": val, 
                        "status": status,
                        "ref_min": ref_min,
                        "ref_max": ref_max
                    }
    return results