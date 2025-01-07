import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from sqlalchemy.orm import Session
from backend.db_setup import SessionLocal, BirdImage

def test_db_connection():
    db: Session = SessionLocal()
    try:
        result = db.query(BirdImage).all()
        assert result is not None
    finally:
        db.close()
