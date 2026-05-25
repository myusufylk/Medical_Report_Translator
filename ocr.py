import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import os
import fitz
import re

# Sistem yolları
if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )
    POPPLER_PATH = r"C:\poppler\Library\bin"
else:
    POPPLER_PATH = None


# ─────────────────────────────────────────────
# MODÜL SEVİYESİ YARDIMCI FONKSİYONLAR
# ─────────────────────────────────────────────

def _to_float(val_str):
    """String → float dönüşümü. Geçersiz formatlarda None döner."""
    if not val_str or any(char in val_str for char in ["^", "/", "*"]):
        return None
    cleaned = re.sub(r"[^\d\.]", "", val_str.replace(",", "."))
    try:
        f_val = float(cleaned)
        return f_val if f_val < 1000000 else None
    except:
        return None


def _alias_match(alias, text):
    """
    Alias'ı word boundary ile arar.
    Kısa alias'ların (af, sr, hr, pr, qt, lad, rad, std, ste vb.)
    başka kelimelerin içinde yanlış eşleşmesini engeller.
    """
    return bool(re.search(rf'\b{re.escape(alias)}\b', text))


# ─────────────────────────────────────────────
# METİN TEMİZLEME VE ÇIKARMA
# ─────────────────────────────────────────────

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
        images = convert_from_path(
            file_path, dpi=300,
            poppler_path=POPPLER_PATH if POPPLER_PATH else None
        )
        return clean_text("\n".join([
            pytesseract.image_to_string(img.convert("L"), lang="tur+eng")
            for img in images
        ]))
    elif ext in [".png", ".jpg", ".jpeg"]:
        image = Image.open(file_path).convert("L")
        return clean_text(pytesseract.image_to_string(image, lang="tur+eng"))
    return ""


# ─────────────────────────────────────────────
# KAN TAHLİLİ
# ─────────────────────────────────────────────

def extract_lab_values(text: str) -> dict:
    """Metni parçalara ayırır, sayısal değerleri ve referans aralıklarını eşleştirir."""
    parts = [p.strip() for p in re.split(r'[,\n]', text) if p.strip()]
    results = {}
    ref_pattern = r"(\d+[\.,]?\d*)\s*[-–]\s*(\d+[\.,]?\d*)"

    for i in range(len(parts)):
        val = _to_float(parts[i])

        if val is not None and not re.match(r"\d{2}\.\d{2}\.", parts[i]):
            if i > 0:
                name = parts[i - 1].lower()
                if re.match(r"^[0-9\.,\-\s]+$", name):
                    continue

                ref_min, ref_max = None, None
                for offset in range(1, 5):
                    if i + offset < len(parts):
                        match = re.search(ref_pattern, parts[i + offset])
                        if match:
                            ref_min = _to_float(match.group(1))
                            ref_max = _to_float(match.group(2))
                            break

                if len(name) > 2 and name not in ["sonuç", "referans", "birimi", "tahlil", "tarih", "sayfa"]:
                    status = "NORMAL"
                    if ref_min is not None and ref_max is not None:
                        if val < ref_min:
                            status = "DÜŞÜK"
                        elif val > ref_max:
                            status = "YÜKSEK"

                    results[name] = {
                        "value": val,
                        "status": status,
                        "ref_min": ref_min,
                        "ref_max": ref_max
                    }
    return results


# ─────────────────────────────────────────────
# EKG
# ─────────────────────────────────────────────

def extract_ekg_data(text: str) -> dict:
    """
    EKG metnini parçalara ayırır, sayısal parametreleri referans aralıklarıyla
    eşleştirir ve her bulgu için value/status/ref_min/ref_max yapısı döndürür.
    """
    parts = [p.strip() for p in re.split(r'[,\n]', text) if p.strip()]
    lower_text = text.lower()
    ref_pattern = r"(\d+[\.,]?\d*)\s*[-–]\s*(\d+[\.,]?\d*)"

    # ── Sayısal EKG parametreleri ──────────────────────────────────────────
    # Alias'lar uzundan kısaya sıralı: daha spesifik olanlar önce eşleşsin
    numeric_params = {
        "Kalp_Hizi": {
            "aliases": ["ventricular rate", "heart rate", "hr"],
            "ref_min": 60,
            "ref_max": 100,
            "unit": "bpm"
        },
        "PR_Araligi": {
            "aliases": ["pr interval", "pri", "pr"],
            "ref_min": 120,
            "ref_max": 200,
            "unit": "ms"
        },
        "QRS_Suresi": {
            "aliases": ["qrs duration", "qrs"],
            "ref_min": 60,
            "ref_max": 120,
            "unit": "ms"
        },
        "QT_QTc_Araligi": {
            "aliases": ["qt interval", "qtc", "qt"],
            "ref_min": 350,
            "ref_max": 440,
            "unit": "ms"
        },
    }

    ekg_data = {}

    for param_key, meta in numeric_params.items():
        value = None
        ref_min_found = None
        ref_max_found = None

        # 1) parts üzerinden lab_values mantığıyla tara (word boundary ile)
        for i in range(len(parts)):
            val = _to_float(parts[i])
            if val is not None and not re.match(r"\d{2}\.\d{2}\.", parts[i]):
                if i > 0:
                    name = parts[i - 1].lower()
                    if re.match(r"^[0-9\.,\-\s]+$", name):
                        continue
                    if any(_alias_match(alias, name) for alias in meta["aliases"]):
                        value = val
                        for offset in range(1, 5):
                            if i + offset < len(parts):
                                m = re.search(ref_pattern, parts[i + offset])
                                if m:
                                    ref_min_found = _to_float(m.group(1))
                                    ref_max_found = _to_float(m.group(2))
                                    break
                        break

        # 2) parts'ta bulunamadıysa lower_text üzerinden serbest regex (word boundary ile)
        if value is None:
            for alias in meta["aliases"]:
                match = re.search(
                    rf'\b{re.escape(alias)}\b[^\d]*(\d+)',
                    lower_text
                )
                if match:
                    value = _to_float(match.group(1))
                    if value is not None:
                        break

        # 3) Referans aralığı bulunamadıysa sabit varsayılanları kullan
        effective_min = ref_min_found if ref_min_found is not None else meta["ref_min"]
        effective_max = ref_max_found if ref_max_found is not None else meta["ref_max"]

        # 4) Status belirle
        if value is None:
            status = "BULUNAMADI"
        elif value < effective_min:
            status = "DÜŞÜK"
        elif value > effective_max:
            status = "YÜKSEK"
        else:
            status = "NORMAL"

        ekg_data[param_key] = {
            "value": value,
            "status": status,
            "ref_min": effective_min,
            "ref_max": effective_max,
            "unit": meta["unit"]
        }

    # ── Boolean bulgular ───────────────────────────────────────────────────
    boolean_params = {
        "Sinus_Ritmi": {
            "aliases": ["normal sinus rhythm", "sinus rhythm", "nsr", "sr"],
            "found_status": "VAR",
            "not_found_status": "YOK"
        },
        "Atriyal_Fibrilasyon": {
            "aliases": ["atrial fibrillation", "afib", "af"],
            "found_status": "VAR",
            "not_found_status": "YOK"
        },
        "ST_Yuksekligi": {
            "aliases": ["st elevation", "stemi", "ste"],
            "found_status": "VAR",
            "not_found_status": "YOK"
        },
        "ST_Depresyonu": {
            "aliases": ["st depression", "std"],
            "found_status": "VAR",
            "not_found_status": "YOK"
        },
        "T_Dalgasi_Anormalligi": {
            "aliases": ["t-wave abnormality", "t inversion", "t abnormality", "lowt"],
            "found_status": "VAR",
            "not_found_status": "YOK"
        },
        "Sol_Dal_Blogu": {
            "aliases": ["left bundle branch block", "lbbb"],
            "found_status": "VAR",
            "not_found_status": "YOK"
        },
        "Sag_Dal_Blogu": {
            "aliases": ["right bundle branch block", "rbbb"],
            "found_status": "VAR",
            "not_found_status": "YOK"
        },
        "Sol_Aks_Sapmasi": {
            "aliases": ["left axis deviation", "lad"],
            "found_status": "VAR",
            "not_found_status": "YOK"
        },
        "Sag_Aks_Sapmasi": {
            "aliases": ["right axis deviation", "rad"],
            "found_status": "VAR",
            "not_found_status": "YOK"
        },
        "Sol_Ventrikul_Hipertrofisi": {
            "aliases": ["left ventricular hypertrophy", "lvh"],
            "found_status": "VAR",
            "not_found_status": "YOK"
        },
    }

    for param_key, meta in boolean_params.items():
        matched_aliases = []

        # 1) parts üzerinden word boundary ile tara
        for part in parts:
            part_lower = part.lower()
            for alias in meta["aliases"]:
                if alias not in matched_aliases and _alias_match(alias, part_lower):
                    matched_aliases.append(alias)

        # 2) Fallback: lower_text üzerinden word boundary ile kontrol et
        if not matched_aliases:
            for alias in meta["aliases"]:
                if _alias_match(alias, lower_text) and alias not in matched_aliases:
                    matched_aliases.append(alias)

        found = len(matched_aliases) > 0
        ekg_data[param_key] = {
            "value": matched_aliases if matched_aliases else None,
            "status": meta["found_status"] if found else meta["not_found_status"],
            "ref_min": None,
            "ref_max": None
        }

    # ── Bradikardi / Taşikardi kalp hızından türet ─────────────────────────
    hr_val = ekg_data["Kalp_Hizi"]["value"]
    if hr_val is not None:
        if hr_val < 60:
            bradikardi_status = "Bradikardi"
        elif hr_val > 100:
            bradikardi_status = "Taşikardi"
        else:
            bradikardi_status = "NORMAL"
    else:
        bradikardi_status = "BULUNAMADI"

    ekg_data["Bradikardi_Tasikardi"] = {
        "value": hr_val,
        "status": bradikardi_status,
        "ref_min": 60,
        "ref_max": 100,
        "unit": "bpm"
    }

    return ekg_data


# ─────────────────────────────────────────────
# EPİKRİZ
# ─────────────────────────────────────────────

def extract_epicrisis_sections(text: str) -> dict:
    """
    Epikriz metnini parçalara ayırır; her bölüm için eşleşen anahtar kelimeleri,
    bulunan sayısal değerleri ve referans aralıklarını lab_values mantığıyla döndürür.
    """
    parts = [p.strip() for p in re.split(r'[,\n]', text) if p.strip()]
    lower_text = text.lower()
    ref_pattern = r"(\d+[\.,]?\d*)\s*[-–]\s*(\d+[\.,]?\d*)"

    section_defs = {
        "Chief_Complaint": {
            "keywords": [
                "chest pain", "shortness of breath", "syncope",
                "dizziness", "fever", "headache", "allergy", "difficulty voiding"
            ]
        },
        "Clinical_History": {
            "keywords": [
                "diabetes", "hypertension", "asthma", "sleep apnea",
                "coronary artery disease", "hypothyroidism", "renal disease",
                "reflux disease", "osteoarthritis"
            ]
        },
        "Physical_Exam": {
            "keywords": [
                "wheezing", "edema", "stable", "tachycardia",
                "afebrile", "erythematous", "murmur"
            ]
        },
        "Primer_Tani": {
            "keywords": [
                "hypertension", "hypothyroidism", "anemia", "heart failure",
                "diabetes mellitus", "hyperlipidemia", "pneumonia", "copd",
                "urinary tract infection", "syncope", "rheumatoid arthritis"
            ]
        },
        "Sekonder_Tani": {
            "keywords": [
                "anxiety", "hypokalemia", "atrial fibrillation",
                "chronic kidney disease", "pancytopenia"
            ]
        },
        "Hospital_Course": {
            "keywords": [
                "surgery", "icu", "antibiotic", "transfusion",
                "hemodialysis", "postoperative", "complication"
            ]
        },
        "Vital_Bulgular": {
            "keywords": [
                "blood pressure", "heart rate", "respiratory rate",
                "spo2", "temperature", "oxygen saturation"
            ]
        },
        "Taburculuk_Durumu": {
            "keywords": [
                "stable", "discharged", "satisfactory condition", "improved"
            ]
        },
        "Taburculuk_Ilaclari": {
            "keywords": [
                "lisinopril", "coreg", "motrin", "bactrim",
                "zyrtec", "loratadine", "nasonex"
            ]
        },
        "Kontrol_Randevusu": {
            "keywords": [
                "follow-up", "return in", "outpatient", "wound check"
            ]
        },
        "Tedavi_Plani": {
            "keywords": [
                "bedrest", "diet", "physical therapy",
                "blood sugar monitoring", "pelvic rest"
            ]
        },
        "Konsultasyon": {
            "keywords": [
                "cardiology", "neurology", "nutritionist",
                "psychiatry", "consultation"
            ]
        },
        "Prognoz": {
            "keywords": [
                "prognosis", "follow required", "partial recovery", "improvement"
            ]
        },
    }

    epicrisis_data = {}

    for section_key, meta in section_defs.items():
        matched_keywords = []
        numeric_findings = {}

        for i in range(len(parts)):
            part_lower = parts[i].lower()

            # 1) Keyword eşleşmesi — word boundary ile
            for keyword in meta["keywords"]:
                if keyword not in matched_keywords and _alias_match(keyword, part_lower):
                    matched_keywords.append(keyword)

            # 2) Sayısal değer varsa lab_values mantığıyla al
            val = _to_float(parts[i])
            if val is not None and not re.match(r"\d{2}\.\d{2}\.", parts[i]):
                if i > 0:
                    name = parts[i - 1].lower()
                    if re.match(r"^[0-9\.,\-\s]+$", name):
                        continue
                    if any(_alias_match(keyword, name) for keyword in meta["keywords"]):
                        if len(name) > 2 and name not in [
                            "sonuç", "referans", "birimi", "tahlil", "tarih", "sayfa"
                        ]:
                            ref_min, ref_max = None, None
                            for offset in range(1, 5):
                                if i + offset < len(parts):
                                    m = re.search(ref_pattern, parts[i + offset])
                                    if m:
                                        ref_min = _to_float(m.group(1))
                                        ref_max = _to_float(m.group(2))
                                        break

                            status = "NORMAL"
                            if ref_min is not None and ref_max is not None:
                                if val < ref_min:
                                    status = "DÜŞÜK"
                                elif val > ref_max:
                                    status = "YÜKSEK"

                            numeric_findings[name] = {
                                "value": val,
                                "status": status,
                                "ref_min": ref_min,
                                "ref_max": ref_max
                            }

        # Fallback: parts'ta eşleşme yoksa lower_text üzerinden word boundary ile kontrol et
        if not matched_keywords:
            for keyword in meta["keywords"]:
                if keyword not in matched_keywords and _alias_match(keyword, lower_text):
                    matched_keywords.append(keyword)

        epicrisis_data[section_key] = {
            "value": matched_keywords,
            "matched_keywords": matched_keywords,
            "status": "VAR" if matched_keywords else "YOK",
            "numeric_findings": numeric_findings,
            "ref_min": None,
            "ref_max": None
        }

    # ── ICD10 ayrı parse ───────────────────────────────────────────────────
    icd10_pattern = r'\b[A-TV-Z][0-9][0-9AB]\.?\d{0,2}\b'
    icd_matches = list(set(re.findall(icd10_pattern, text)))

    epicrisis_data["ICD10_Kodu"] = {
        "value": icd_matches,
        "matched_keywords": icd_matches,
        "status": "VAR" if icd_matches else "YOK",
        "numeric_findings": {},
        "ref_min": None,
        "ref_max": None
    }

    return epicrisis_data