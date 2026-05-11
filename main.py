from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from models import BloodTestReport, EpicrisisReport, EKGReport
from fastapi.middleware.cors import CORSMiddleware
import models
import shutil
import os
import uuid
print(" CALISAN MAIN:", os.path.abspath(__file__))


from ocr import extract_text, extract_lab_values

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.get("/")
def root():
    return {"message": "API çalışıyor"}


@app.post("/ocr-new")
async def ocr_file(
    file: UploadFile = File(...),
    report_type: str = Form(...),
    db: Session = Depends(get_db)
):
    file_path = None

    try:

        allowed_types = ["image/jpeg", "image/png", "application/pdf"]
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Desteklenmeyen dosya tipi")


        unique_name = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_name)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)


        text = extract_text(file_path)

        if not text or len(text.strip()) < 10:
            raise HTTPException(status_code=400, detail="OCR metni boş")

        print("OCR TEXT LENGTH:", len(text))


        parsed_data = extract_lab_values(text)


        new_report = models.Report(
            user_id=1,
            report_type=report_type,
            report_name=file.filename,
            file_path=file_path,
            original_text=text,
            summary_text=None
        )

        db.add(new_report)
        db.flush()
        db.refresh(new_report)

        if report_type == "Kan Tahlili":

            blood_test = BloodTestReport(
                report_id=new_report.id,

                hemoglobin=str(
                    parsed_data.get("hgb", {}).get("value", "")
                ),

                wbc=str(
                    parsed_data.get("wbc", {}).get("value", "")
                ),

                rbc=str(
                    parsed_data.get("rbc", {}).get("value", "")
                ),

                platelet=str(
                    parsed_data.get("plt", {}).get("value", "")
                ),
            )

            db.add(blood_test)




        elif report_type == "Epikriz Raporu":

            epicrisis = EpicrisisReport(
                report_id=new_report.id,

                diagnosis=text[:300],
                treatment="",
                discharge_summary="",
                doctor_notes=""
            )

            db.add(epicrisis)




        elif report_type == "EKG Metin Raporu":

            ekg = EKGReport(
                report_id=new_report.id,

                heart_rate="",
                rhythm="",
                pr_interval="",
                qrs_duration="",
                qt_qtc="",
                interpretation=text[:300]
            )

            db.add(ekg)

        db.commit()


        return {
            "report_id": new_report.id,
            "filename": file.filename,
            "report_type": report_type,
            "text_lines": [line for line in text.split("\n") if line.strip()],
            "parsed_data": parsed_data
        }

    except HTTPException as e:
        raise e

    except Exception as e:
        print("ERROR:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

    finally:

        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as cleanup_error:
                print("File cleanup error:", cleanup_error)
