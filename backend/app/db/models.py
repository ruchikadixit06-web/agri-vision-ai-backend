from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, func
from backend.app.db.session import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="farmer")
    created_at = Column(DateTime, server_default=func.now())

class Farm(Base):
    __tablename__ = "farms"

    farm_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    farm_name = Column(String(100), nullable=False)
    state = Column(String(50), nullable=False)
    district = Column(String(50), nullable=False)
    area_acres = Column(Numeric(8, 2), nullable=False)

class YieldRecord(Base):
    __tablename__ = "yield_records"

    record_id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.farm_id", ondelete="CASCADE"))
    crop_type = Column(String(50), nullable=False)
    yield_amount = Column(Numeric(10, 2), nullable=False)
    harvest_date = Column(DateTime, nullable=False)