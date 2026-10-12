from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.db.session import engine, Base, get_db
from backend.app.db.models import User
from backend.app.schemas import UserCreate, UserLogin, Token
from backend.app.auth import hash_password, verify_password, create_access_token

# Automatically create database tables if not exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Agri-Vision AI Backend", version="1.0")

@app.get("/")
def read_root():
    return {"message": "Agri Vision AI API is running successfully!"}

# 1. User Registration Endpoint
@app.post("/register", response_model=Token)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password & create user
    hashed_pwd = hash_password(user.password)
    new_user = User(
        full_name=user.full_name,
        email=user.email,
        password_hash=hashed_pwd,
        role=user.role
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Generate access token immediately after signup
    access_token = create_access_token(data={"sub": new_user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# 2. User Login Endpoint
@app.post("/login", response_model=Token)
def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_credentials.email).first()
    
    if not user or not verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

from backend.app.schemas import FarmCreate, FarmResponse
from backend.app.db.models import Farm
from fastapi import Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from backend.app.auth import SECRET_KEY, ALGORITHM

security = HTTPBearer()

def get_current_user_email(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

@app.post("/farms", response_model=FarmResponse)
def create_farm(farm: FarmCreate, db: Session = Depends(get_db), current_user_email: str = Depends(get_current_user_email)):
    user = db.query(User).filter(User.email == current_user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_farm = Farm(
        user_id=user.user_id,
        farm_name=farm.farm_name,
        state=farm.state,
        district=farm.district,
        area_acres=farm.area_acres
    )
    
    db.add(new_farm)
    db.commit()
    db.refresh(new_farm)
    return new_farm

from backend.app.schemas import YieldRecordCreate, YieldRecordResponse
from backend.app.db.models import YieldRecord

# 4. Get All Farms for Logged-in User
@app.get("/farms", response_model=list[FarmResponse])
def get_user_farms(db: Session = Depends(get_db), current_user_email: str = Depends(get_current_user_email)):
    user = db.query(User).filter(User.email == current_user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    farms = db.query(Farm).filter(Farm.user_id == user.user_id).all()
    return farms

# 5. Create Crop Yield Record for a Farm
@app.post("/yield-records", response_model=YieldRecordResponse)
def create_yield_record(record: YieldRecordCreate, db: Session = Depends(get_db), current_user_email: str = Depends(get_current_user_email)):
    user = db.query(User).filter(User.email == current_user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify that the farm belongs to the logged-in user
    farm = db.query(Farm).filter(Farm.farm_id == record.farm_id, Farm.user_id == user.user_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found or unauthorized")
    
    new_record = YieldRecord(
        farm_id=record.farm_id,
        crop_type=record.crop_type,
        season=record.season,
        predicted_yield_tons=record.predicted_yield_tons
    )
    
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record

# 6. Get All Yield Records for Logged-in User's Farms
@app.get("/yield-records", response_model=list[YieldRecordResponse])
def get_user_yield_records(db: Session = Depends(get_db), current_user_email: str = Depends(get_current_user_email)):
    user = db.query(User).filter(User.email == current_user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get all farm IDs belonging to this user
    user_farm_ids = db.query(Farm.farm_id).filter(Farm.user_id == user.user_id).all()
    farm_ids_list = [farm.farm_id for farm in user_farm_ids]
    
    if not farm_ids_list:
        return []
    
    # Query yield records associated with those farms
    records = db.query(YieldRecord).filter(YieldRecord.farm_id.in_(farm_ids_list)).all()
    return records