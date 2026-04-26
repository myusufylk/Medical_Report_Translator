import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import os
import fitz


pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_PATH = r"C:\poppler\Library\bin"


def clean_text(text: str) -> str:
    text = text.replace("\r", "\n")

    lines = text.split("\n")
    cleaned = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        cleaned.append(line)

    return "\n".join(cleaned)


def process_image(image):
    image = image.convert("L")

    text = pytesseract.image_to_string(
        image,
        lang="tur+eng",
        config="--oem 3 --psm 6"
    )

    return clean_text(text)


# 📷 IMAGE
def extract_text_from_image(path: str) -> str:
    image = Image.open(path)
    return process_image(image)


# 📄 PDF
def extract_text_from_pdf(path: str) -> str:
    try:
        doc = fitz.open(path)
        text = ""

        for page in doc:
            text += page.get_text()

        if text.strip():
            return clean_text(text)

    except:
        pass


    images = convert_from_path(path, dpi=300, poppler_path=POPPLER_PATH)

    texts = []
    for img in images:
        texts.append(process_image(img))

    return "\n\n".join(texts)



def extract_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()

    if ext in [".png", ".jpg", ".jpeg"]:
        return extract_text_from_image(file_path)

    elif ext == ".pdf":
        return extract_text_from_pdf(file_path)

    else:
        raise ValueError("Desteklenmeyen dosya formatı")


def extract_lab_values(text: str) -> dict:
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    results = {}

    def to_float(val):
        try:
            return float(val.replace(",", "."))
        except:
            return None

    def parse_ref(ref_str):
        try:
            ref_str = ref_str.replace(",", ".")
            parts = ref_str.split("-")
            if len(parts) == 2:
                return float(parts[0].strip()), float(parts[1].strip())
        except:
            pass
        return None, None

    def get_flag(value, ref_min, ref_max):
        if value is None or ref_min is None or ref_max is None:
            return "unknown"
        if value < ref_min:
            return "low"
        elif value > ref_max:
            return "high"
        else:
            return "normal"

    i = 0
    while i < len(lines):
        line = lines[i]
        line_lower = line.lower()

        if line.startswith("Hemogram") and i + 3 < len(lines):
            try:
                name = line.replace("Hemogram", "").strip().lower()

                raw_value = lines[i+1]
                unit = lines[i+2].strip()
                ref = lines[i+3].strip()

                value = to_float(raw_value)
                ref_min, ref_max = parse_ref(ref)

                flag = get_flag(value, ref_min, ref_max)

                results[name] = {
                    "value": value,
                    "unit": unit,
                    "ref": ref,
                    "ref_min": ref_min,
                    "ref_max": ref_max,
                    "status": flag
                }

                i += 4
                continue
            except:
                pass

        if "hemogram" in line_lower:
            try:
                parts = line.split()

                if len(parts) >= 5:
                    name = parts[1].lower()
                    raw_value = parts[2]
                    unit = parts[3].strip()
                    ref = " ".join(parts[4:]).strip()

                    value = to_float(raw_value)
                    ref_min, ref_max = parse_ref(ref)

                    flag = get_flag(value, ref_min, ref_max)

                    results[name] = {
                        "value": value,
                        "unit": unit,
                        "ref": ref,
                        "ref_min": ref_min,
                        "ref_max": ref_max,
                        "status": flag
                    }
            except:
                pass

        i += 1

    return results