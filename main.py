import asyncio

from sqlalchemy import text
from sqlalchemy.orm import Session

import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from src.routes import meals, orders
from src.database.db import get_db

app = FastAPI()

app.include_router(meals.router, prefix='/api')
app.include_router(orders.router, prefix='/api')
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/api/healthchecker")
async def healthchecker(db: Session = Depends(get_db)):
    try:
        result = await asyncio.wait_for(db.execute(text("SELECT 1")).fetchone(), timeout=5)
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"status": "OK", "message": "Database connection is healthy"}
    except asyncio.TimeoutError:
        raise HTTPException(status_code=500, detail="Timeout error: Database is not responding")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error connecting to the database")


if __name__ == '__main__':
    uvicorn.run('main:app', port=8000, reload=True)
