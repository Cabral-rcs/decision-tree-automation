from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class AutoAlertConfig(Base):
    __tablename__ = 'auto_alert_config'
    id = Column(Integer, primary_key=True, index=True)
    is_active = Column(Boolean, default=False)
    interval_minutes = Column(Integer, default=3)
    last_execution = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 