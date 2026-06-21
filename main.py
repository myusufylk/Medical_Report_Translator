from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import shutil
import os
import uuid
import json
#import torch
import re
#from unsloth import FastLanguageModel

# Kendi modüllerin
from database import Base, engine, get_db
import models
from ocr import extract_text, extract_lab_values, extract_ekg_data, extract_epicrisis_sections

# --- 1. BAŞLANGIÇ AYARLARI ---
models.Base.metadata.create_all(bind=engine)
if not os.path.exists("uploads"):
    os.makedirs("uploads")

app = FastAPI(title="Medikal Analiz Sistemi - Profesyonel Karar Destek")

# --- 2. MODEL YÜKLEME (Unsloth Llama-3) ---
#MODEL_YOLU = "medikal_model_llama3"
#model, tokenizer = FastLanguageModel.from_pretrained(
    #model_name = MODEL_YOLU,
    #max_seq_length = 2048,
    #load_in_4bit = True,
#)
#FastLanguageModel.for_inference(model)

# --- 3. AKILLI ANALİZ MANTIĞI ---
def get_reference_data(report_type: str):
    mapping = {
        "Hemogram": "hemogram.json",
        "Biyokimya": "biyokimya.json",
        "EKG": "ekg.json",
        "Epikriz": "epikriz.json",
        "Kan Tahlili": "biyokimya.json"
    }
    file_name = mapping.get(report_type)
    if file_name and os.path.exists(file_name):
        with open(file_name, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def analyze_numerics(raw_text, report_type):
    if report_type == "EKG":
        parsed_data = extract_ekg_data(raw_text)
    elif report_type == "Epikriz":
        parsed_data = extract_epicrisis_sections(raw_text)
    else:
        parsed_data = extract_lab_values(raw_text)

    ref_data = get_reference_data(report_type)

    if not parsed_data:
        return "Sayısal veri ayıklanamadı.", "Veri bulunamadı."

    all_results = []
    only_deviations = []
    noise_list = ["enabiz", "gov.tr", "sayfa", "0850", "10^", "mmol/l", "mg/dl", "u/l", "coi", "cells", "01.08"]

    for key, info in parsed_data.items():
        if any(noise in key.lower() for noise in noise_list) or len(key) < 2:
            continue

        val = info.get("value")
        status = str(info.get("status", "NORMAL")).upper()

        # Epikriz için matched_keywords listesini string'e çevir
        if isinstance(val, list):
            val = ", ".join(val) if val else None

        match = next((k for k in ref_data.keys() if k.upper() in key.upper()), None)
        if match and val is not None:
            try:
                item = ref_data[match]
                range_str = str(item.get('normal_aralik', item.get('referans', ''))).replace(",", ".").replace("–", "-")
                nums = re.findall(r"\d+\.\d+|\d+", range_str)
                if len(nums) >= 2:
                    low, high = float(nums[0]), float(nums[1])
                    v_float = float(str(val).replace(",", "."))
                    if v_float > high:
                        status = "YÜKSEK"
                    elif v_float < low:
                        status = "DÜŞÜK"
                    else:
                        status = "NORMAL"
            except:
                pass

        display_name = re.sub(r"[\d\.,\-\s/]+", " ", key).strip().upper()
        if not display_name:
            display_name = match.upper() if match else key.upper()

        if status in ["YÜKSEK", "DÜŞÜK", "VAR"]:
            status_label = f"({status} ⚠️)"
            only_deviations.append(f"{display_name} degeri {val} yani {status} seviyededir.")
        else:
            status_label = f"({status})"

        all_results.append(f"- {display_name}: {val} {status_label}")

    islenmis_metin = "\n".join(all_results)
    sapan_metin = "\n".join(only_deviations) if only_deviations else "Tum degerler normal aralikta."

    return islenmis_metin, sapan_metin

# --- 4. API ENDPOINT ---
@app.post("/ocr-new")
async def process_report(
    file: UploadFile = File(...),
    report_type: str = Form(...),
    db: Session = Depends(get_db)
):
    temp_path = f"uploads/{uuid.uuid4()}_{file.filename}"

    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

       raw_text = extract_text(temp_path)

        labeled_results, model_input_results = analyze_numerics(
            raw_text,
            report_type
        )

        # GEÇİCİ OLARAK LLM KAPALI
        cevap = model_input_results

        if not cevap:
            cevap = "Analiz sonucu üretilemedi."

        new_report = models.Report(
            user_id=1,
            report_type=report_type,
            report_name=file.filename,
            file_path=temp_path,
            original_text=raw_text,
            summary_text=cevap
        )

        db.add(new_report)
        db.commit()

        return {
            "islenmis_veri": labeled_results,
            "analiz": cevap,
            "durum": "Başarılı"
        }

    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)

        print(f"WSL LOG HATASI: {str(e)}")

        raise HTTPException(
            status_code=500,
            detail=f"Sistem Hatası: {str(e)}"
        )
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
