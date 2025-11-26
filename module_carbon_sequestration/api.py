from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from .pipeline import run_pipeline

app = FastAPI(title="Carbon Sequestration API", version="0.1.0")

class CarbonRequest(BaseModel):
    location: Optional[str] = None

@app.get('/health')
async def health():
    return {'status':'ok'}

@app.post('/carbon-sequestration')
async def carbon(req: CarbonRequest):
    try:
        rows = run_pipeline()
        if req.location:
            rows = [r for r in rows if r.get('location') == req.location]
        return {'count': len(rows), 'results': rows[:25]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {e}")
