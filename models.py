from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    report_type = Column(String(30), nullable=False)
    report_name = Column(String(255), nullable=False)
    file_path = Column(Text)
    original_text = Column(Text)
    summary_text = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())


class BloodTestReport(Base):
    __tablename__ = "blood_test_reports"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"), unique=True)
    hemoglobin = Column(String(50))
    wbc = Column(String(50))
    rbc = Column(String(50))
    platelet = Column(String(50))
    glucose = Column(String(50))
    creatinine = Column(String(50))
    alt = Column(String(50))
    ast = Column(String(50))
    general_comment = Column(Text)


class EpicrisisReport(Base):
    __tablename__ = "epicrisis_reports"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"), unique=True)
    diagnosis = Column(Text)
    treatment = Column(Text)
    discharge_summary = Column(Text)
    doctor_notes = Column(Text)


class EKGReport(Base):
    __tablename__ = "ekg_reports"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"), unique=True)
    heart_rate = Column(String(50))
    rhythm = Column(String(100))
    pr_interval = Column(String(50))
    qrs_duration = Column(String(50))
    qt_qtc = Column(String(50))
    interpretation = Column(Text)