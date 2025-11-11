"""
Database Schemas for DNA Health Tracker

Each Pydantic model maps to a MongoDB collection with the lowercase class name.
- UserProfile -> "userprofile"
- GeneticMarker -> "geneticmarker"
- HealthLog -> "healthlog"

These are used for validation and for the database viewer via GET /schema.
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal

class UserProfile(BaseModel):
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address (unique)")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    gender: Optional[Literal["male", "female", "non-binary", "other"]] = Field(None, description="Gender identity")

class GeneticMarker(BaseModel):
    user_email: EmailStr = Field(..., description="Link to user by email")
    gene: str = Field(..., description="Gene symbol (e.g., MTHFR)")
    snp: str = Field(..., description="SNP identifier (e.g., rs1801133)")
    risk_level: Literal["low", "moderate", "high"] = Field(..., description="Relative risk level")
    note: Optional[str] = Field(None, description="Optional note/interpretation")

class HealthLog(BaseModel):
    user_email: EmailStr = Field(..., description="Link to user by email")
    mood: Optional[Literal["low", "okay", "good", "great"]] = Field(None, description="Self-reported mood")
    sleep_hours: Optional[float] = Field(None, ge=0, le=24, description="Sleep duration in hours")
    hydration_ml: Optional[int] = Field(None, ge=0, le=10000, description="Water intake in milliliters")
    activity_minutes: Optional[int] = Field(None, ge=0, le=1440, description="Physical activity minutes")
