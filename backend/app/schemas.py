from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: str = "farmer"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class FarmCreate(BaseModel):
    farm_name: str
    state: str
    district: str
    area_acres: float

class FarmResponse(FarmCreate):
    farm_id: int
    user_id: int

    class Config:
        orm_mode = True

class YieldRecordCreate(BaseModel):
    farm_id: int
    crop_type: str
    season: str
    predicted_yield_tons: float

class YieldRecordResponse(YieldRecordCreate):
    record_id: int

    class Config:
        orm_mode = True        