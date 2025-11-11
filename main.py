import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import UserProfile, GeneticMarker, HealthLog

app = FastAPI(title="DNA Health Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "DNA Health Tracker Backend is running"}

@app.get("/test")
def test_database():
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
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
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

# Simple schema listing to help the built-in DB viewer
@app.get("/schema")
def get_schema():
    return {
        "userprofile": UserProfile.model_json_schema(),
        "geneticmarker": GeneticMarker.model_json_schema(),
        "healthlog": HealthLog.model_json_schema(),
    }

# API models for create endpoints (reuse schemas)

@app.post("/users", status_code=201)
def create_user(profile: UserProfile):
    try:
        # prevent duplicates by email
        existing = db["userprofile"].find_one({"email": profile.email}) if db else None
        if existing:
            raise HTTPException(status_code=409, detail="User with this email already exists")
        inserted_id = create_document("userprofile", profile)
        return {"id": inserted_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users")
def list_users(limit: int = 50):
    try:
        items = get_documents("userprofile", {}, limit)
        # Convert ObjectId to string for JSON safety
        for it in items:
            if it.get("_id"):
                it["_id"] = str(it["_id"])
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/markers", status_code=201)
def add_marker(marker: GeneticMarker):
    try:
        # ensure user exists
        if db and not db["userprofile"].find_one({"email": marker.user_email}):
            raise HTTPException(status_code=404, detail="User not found for user_email")
        inserted_id = create_document("geneticmarker", marker)
        return {"id": inserted_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/markers")
def list_markers(user_email: Optional[str] = None, limit: int = 100):
    try:
        filt = {"user_email": user_email} if user_email else {}
        items = get_documents("geneticmarker", filt, limit)
        for it in items:
            if it.get("_id"):
                it["_id"] = str(it["_id"])
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/logs", status_code=201)
def add_health_log(log: HealthLog):
    try:
        if db and not db["userprofile"].find_one({"email": log.user_email}):
            raise HTTPException(status_code=404, detail="User not found for user_email")
        inserted_id = create_document("healthlog", log)
        return {"id": inserted_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logs")
def list_health_logs(user_email: Optional[str] = None, limit: int = 100):
    try:
        filt = {"user_email": user_email} if user_email else {}
        items = get_documents("healthlog", filt, limit)
        for it in items:
            if it.get("_id"):
                it["_id"] = str(it["_id"])
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
