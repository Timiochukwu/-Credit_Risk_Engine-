"""
FastAPI Application - Nigerian Credit Risk Engine
==================================================

RESTful API for credit risk assessment.

Endpoints:
- POST /token - Get authentication token
- POST /predict - Single prediction
- POST /predict/batch - Batch predictions
- GET /health - Health check
- GET /model/info - Model information
- GET /docs - API documentation (Swagger UI)

Authentication:
- JWT bearer token required for prediction endpoints
- Use /token endpoint to get access token

Run with:
    uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from typing import List
import uuid
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.api.schemas import (
    LoanApplicationRequest, PredictionResponse,
    BatchPredictionRequest, BatchPredictionResponse,
    HealthResponse, Token, User, ModelInfo, ErrorResponse
)
from src.api.auth import (
    authenticate_user, create_access_token,
    get_current_active_user, ACCESS_TOKEN_EXPIRE_MINUTES
)
from src.models.predict import CreditRiskPredictor
from src.utils.config import (
    API_TITLE, API_VERSION, API_DESCRIPTION,
    ALLOWED_ORIGINS, MODELS_DIR
)

# ============================================
# Initialize FastAPI App
# ============================================
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# ============================================
# CORS Middleware
# ============================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# Global Predictor (loaded on startup)
# ============================================
predictor = None


@app.on_event("startup")
async def startup_event():
    """
    Load model on application startup.

    This ensures the model is loaded once and reused for all requests,
    improving performance.
    """
    global predictor
    try:
        print("\n" + "="*70)
        print(" "*15 + "STARTING NIGERIAN CREDIT RISK API")
        print("="*70)

        predictor = CreditRiskPredictor(model_name="xgboost")

        print("\n✓ Model loaded successfully")
        print(f"✓ API ready at http://localhost:8000")
        print(f"✓ Documentation at http://localhost:8000/docs")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\n⚠ Warning: Could not load model: {str(e)}")
        print("⚠ API will start but predictions will fail")
        print("⚠ Please train model first: python src/models/train.py\n")


# ============================================
# Authentication Endpoints
# ============================================

@app.post("/token", response_model=Token, tags=["Authentication"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Get access token for authentication.

    **Demo Credentials:**
    - Username: `admin`, Password: `password123`
    - Username: `loan_officer`, Password: `password123`
    - Username: `analyst`, Password: `password123`

    Returns a JWT token that expires in 30 minutes.
    Use this token in the Authorization header: `Bearer <token>`
    """
    user = authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=User, tags=["Authentication"])
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Get current user information.

    Requires authentication token.
    """
    return current_user


# ============================================
# Health Check
# ============================================

@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """
    Health check endpoint.

    Returns service status and model information.
    No authentication required.
    """
    return HealthResponse(
        status="healthy" if predictor is not None else "degraded",
        model_loaded=predictor is not None,
        model_name=predictor.model_name if predictor else "none"
    )


@app.get("/", tags=["System"])
async def root():
    """
    Root endpoint - API information.
    """
    return {
        "name": API_TITLE,
        "version": API_VERSION,
        "description": API_DESCRIPTION,
        "status": "operational",
        "documentation": "/docs",
        "health": "/health"
    }


# ============================================
# Prediction Endpoints
# ============================================

@app.post("/predict", response_model=PredictionResponse, tags=["Predictions"])
async def predict_single(
    application: LoanApplicationRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Make a credit risk prediction for a single loan application.

    **Requires Authentication** - Include JWT token in Authorization header.

    **Process:**
    1. Validates application data
    2. Engineers features
    3. Runs through ML model
    4. Returns risk assessment and recommendation

    **Risk Categories:**
    - VERY_LOW (< 5%): Auto-approve with best terms
    - LOW (5-15%): Auto-approve with standard terms
    - MEDIUM (15-30%): Approve with conditions
    - HIGH (30-50%): Manual review required
    - VERY_HIGH (> 50%): Reject

    **Example:**
    ```python
    import requests

    # Get token
    token_response = requests.post(
        "http://localhost:8000/token",
        data={"username": "admin", "password": "password123"}
    )
    token = token_response.json()["access_token"]

    # Make prediction
    headers = {"Authorization": f"Bearer {token}"}
    application = {
        "full_name": "Adebayo Ogunleye",
        "age": 35,
        # ... other fields
    }
    response = requests.post(
        "http://localhost:8000/predict",
        json=application,
        headers=headers
    )
    print(response.json())
    ```
    """
    if predictor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded. Please contact administrator."
        )

    try:
        # Convert Pydantic model to dict
        app_dict = application.dict()

        # Add application ID if not present
        if "application_id" not in app_dict or not app_dict["application_id"]:
            app_dict["application_id"] = f"NGN{uuid.uuid4().hex[:8].upper()}"

        # Calculate monthly payment (simplified)
        loan_amount = app_dict["loan_amount"]
        term_months = app_dict["loan_term_months"]
        interest_rate = app_dict["interest_rate"]

        monthly_rate = interest_rate / 100 / 12
        if monthly_rate > 0:
            monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**term_months) / \
                            ((1 + monthly_rate)**term_months - 1)
        else:
            monthly_payment = loan_amount / term_months

        app_dict["monthly_payment"] = monthly_payment

        # Make prediction
        result = predictor.predict_single(app_dict)

        # Add timestamp
        result["timestamp"] = datetime.now()

        return PredictionResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction error: {str(e)}"
        )


@app.post("/predict/batch", response_model=BatchPredictionResponse, tags=["Predictions"])
async def predict_batch(
    batch_request: BatchPredictionRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Make credit risk predictions for multiple loan applications.

    **Requires Authentication** - Include JWT token in Authorization header.

    **Limitations:**
    - Maximum 100 applications per batch
    - Processing time increases with batch size

    **Returns:**
    - Individual predictions for each application
    - Summary statistics for the batch
    """
    if predictor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded. Please contact administrator."
        )

    try:
        applications = []

        for app in batch_request.applications:
            app_dict = app.dict()

            # Add application ID if not present
            if "application_id" not in app_dict or not app_dict["application_id"]:
                app_dict["application_id"] = f"NGN{uuid.uuid4().hex[:8].upper()}"

            # Calculate monthly payment
            loan_amount = app_dict["loan_amount"]
            term_months = app_dict["loan_term_months"]
            interest_rate = app_dict["interest_rate"]

            monthly_rate = interest_rate / 100 / 12
            if monthly_rate > 0:
                monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**term_months) / \
                                ((1 + monthly_rate)**term_months - 1)
            else:
                monthly_payment = loan_amount / term_months

            app_dict["monthly_payment"] = monthly_payment
            applications.append(app_dict)

        # Make batch predictions
        results_df = predictor.predict_batch(applications)

        # Convert to list of PredictionResponse
        predictions = []
        for _, row in results_df.iterrows():
            pred = row.to_dict()
            pred["timestamp"] = datetime.now()
            predictions.append(PredictionResponse(**pred))

        # Calculate summary
        summary = {
            "total_applications": len(predictions),
            "risk_distribution": results_df['risk_category'].value_counts().to_dict(),
            "decision_distribution": results_df['decision'].value_counts().to_dict(),
            "average_default_probability": float(results_df['default_probability'].mean()),
            "total_loan_amount": float(results_df['loan_amount'].sum())
        }

        return BatchPredictionResponse(
            total_applications=len(predictions),
            predictions=predictions,
            summary=summary
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch prediction error: {str(e)}"
        )


# ============================================
# Model Information
# ============================================

@app.get("/model/info", response_model=ModelInfo, tags=["Model"])
async def get_model_info(current_user: User = Depends(get_current_active_user)):
    """
    Get information about the loaded model.

    **Requires Authentication**

    Returns model name, type, version, and performance metrics.
    """
    if predictor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded"
        )

    # Try to load model metadata
    try:
        import joblib
        metadata_path = MODELS_DIR / "model_metadata.pkl"
        metadata = joblib.load(metadata_path)

        return ModelInfo(
            model_name=predictor.model_name,
            model_type="XGBoost" if "xgb" in predictor.model_name.lower() else "Unknown",
            version=API_VERSION,
            trained_date=metadata.get("timestamp", "Unknown"),
            performance_metrics=metadata.get("all_scores", {})
        )
    except:
        return ModelInfo(
            model_name=predictor.model_name,
            model_type="Unknown",
            version=API_VERSION,
            trained_date=None,
            performance_metrics=None
        )


# ============================================
# Error Handlers
# ============================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.__class__.__name__,
            message=exc.detail,
            detail=str(exc)
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler."""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="InternalServerError",
            message="An unexpected error occurred",
            detail=str(exc)
        ).dict()
    )


# ============================================
# Main (for development)
# ============================================

if __name__ == "__main__":
    import uvicorn

    print("\n" + "="*70)
    print(" "*15 + "NIGERIAN CREDIT RISK ENGINE API")
    print("="*70)
    print("\nStarting development server...")
    print("\n📚 API Documentation: http://localhost:8000/docs")
    print("🔐 Demo credentials:")
    print("   Username: admin | Password: password123")
    print("\n" + "="*70 + "\n")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
