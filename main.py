import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from database import create_document, get_documents, db
from schemas import Lead

app = FastAPI(title="RZ-CLEAN-SEAL API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "RZ-CLEAN-SEAL API a funcionar"}


@app.get("/api/hello")
def hello():
    return {"message": "Bem-vindo à API da RZ-CLEAN-SEAL"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = getattr(db, 'name', 'unknown')
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    return response


# -------- Leads Endpoints ---------
@app.post("/api/leads")
def create_lead(lead: Lead):
    try:
        doc_id = create_document("lead", lead)
        return {"status": "ok", "id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class LeadQuery(BaseModel):
    email: Optional[str] = None
    tipo: Optional[str] = None


@app.get("/api/leads")
def list_leads(email: Optional[str] = None, tipo: Optional[str] = None, limit: int = 50):
    try:
        filtro = {}
        if email:
            filtro["email"] = email
        if tipo:
            filtro["tipo"] = tipo
        leads = get_documents("lead", filtro, limit)
        # Convert ObjectId to string
        for l in leads:
            if "_id" in l:
                l["_id"] = str(l["_id"])
        return {"items": leads, "count": len(leads)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
