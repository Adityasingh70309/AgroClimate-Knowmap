from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from .pipeline import run_pipeline

app = FastAPI(title='Climate Smart Farming API', version='0.1.0')

class StrategyRequest(BaseModel):
    location: Optional[str] = None
    crop: Optional[str] = None

@app.get('/health')
async def health():
    return {'status':'ok'}

@app.post('/recommend-strategy')
async def recommend(req: StrategyRequest):
    try:
        rows = run_pipeline()
        if req.location:
            rows = [r for r in rows if r.get('location') == req.location]
        if req.crop:
            rows = [r for r in rows if r.get('crop') == req.crop]
        return {'count': len(rows), 'results': rows[:25]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Strategy pipeline failed: {e}")
