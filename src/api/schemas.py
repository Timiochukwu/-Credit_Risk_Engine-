"""
API Schemas
============

Pydantic models for API request/response validation.

These schemas ensure:
- Data type validation
- Required field enforcement
- Documentation for API endpoints
- Type hints for developers
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from datetime import date, datetime


class LoanApplicationRequest(BaseModel):
    """Schema for loan application request."""

    # Personal Information
    full_name: str = Field(..., description="Full name of applicant", example="Adebayo Ogunleye")
    email: Optional[EmailStr] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number", example="08031234567")
    age: int = Field(..., ge=18, le=100, description="Age of applicant", example=35)

    # Education and Employment
    education: str = Field(..., description="Education level", example="B.Sc")
    employment_sector: str = Field(..., description="Employment sector", example="Banking & Finance")
    years_employed: float = Field(..., ge=0, description="Years in current employment", example=8.5)

    # Financial Information
    monthly_income: float = Field(..., gt=0, description="Monthly income in Naira", example=450_000)
    existing_monthly_debt: float = Field(..., ge=0, description="Existing monthly debt obligations", example=80_000)

    # Credit History
    credit_history_months: int = Field(..., ge=0, description="Credit history in months", example=48)
    num_credit_lines: int = Field(..., ge=0, description="Number of existing credit lines", example=2)
    previous_defaults: int = Field(..., ge=0, description="Number of previous defaults", example=0)

    # Banking Information
    bank: str = Field(..., description="Bank name", example="GTBank")
    account_age_years: float = Field(..., ge=0, description="Account age in years", example=6.0)

    # Loan Details
    loan_amount: float = Field(..., gt=0, description="Requested loan amount in Naira", example=2_500_000)
    loan_term_months: int = Field(..., gt=0, le=60, description="Loan term in months", example=24)
    loan_purpose: str = Field(..., description="Purpose of loan", example="Business Expansion")
    interest_rate: float = Field(..., gt=0, description="Proposed interest rate (%)", example=22.0)

    @validator('education')
    def validate_education(cls, v):
        """Validate education level."""
        valid_levels = ['SSCE', 'OND', 'HND', 'B.Sc', 'M.Sc', 'PhD']
        if v not in valid_levels:
            raise ValueError(f'Education must be one of {valid_levels}')
        return v

    @validator('phone')
    def validate_phone(cls, v):
        """Validate Nigerian phone number format."""
        if v is None:
            return v
        # Remove spaces and dashes
        v = v.replace(' ', '').replace('-', '')
        # Nigerian numbers start with 0 and are 11 digits, or +234 and 13 digits
        if not (v.startswith('0') and len(v) == 11) and not (v.startswith('+234') and len(v) == 14):
            raise ValueError('Invalid Nigerian phone number format')
        return v

    class Config:
        schema_extra = {
            "example": {
                "full_name": "Chukwuemeka Okafor",
                "email": "chukwuemeka.okafor@gmail.com",
                "phone": "08031234567",
                "age": 35,
                "education": "B.Sc",
                "employment_sector": "Oil & Gas",
                "years_employed": 8.5,
                "monthly_income": 650_000,
                "existing_monthly_debt": 120_000,
                "credit_history_months": 60,
                "num_credit_lines": 3,
                "previous_defaults": 0,
                "bank": "Access Bank",
                "account_age_years": 7.5,
                "loan_amount": 5_000_000,
                "loan_term_months": 36,
                "loan_purpose": "Business Expansion",
                "interest_rate": 22.5
            }
        }


class PredictionResponse(BaseModel):
    """Schema for prediction response."""

    application_id: str = Field(..., description="Application ID")
    applicant_name: str = Field(..., description="Applicant name")
    loan_amount: float = Field(..., description="Loan amount requested")
    default_probability: float = Field(..., description="Default probability (0-1)")
    default_probability_percent: str = Field(..., description="Default probability as percentage")
    predicted_default: bool = Field(..., description="Binary prediction (True = likely default)")
    risk_category: str = Field(..., description="Risk category (VERY_LOW, LOW, MEDIUM, HIGH, VERY_HIGH)")
    decision: str = Field(..., description="Loan decision recommendation")
    terms: str = Field(..., description="Proposed loan terms")
    reasoning: str = Field(..., description="Reasoning for decision")
    suggested_action: str = Field(..., description="Suggested action for loan officer")
    timestamp: datetime = Field(default_factory=datetime.now, description="Prediction timestamp")

    class Config:
        schema_extra = {
            "example": {
                "application_id": "NGN001234",
                "applicant_name": "Chukwuemeka Okafor",
                "loan_amount": 5_000_000,
                "default_probability": 0.0823,
                "default_probability_percent": "8.23%",
                "predicted_default": False,
                "risk_category": "LOW",
                "decision": "APPROVE",
                "terms": "Standard terms",
                "reasoning": "Good credit profile with low default risk (8.23%)",
                "suggested_action": "Auto-approve with standard terms",
                "timestamp": "2024-01-15T10:30:00"
            }
        }


class BatchPredictionRequest(BaseModel):
    """Schema for batch prediction request."""

    applications: List[LoanApplicationRequest] = Field(..., description="List of loan applications")

    @validator('applications')
    def validate_batch_size(cls, v):
        """Limit batch size."""
        if len(v) > 100:
            raise ValueError('Batch size cannot exceed 100 applications')
        if len(v) == 0:
            raise ValueError('Batch must contain at least one application')
        return v


class BatchPredictionResponse(BaseModel):
    """Schema for batch prediction response."""

    total_applications: int = Field(..., description="Total number of applications processed")
    predictions: List[PredictionResponse] = Field(..., description="List of predictions")
    summary: dict = Field(..., description="Summary statistics")


class HealthResponse(BaseModel):
    """Schema for health check response."""

    status: str = Field(..., description="Service status")
    model_loaded: bool = Field(..., description="Whether model is loaded")
    model_name: str = Field(..., description="Name of loaded model")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


class UserLogin(BaseModel):
    """Schema for user login."""

    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")


class Token(BaseModel):
    """Schema for authentication token."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


class User(BaseModel):
    """Schema for user."""

    username: str = Field(..., description="Username")
    email: Optional[EmailStr] = Field(None, description="Email address")
    full_name: Optional[str] = Field(None, description="Full name")
    disabled: Optional[bool] = Field(False, description="Whether user is disabled")


class ModelInfo(BaseModel):
    """Schema for model information."""

    model_name: str = Field(..., description="Model name")
    model_type: str = Field(..., description="Model type (e.g., XGBoost, LightGBM)")
    version: str = Field(..., description="Model version")
    trained_date: Optional[str] = Field(None, description="Date model was trained")
    performance_metrics: Optional[dict] = Field(None, description="Model performance metrics")


class ErrorResponse(BaseModel):
    """Schema for error responses."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
