from uuid import UUID
from fastapi import FastAPI, HTTPException, Body
import jwt
from datetime import datetime, timedelta
from app.dto.token_request import TokenRequest
from app.model.token_data import TokenData

app = FastAPI()

SECRET_KEY = "grogu"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

@app.post("/token/{user_id}")
def create_token(user_id: UUID) -> dict:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "exp": expire,
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

@app.post("/validate")
def validate_token(token_request: TokenRequest) -> TokenData:
    try:
        payload = jwt.decode(token_request.token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return TokenData(user_id=user_id)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
