from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from model import schemes, core
from model.database import get_db

router = APIRouter()


@router.get("/", response_model=List[schemes.Timestamp])
def read_timestamps(db: Session = Depends(get_db)):
    return db.query(core.Timestamp).all()


@router.delete("/")
def delete_all_timestamps(db: Session = Depends(get_db)):
    try:
        count = db.query(core.Timestamp).count()
        if count == 0:
            return {"message": "No records"}

        db.query(core.Timestamp).delete()
        db.commit()
        return {"message": "All records deleted"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error due deleting {str(e)}")
