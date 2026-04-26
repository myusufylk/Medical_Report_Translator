from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    reports = relationship("Report", back_populates="user", cascade="all, delete")



class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    report_type = Column(String(30), nullable=False)
    report_name = Column(String(255), nullable=False)

    file_path = Column(Text)

    original_text = Column(Text)
    summary_text = Column(Text, nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)

    # 🔗 ilişkiler
    user = relationship("User", back_populates="reports")

    blood_test = relationship(
        "BloodTestReport",
        back_populates="report",
        uselist=False,
        cascade="all, delete"
    )

    epicrisis = relationship(
        "EpicrisisReport",
        back_populates="report",
        uselist=False,
        cascade="all, delete"
    )

    ekg = relationship(
        "EKGReport",
        back_populates="report",
        uselist=False,
        cascade="all, delete"
    )



class BloodTestReport(Base):
    __tablename__ = "blood_test_reports"

    id = Column(Integer, primary_key=True, index=True)

    report_id = Column(
        Integer,
        ForeignKey("reports.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )

    hemoglobin = Column(String(50))
    wbc = Column(String(50))
    rbc = Column(String(50))
    platelet = Column(String(50))
    glucose = Column(String(50))
    creatinine = Column(String(50))
    alt = Column(String(50))
    ast = Column(String(50))

    general_comment = Column(Text)

    report = relationship("Report", back_populates="blood_test")


class EpicrisisReport(Base):
    __tablename__ = "epicrisis_reports"

    id = Column(Integer, primary_key=True, index=True)

    report_id = Column(
        Integer,
        ForeignKey("reports.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )

    diagnosis = Column(Text)
    treatment = Column(Text)
    discharge_summary = Column(Text)
    doctor_notes = Column(Text)

    report = relationship("Report", back_populates="epicrisis")



class EKGReport(Base):
    __tablename__ = "ekg_reports"

    id = Column(Integer, primary_key=True, index=True)

    report_id = Column(
        Integer,
        ForeignKey("reports.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )

    heart_rate = Column(String(50))
    rhythm = Column(String(100))
    pr_interval = Column(String(50))
    qrs_duration = Column(String(50))
    qt_qtc = Column(String(50))
    interpretation = Column(Text)

    report = relationship("Report", back_populates="ekg")