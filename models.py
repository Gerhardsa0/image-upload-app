from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base
from datetime import datetime


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, nullable=False)
    number = Column(Float, nullable=False)
    image_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)