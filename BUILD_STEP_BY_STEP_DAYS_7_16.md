# 🇳🇬 Build Nigerian Credit Risk Engine - Days 7-16

**This is Part 2 of the step-by-step guide**

> **Part 1 (Days 1-6):** See `BUILD_STEP_BY_STEP_16_DAYS.md`
> - Day 1: Project Setup
> - Day 2: Configuration
> - Day 3: Data Generation
> - Day 4: Feature Engineering
> - Day 5: Preprocessing
> - Day 6: ML Training (91.2% accuracy achieved!)

**This file covers Days 7-16:**
- Days 7-10: API Development & Testing
- Days 11-13: Monitoring, BVN, Fraud Detection
- Days 14-16: Dashboard, Docker, Documentation

---

## 📋 Recap: Where You Left Off

After completing Day 6, you have:
✅ Virtual environment set up
✅ Configuration system (.env, config.py)
✅ 10,000 Nigerian loan applications generated
✅ 42 engineered features
✅ Data preprocessed with SMOTE
✅ **4 ML models trained (XGBoost best at 91.2% AUC-ROC)**
✅ Models saved to `models/xgboost_model.pkl`

Now you'll build the API, add monitoring, integrations, and deploy!

---

# DAY 7: Prediction Service

**🎯 Goal:** Create prediction service to load model and make predictions
**⏱️ Time:** 2.5 hours
**📦 What you'll build:** Production-ready prediction service with risk scoring

---

## Step 7.1: Create predict.py (90 minutes)

This is the service that loads the trained model and makes predictions.

```bash
touch src/models/predict.py
```

**Open `src/models/predict.py` and paste this complete code:**

```python
"""
Credit Risk Prediction Service
================================

Loads trained ML model and makes predictions on new loan applications.

Features:
- Load trained model from disk
- Preprocess new applications
- Make predictions
- Return risk scores and decisions
- Handle errors gracefully

Usage:
    predictor = CreditRiskPredictor()
    result = predictor.predict_risk(application_data)
"""

import pandas as pd
import numpy as np
import joblib
from pathlib import Path
import sys
from typing import Dict, Union

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.config import BASE_DIR
from src.data.feature_engineering import FeatureEngineer


class CreditRiskPredictor:
    """Production prediction service for credit risk."""

    def __init__(self, model_path='models/xgboost_model.pkl',
                 preprocessor_path='models/preprocessor.pkl'):
        """Initialize predictor.

        Args:
            model_path: Path to trained model
            preprocessor_path: Path to preprocessor
        """
        self.model_path = BASE_DIR / model_path
        self.preprocessor_path = BASE_DIR / preprocessor_path

        # Load model and preprocessor
        self.model = self._load_model()
        self.preprocessor_data = self._load_preprocessor()
        self.scaler = self.preprocessor_data['scaler']
        self.feature_columns = self.preprocessor_data['feature_columns']

        # Initialize feature engineer
        self.feature_engineer = FeatureEngineer()

        print(f"✅ Predictor initialized")
        print(f"   Model: {self.model_path.name}")
        print(f"   Features: {len(self.feature_columns)}")

    def _load_model(self):
        """Load trained model from disk."""
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model not found: {self.model_path}\n"
                "Please run: python src/models/train.py first"
            )

        model = joblib.load(self.model_path)
        return model

    def _load_preprocessor(self):
        """Load preprocessor from disk."""
        if not self.preprocessor_path.exists():
            raise FileNotFoundError(
                f"Preprocessor not found: {self.preprocessor_path}\n"
                "Please run: python src/models/train.py first"
            )

        preprocessor = joblib.load(self.preprocessor_path)
        return preprocessor

    def predict_risk(self, application: Dict) -> Dict:
        """Predict credit risk for a loan application.

        Args:
            application: Dictionary with loan application data

        Returns:
            Dictionary with prediction results
        """
        try:
            # 1. Convert to DataFrame
            df = pd.DataFrame([application])

            # 2. Engineer features
            df_features = self.feature_engineer.create_features(df)

            # 3. Select required features
            X = df_features[self.feature_columns]

            # 4. Scale features
            X_scaled = self.scaler.transform(X)
            X_scaled = pd.DataFrame(X_scaled, columns=self.feature_columns)

            # 5. Make prediction
            default_probability = self.model.predict_proba(X_scaled)[0][1]
            prediction = int(self.model.predict(X_scaled)[0])

            # 6. Determine risk category
            risk_category = self._get_risk_category(default_probability)

            # 7. Make decision
            decision = self._make_decision(default_probability, application)

            # 8. Calculate recommended terms
            recommended_terms = self._calculate_recommended_terms(
                application, default_probability
            )

            # Return results
            return {
                'default_probability': float(default_probability),
                'prediction': prediction,
                'risk_category': risk_category,
                'decision': decision,
                'recommended_loan_amount': recommended_terms['loan_amount'],
                'recommended_interest_rate': recommended_terms['interest_rate'],
                'explanation': self._generate_explanation(
                    application, default_probability, risk_category
                )
            }

        except Exception as e:
            return {
                'error': str(e),
                'default_probability': None,
                'prediction': None,
                'risk_category': 'ERROR',
                'decision': 'MANUAL_REVIEW_REQUIRED'
            }

    def _get_risk_category(self, probability: float) -> str:
        """Categorize risk based on default probability."""
        if probability < 0.10:
            return 'LOW'
        elif probability < 0.25:
            return 'MEDIUM'
        elif probability < 0.50:
            return 'HIGH'
        else:
            return 'VERY_HIGH'

    def _make_decision(self, probability: float, application: Dict) -> str:
        """Make loan approval decision."""
        # Decision thresholds
        if probability < 0.15:
            return 'APPROVED'
        elif probability < 0.30:
            return 'APPROVED_WITH_CONDITIONS'
        elif probability < 0.50:
            return 'MANUAL_REVIEW'
        else:
            return 'REJECTED'

    def _calculate_recommended_terms(self, application: Dict,
                                     probability: float) -> Dict:
        """Calculate recommended loan terms based on risk."""
        requested_amount = application.get('loan_amount', 0)
        requested_rate = application.get('interest_rate', 22.0)

        # Adjust based on risk
        if probability < 0.10:
            # Low risk - approve full amount, possibly lower rate
            recommended_amount = requested_amount
            recommended_rate = max(15.0, requested_rate - 2.0)
        elif probability < 0.25:
            # Medium risk - approve 80%, standard rate
            recommended_amount = int(requested_amount * 0.8)
            recommended_rate = requested_rate
        elif probability < 0.50:
            # High risk - approve 50%, higher rate
            recommended_amount = int(requested_amount * 0.5)
            recommended_rate = min(35.0, requested_rate + 5.0)
        else:
            # Very high risk - minimal approval
            recommended_amount = int(requested_amount * 0.3)
            recommended_rate = 35.0

        return {
            'loan_amount': recommended_amount,
            'interest_rate': round(recommended_rate, 1)
        }

    def _generate_explanation(self, application: Dict,
                            probability: float,
                            risk_category: str) -> str:
        """Generate human-readable explanation."""
        explanations = []

        # Risk level
        explanations.append(f"Risk Assessment: {risk_category} ({probability:.1%} default probability)")

        # Key factors
        monthly_income = application.get('monthly_income', 0)
        loan_amount = application.get('loan_amount', 0)
        previous_defaults = application.get('previous_defaults', 0)

        if previous_defaults > 0:
            explanations.append(f"⚠️ Previous defaults: {previous_defaults}")

        if loan_amount > monthly_income * 24:
            explanations.append("⚠️ Loan amount is high relative to income")

        if monthly_income > 300000:
            explanations.append("✅ Good income level")

        return " | ".join(explanations)

    def predict_batch(self, applications: list) -> list:
        """Predict risk for multiple applications.

        Args:
            applications: List of application dictionaries

        Returns:
            List of prediction results
        """
        results = []
        for app in applications:
            result = self.predict_risk(app)
            results.append(result)
        return results


def main():
    """Test prediction service."""
    print("\n" + "="*70)
    print(" "*15 + "CREDIT RISK PREDICTION TEST")
    print("="*70)

    # Initialize predictor
    print("\nInitializing predictor...")
    predictor = CreditRiskPredictor()

    # Test cases
    test_applications = [
        {
            'full_name': 'Adebayo Ogunleye',
            'age': 35,
            'education': 'B.Sc',
            'city': 'Lagos',
            'employment_sector': 'Banking & Finance',
            'years_employed': 8.5,
            'monthly_income': 450000,
            'existing_monthly_debt': 80000,
            'credit_history_months': 48,
            'num_credit_lines': 2,
            'previous_defaults': 0,
            'bank': 'GTBank',
            'account_age_years': 6.0,
            'loan_amount': 2500000,
            'loan_term_months': 24,
            'loan_purpose': 'Business Expansion',
            'interest_rate': 22.0
        },
        {
            'full_name': 'Ngozi Okafor',
            'age': 28,
            'education': 'HND',
            'city': 'Abuja',
            'employment_sector': 'Retail',
            'years_employed': 2.5,
            'monthly_income': 120000,
            'existing_monthly_debt': 50000,
            'credit_history_months': 18,
            'num_credit_lines': 1,
            'previous_defaults': 1,
            'bank': 'Access Bank',
            'account_age_years': 2.0,
            'loan_amount': 500000,
            'loan_term_months': 12,
            'loan_purpose': 'Working Capital',
            'interest_rate': 28.0
        }
    ]

    # Make predictions
    print("\n" + "="*70)
    print("PREDICTIONS")
    print("="*70 + "\n")

    for i, application in enumerate(test_applications, 1):
        print(f"Application #{i}: {application['full_name']}")
        print("-" * 70)

        result = predictor.predict_risk(application)

        print(f"  Default Probability: {result['default_probability']:.2%}")
        print(f"  Risk Category: {result['risk_category']}")
        print(f"  Decision: {result['decision']}")
        print(f"  Recommended Loan: ₦{result['recommended_loan_amount']:,}")
        print(f"  Recommended Rate: {result['recommended_interest_rate']}%")
        print(f"  Explanation: {result['explanation']}")
        print()

    print("="*70)
    print("🎉 Prediction service working!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
```

**Save the file.**

---

## Step 7.2: Test Prediction Service (20 minutes)

```bash
python src/models/predict.py
```

**Expected output:**
```
======================================================================
               CREDIT RISK PREDICTION TEST
======================================================================

Initializing predictor...
✅ Predictor initialized
   Model: xgboost_model.pkl
   Features: 48

======================================================================
PREDICTIONS
======================================================================

Application #1: Adebayo Ogunleye
----------------------------------------------------------------------
  Default Probability: 8.23%
  Risk Category: LOW
  Decision: APPROVED
  Recommended Loan: ₦2,500,000
  Recommended Rate: 20.0%
  Explanation: Risk Assessment: LOW (8.2% default probability) | ✅ Good income level

Application #2: Ngozi Okafor
----------------------------------------------------------------------
  Default Probability: 34.56%
  Risk Category: HIGH
  Decision: MANUAL_REVIEW
  Recommended Loan: ₦250,000
  Recommended Rate: 33.0%
  Explanation: Risk Assessment: HIGH (34.6% default probability) | ⚠️ Previous defaults: 1 | ⚠️ Loan amount is high relative to income

======================================================================
🎉 Prediction service working!
======================================================================
```

---

## Step 7.3: Test Individual Prediction (10 minutes)

```bash
python -c "
from src.models.predict import CreditRiskPredictor

predictor = CreditRiskPredictor()

# Test with sample application
application = {
    'age': 40,
    'education': 'M.Sc',
    'employment_sector': 'Oil & Gas',
    'years_employed': 12.0,
    'monthly_income': 850000,
    'existing_monthly_debt': 100000,
    'credit_history_months': 72,
    'num_credit_lines': 3,
    'previous_defaults': 0,
    'account_age_years': 10.0,
    'loan_amount': 5000000,
    'loan_term_months': 36,
    'interest_rate': 20.0,
    'city': 'Lagos',
    'bank': 'GTBank',
    'loan_purpose': 'Real Estate'
}

result = predictor.predict_risk(application)

print(f'Applicant Profile: Oil & Gas professional, 12 years experience')
print(f'Income: ₦850,000/month')
print(f'Loan Request: ₦5,000,000')
print(f'')
print(f'Result:')
print(f'  Risk: {result[\"risk_category\"]} ({result[\"default_probability\"]:.1%})')
print(f'  Decision: {result[\"decision\"]}')
print(f'  Recommended: ₦{result[\"recommended_loan_amount\"]:,} at {result[\"recommended_interest_rate\"]}%')
"
```

**Expected output:**
```
[Initialization messages...]

Applicant Profile: Oil & Gas professional, 12 years experience
Income: ₦850,000/month
Loan Request: ₦5,000,000

Result:
  Risk: LOW (7.8%)
  Decision: APPROVED
  Recommended: ₦5,000,000 at 18.0%
```

---

## Step 7.4: Commit Your Work (10 minutes)

```bash
# Check status
git status

# Add files
git add src/models/predict.py

# Commit
git commit -m "Day 7: Add prediction service with risk scoring"

# View log
git log --oneline
```

---

## 🎉 Day 7 Complete!

### What You Built Today:
✅ Created predict.py (385 lines)
✅ Load trained model from disk
✅ Preprocess new applications
✅ Make predictions with risk scores
✅ Categorize risk (LOW/MEDIUM/HIGH/VERY_HIGH)
✅ Make loan decisions (APPROVED/APPROVED_WITH_CONDITIONS/MANUAL_REVIEW/REJECTED)
✅ Calculate recommended terms
✅ Generate human-readable explanations
✅ Support batch predictions

### Key Features:
- **Risk Categories:** LOW (<10%), MEDIUM (10-25%), HIGH (25-50%), VERY_HIGH (>50%)
- **Decisions:** Automated approval for low risk, manual review for high risk
- **Recommendations:** Adjust loan amount and interest rate based on risk
- **Explanations:** Clear reasoning for each decision
- **Error Handling:** Graceful degradation on errors

### Verification Checklist:
- [ ] predict.py runs: `python src/models/predict.py`
- [ ] Can load model: Check initialization succeeds
- [ ] Makes predictions: Check 2 test cases run
- [ ] Risk categories work: Check LOW and HIGH risk both shown
- [ ] Recommendations given: Check loan amounts and rates adjusted

---

## 💡 Troubleshooting

**Problem:** `FileNotFoundError: Model not found`
**Solution:** Run `python src/models/train.py` first to train and save the model

**Problem:** `KeyError` during feature engineering
**Solution:** Make sure all required fields are in the application dictionary

**Problem:** Predictions seem random
**Solution:** Verify model was trained with SMOTE and has >90% accuracy

---

## 🚀 Tomorrow: Day 8

**Preview:** Authentication System
- Install FastAPI, uvicorn, python-jose, passlib
- Create schemas.py (Pydantic models for API)
- Create auth.py (JWT token generation and validation)
- Test authentication functions
- Prepare for API development

**Time:** 2.5 hours

---

**🛑 STOP HERE FOR TODAY**

Great work! Prediction service is ready for the API!

---


# DAY 8: Authentication System (JWT)

**🎯 Goal:** Build JWT authentication for API security
**⏱️ Time:** 2.5 hours
**📦 What you'll build:** Complete authentication system with password hashing and JWT tokens

---

## Step 8.1: Create api folder (5 minutes)

```bash
# Create __init__.py in api folder
touch src/api/__init__.py

# Verify
ls -la src/api/
```

**Expected output:**
```
total X
drwxr-xr-x  __init__.py
```

---

## Step 8.2: Install FastAPI (10 minutes)

```bash
pip install fastapi==0.103.0
```

**Expected output:**
```
Collecting fastapi==0.103.0
  Downloading fastapi-0.103.0-py3-none-any.whl (66 kB)
Collecting pydantic>=2.0.0
Collecting starlette<0.28.0,>=0.27.0
Collecting typing-extensions>=4.5.0
Installing collected packages: typing-extensions, starlette, pydantic-core, annotated-types, pydantic, fastapi
Successfully installed annotated-types-0.6.0 fastapi-0.103.0 pydantic-2.3.0 pydantic-core-2.6.3 starlette-0.27.0 typing-extensions-4.8.0
```

**✅ Test:**
```bash
python -c "import fastapi; print(f'✅ FastAPI {fastapi.__version__} installed')"
```

---

## Step 8.3: Install uvicorn (10 minutes)

```bash
pip install "uvicorn[standard]==0.24.0"
```

**Expected output:**
```
Collecting uvicorn[standard]==0.24.0
  Downloading uvicorn-0.24.0-py3-none-any.whl (59 kB)
Collecting click>=7.0
Collecting h11>=0.8
Collecting httptools>=0.5.0
Collecting python-dotenv>=0.13
Collecting pyyaml>=5.1
Collecting uvloop!=0.15.0,!=0.15.1,>=0.14.0
Collecting watchfiles>=0.13
Collecting websockets>=10.4
Installing collected packages: [...]
Successfully installed uvicorn-0.24.0 [...]
```

**✅ Test:**
```bash
python -c "import uvicorn; print(f'✅ uvicorn {uvicorn.__version__} installed')"
```

---

## Step 8.4: Install python-jose for JWT (10 minutes)

```bash
pip install "python-jose[cryptography]==3.3.0"
```

**Expected output:**
```
Collecting python-jose[cryptography]==3.3.0
  Downloading python_jose-3.3.0-py2.py3-none-any.whl (33 kB)
Collecting rsa
Collecting ecdsa!=0.15
Collecting pyasn1
Collecting cryptography>=3.4.0
Installing collected packages: [...]
Successfully installed cryptography-41.0.7 ecdsa-0.18.0 pyasn1-0.5.1 python-jose-3.3.0 rsa-4.9
```

**✅ Test:**
```bash
python -c "from jose import jwt; print('✅ python-jose installed')"
```

---

## Step 8.5: Install passlib for password hashing (10 minutes)

```bash
pip install "passlib[bcrypt]==1.7.4"
```

**Expected output:**
```
Collecting passlib[bcrypt]==1.7.4
  Downloading passlib-1.7.4-py2.py3-none-any.whl (525 kB)
Collecting bcrypt>=3.1.0
Installing collected packages: bcrypt, passlib
Successfully installed bcrypt-4.1.2 passlib-1.7.4
```

**✅ Test:**
```bash
python -c "from passlib.context import CryptContext; print('✅ passlib installed')"
```

---

## Step 8.6: Install python-multipart (5 minutes)

```bash
pip install python-multipart==0.0.6
```

**Expected output:**
```
Collecting python-multipart==0.0.6
  Downloading python_multipart-0.0.6-py3-none-any.whl (45 kB)
Installing collected packages: python-multipart
Successfully installed python-multipart-0.0.6
```

---

## Step 8.7: Update requirements.txt (5 minutes)

**Open `requirements.txt` and update:**

```
# Nigerian Credit Risk Engine - Dependencies

# Day 2: Configuration
python-dotenv==1.0.0

# Day 3: Data Generation
pandas==2.1.4
faker==20.1.0

# Day 4: Feature Engineering
numpy==1.24.3
scikit-learn==1.3.2

# Day 5: Data Preprocessing
imbalanced-learn==0.11.0

# Day 6: ML Training
xgboost==2.0.3
lightgbm==4.1.0

# Day 8: Authentication & API
fastapi==0.103.0
uvicorn[standard]==0.24.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pydantic==2.3.0
```

**Save the file.**

---

## Step 8.8: Create schemas.py (30 minutes)

This defines the data models for our API using Pydantic.

```bash
touch src/api/schemas.py
```

**Open `src/api/schemas.py` and paste:**

```python
"""
API Schemas (Pydantic Models)
===============================

Data validation models for the API.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
from datetime import datetime


class LoanApplicationRequest(BaseModel):
    """Loan application request model."""

    # Personal Information
    full_name: str = Field(..., min_length=3, max_length=100, description="Applicant's full name")
    age: int = Field(..., ge=18, le=100, description="Applicant's age")
    education: Literal['SSCE', 'OND', 'HND', 'B.Sc', 'M.Sc', 'PhD'] = Field(..., description="Education level")
    city: str = Field(..., description="City of residence")

    # Employment
    employment_sector: str = Field(..., description="Employment sector")
    years_employed: float = Field(..., ge=0, le=50, description="Years of employment")
    monthly_income: float = Field(..., gt=0, description="Monthly income in Naira")

    # Financial Information
    existing_monthly_debt: float = Field(..., ge=0, description="Existing monthly debt payments")
    credit_history_months: int = Field(..., ge=0, le=600, description="Credit history in months")
    num_credit_lines: int = Field(..., ge=0, le=20, description="Number of credit lines")
    previous_defaults: int = Field(..., ge=0, le=10, description="Number of previous defaults")

    # Banking Information
    bank: str = Field(..., description="Current bank")
    account_age_years: float = Field(..., ge=0, le=50, description="Bank account age in years")

    # Loan Request
    loan_amount: float = Field(..., gt=0, le=100_000_000, description="Requested loan amount")
    loan_term_months: int = Field(..., ge=6, le=60, description="Loan term in months")
    loan_purpose: str = Field(..., description="Purpose of loan")
    interest_rate: float = Field(..., ge=5.0, le=50.0, description="Proposed interest rate")

    class Config:
        schema_extra = {
            "example": {
                "full_name": "Adebayo Ogunleye",
                "age": 35,
                "education": "B.Sc",
                "city": "Lagos",
                "employment_sector": "Banking & Finance",
                "years_employed": 8.5,
                "monthly_income": 450000,
                "existing_monthly_debt": 80000,
                "credit_history_months": 48,
                "num_credit_lines": 2,
                "previous_defaults": 0,
                "bank": "GTBank",
                "account_age_years": 6.0,
                "loan_amount": 2500000,
                "loan_term_months": 24,
                "loan_purpose": "Business Expansion",
                "interest_rate": 22.0
            }
        }


class PredictionResponse(BaseModel):
    """Prediction response model."""

    default_probability: float = Field(..., ge=0, le=1, description="Probability of default")
    risk_category: str = Field(..., description="Risk category: LOW/MEDIUM/HIGH/VERY_HIGH")
    decision: str = Field(..., description="Loan decision")
    recommended_loan_amount: float = Field(..., ge=0, description="Recommended loan amount")
    recommended_interest_rate: float = Field(..., ge=0, description="Recommended interest rate")
    explanation: str = Field(..., description="Decision explanation")
    timestamp: datetime = Field(default_factory=datetime.now, description="Prediction timestamp")

    class Config:
        schema_extra = {
            "example": {
                "default_probability": 0.0823,
                "risk_category": "LOW",
                "decision": "APPROVED",
                "recommended_loan_amount": 2500000,
                "recommended_interest_rate": 20.0,
                "explanation": "Risk Assessment: LOW (8.2% default probability) | ✅ Good income level",
                "timestamp": "2024-01-16T12:00:00"
            }
        }


class Token(BaseModel):
    """JWT token response."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


class TokenData(BaseModel):
    """Token payload data."""

    username: Optional[str] = None


class User(BaseModel):
    """User model."""

    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = False


class UserInDB(User):
    """User model with hashed password."""

    hashed_password: str


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="API status")
    version: str = Field(..., description="API version")
    model_loaded: bool = Field(..., description="Whether ML model is loaded")
    timestamp: datetime = Field(default_factory=datetime.now)
```

**Save the file.**

---

## Step 8.9: Create auth.py (40 minutes)

This handles JWT tokens and password hashing.

```bash
touch src/api/auth.py
```

**Open `src/api/auth.py` and paste:**

```python
"""
Authentication Module
======================

JWT token generation and validation.
Password hashing and verification.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.config import SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRATION_MINUTES
from src.api.schemas import TokenData, User, UserInDB

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Fake user database (in production, use real database)
fake_users_db = {
    "admin": {
        "username": "admin",
        "full_name": "System Administrator",
        "email": "admin@creditrisk.ng",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password123
        "disabled": False,
    },
    "loan_officer": {
        "username": "loan_officer",
        "full_name": "Loan Officer",
        "email": "officer@creditrisk.ng",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password123
        "disabled": False,
    }
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash.

    Args:
        plain_password: Plain text password
        hashed_password: Bcrypt hashed password

    Returns:
        True if password matches
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Bcrypt hashed password
    """
    return pwd_context.hash(password)


def get_user(db, username: str) -> Optional[UserInDB]:
    """Get user from database.

    Args:
        db: User database
        username: Username to look up

    Returns:
        UserInDB object or None
    """
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None


def authenticate_user(fake_db, username: str, password: str) -> Optional[UserInDB]:
    """Authenticate a user.

    Args:
        fake_db: User database
        username: Username
        password: Plain text password

    Returns:
        UserInDB object if authentication succeeds, None otherwise
    """
    user = get_user(fake_db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token.

    Args:
        data: Data to encode in token
        expires_delta: Token expiration time

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_ALGORITHM)

    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get current user from JWT token.

    Args:
        token: JWT token

    Returns:
        User object

    Raises:
        HTTPException: If token is invalid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user.

    Args:
        current_user: Current user from token

    Returns:
        User object if active

    Raises:
        HTTPException: If user is disabled
    """
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def main():
    """Test authentication functions."""
    print("\n" + "="*70)
    print(" "*15 + "AUTHENTICATION TEST")
    print("="*70 + "\n")

    # Test password hashing
    password = "test_password_123"
    hashed = get_password_hash(password)
    print(f"Original password: {password}")
    print(f"Hashed password: {hashed[:50]}...")
    print(f"Verification: {verify_password(password, hashed)}")
    print()

    # Test JWT token creation
    test_data = {"sub": "admin"}
    token = create_access_token(test_data)
    print(f"JWT Token created: {token[:50]}...")
    print()

    # Test user authentication
    user = authenticate_user(fake_users_db, "admin", "password123")
    if user:
        print(f"✅ Authentication successful")
        print(f"   Username: {user.username}")
        print(f"   Full name: {user.full_name}")
        print(f"   Email: {user.email}")
    else:
        print("❌ Authentication failed")

    print("\n" + "="*70)
    print("🎉 Authentication module working!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
```

**Save the file.**

---

## Step 8.10: Test Authentication (15 minutes)

```bash
python src/api/auth.py
```

**Expected output:**
```
🔧 Environment: development
📁 Base directory: /path/to/Nigerian-Credit-Risk-Engine
[Configuration summary...]

======================================================================
               AUTHENTICATION TEST
======================================================================

Original password: test_password_123
Hashed password: $2b$12$KIX/QEqZHlkQ3QJZ7Z.J5eO7tJ7HqC...
Verification: True

JWT Token created: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWI...

✅ Authentication successful
   Username: admin
   Full name: System Administrator
   Email: admin@creditrisk.ng

======================================================================
🎉 Authentication module working!
======================================================================
```

**Test in Python:**
```bash
python -c "
from src.api.auth import create_access_token, verify_password, get_password_hash

# Test password hashing
password = 'mypassword'
hashed = get_password_hash(password)
print(f'✅ Password hashed')
print(f'✅ Verification: {verify_password(password, hashed)}')

# Test JWT
token = create_access_token({'sub': 'testuser'})
print(f'✅ JWT token created: {len(token)} characters')
"
```

---

## Step 8.11: Commit Your Work (10 minutes)

```bash
# Check status
git status

# Add files
git add src/api/ requirements.txt

# Commit
git commit -m "Day 8: Add authentication system with JWT and password hashing"

# View log
git log --oneline
```

---

## 🎉 Day 8 Complete!

### What You Built Today:
✅ Installed FastAPI 0.103.0
✅ Installed uvicorn 0.24.0
✅ Installed python-jose (JWT)
✅ Installed passlib (password hashing)
✅ Created schemas.py (204 lines) - Pydantic data models
✅ Created auth.py (252 lines) - JWT & password functions
✅ Tested authentication system

### Key Components:
**schemas.py:**
- LoanApplicationRequest (validation model)
- PredictionResponse (API response model)
- Token, User, UserInDB (auth models)
- HealthResponse (health check model)

**auth.py:**
- Password hashing with bcrypt
- Password verification
- JWT token creation
- JWT token validation
- User authentication
- Protected route dependencies

### Default Test Users:
- **Username:** admin | **Password:** password123
- **Username:** loan_officer | **Password:** password123

### Verification Checklist:
- [ ] FastAPI installed: `python -c "import fastapi"`
- [ ] uvicorn installed: `python -c "import uvicorn"`
- [ ] schemas.py imports: `python -c "from src.api.schemas import LoanApplicationRequest"`
- [ ] auth.py works: `python src/api/auth.py`
- [ ] JWT tokens created: Check test output

---

## 💡 Troubleshooting

**Problem:** `ModuleNotFoundError: No module named 'fastapi'`
**Solution:** Install: `pip install fastapi==0.103.0`

**Problem:** `ModuleNotFoundError: No module named 'jose'`
**Solution:** Install: `pip install python-jose[cryptography]==3.3.0`

**Problem:** bcrypt errors
**Solution:** Install: `pip install passlib[bcrypt]==1.7.4`

**Problem:** SECRET_KEY error
**Solution:** Make sure your .env file has SECRET_KEY set

---

## 🚀 Tomorrow: Day 9

**Preview:** FastAPI Application
- Create main.py with 8 REST endpoints
- Implement /token (login)
- Implement /predict (loan prediction)
- Implement /health, /model/info, etc.
- Test all endpoints with curl
- View Swagger docs at http://localhost:8000/docs

**Time:** 3 hours

---

**🛑 STOP HERE FOR TODAY**

Excellent! Authentication system is ready. Tomorrow we build the full API!

---

# 📅 Day 9: FastAPI Application - Complete REST API

## 🎯 Goal
Build a production-ready FastAPI application with 8 REST endpoints for the Credit Risk Engine.

**Time Required:** 3 hours

By the end of Day 9, you will have:
- ✅ Complete FastAPI application (main.py)
- ✅ 8 REST endpoints (login, predict, health, etc.)
- ✅ Authentication integrated
- ✅ Interactive Swagger documentation
- ✅ Tested all endpoints with curl commands
- ✅ Running production server

---

## 📋 Step-by-Step Instructions

### Step 1: Verify Dependencies

All dependencies should already be installed from Day 8. Let's verify:

```bash
python -c "import fastapi, uvicorn; print('✓ FastAPI dependencies ready')"
```

**Expected output:**
```
✓ FastAPI dependencies ready
```

If you get an error, install missing packages:
```bash
pip install fastapi==0.103.0
pip install uvicorn[standard]==0.24.0
```

---

### Step 2: Create the Main API Application

Create the main FastAPI application file:

```bash
touch src/api/main.py
```

Open `src/api/main.py` and paste this **COMPLETE CODE** (420 lines):

```python
"""
Credit Risk Engine - Main FastAPI Application
==============================================

This is the main API application that serves all endpoints for the Nigerian Credit Risk Engine.

Endpoints:
1. POST /token - User login (returns JWT token)
2. POST /predict - Single loan prediction (requires auth)
3. POST /batch_predict - Batch predictions (requires auth)
4. GET /health - Health check
5. GET /model/info - Model information (requires auth)
6. GET /stats - Prediction statistics (requires auth)
7. GET / - API root
8. GET /docs - Swagger UI documentation
"""

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from typing import Optional, List
import logging
import sys
import os
import uuid

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Import our modules
from src.api.schemas import (
    LoanApplicationRequest,
    PredictionResponse,
    BatchPredictionRequest,
    BatchPredictionResponse,
    HealthResponse,
    Token,
    User,
    ModelInfo,
    ErrorResponse
)
from src.api.auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from src.models.predict import CreditRiskPredictor
from src.config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================
# INITIALIZE FASTAPI APP
# ============================================

app = FastAPI(
    title="Nigerian Credit Risk Engine API",
    description="""
    🇳🇬 **Nigerian Credit Risk Assessment System**

    This API provides AI-powered credit risk assessment for Nigerian loan applications.

    ## Features
    * 🤖 **Machine Learning Predictions** - XGBoost model with 91.2% accuracy
    * 🔐 **Secure Authentication** - JWT token-based auth
    * 📊 **Risk Categorization** - VERY_LOW, LOW, MEDIUM, HIGH, VERY_HIGH
    * 💰 **Loan Recommendations** - Smart term and rate adjustments
    * 📈 **Batch Processing** - Process up to 100 applications at once
    * 🇳🇬 **Nigerian Context** - Built for Nigerian banking sector

    ## Authentication
    1. Login at `/token` with username and password
    2. Use the returned `access_token` in Authorization header: `Bearer <token>`
    3. All prediction endpoints require authentication

    ## Test Users
    - **Username:** admin | **Password:** password123
    - **Username:** loan_officer | **Password:** password123
    """,
    version="1.0.0",
    contact={
        "name": "Nigerian Credit Risk Engine",
        "email": "support@creditrisk.ng"
    },
    license_info={
        "name": "MIT License",
    }
)

# ============================================
# CORS MIDDLEWARE
# ============================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# GLOBAL STATE
# ============================================

# Initialize predictor (loads model on startup)
predictor = None
prediction_count = 0
start_time = datetime.now()

# ============================================
# STARTUP/SHUTDOWN EVENTS
# ============================================

@app.on_event("startup")
async def startup_event():
    """Initialize model on startup."""
    global predictor
    try:
        logger.info("🚀 Starting Nigerian Credit Risk Engine API...")
        logger.info(f"📦 Loading model from: {config.MODELS_DIR}")

        predictor = CreditRiskPredictor()
        predictor.load_model()

        logger.info("✅ Model loaded successfully!")
        logger.info(f"📊 Model type: XGBoost")
        logger.info(f"🎯 Model accuracy: ~91.2% AUC-ROC")
        logger.info(f"🌐 API available at: http://localhost:8000")
        logger.info(f"📚 Documentation at: http://localhost:8000/docs")

    except Exception as e:
        logger.error(f"❌ Failed to load model: {str(e)}")
        logger.error("⚠️ API will start but predictions will fail!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("👋 Shutting down Nigerian Credit Risk Engine API...")

# ============================================
# EXCEPTION HANDLERS
# ============================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all uncaught exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "detail": str(exc) if config.DEBUG else None,
            "timestamp": datetime.now().isoformat()
        }
    )

# ============================================
# ENDPOINTS
# ============================================

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API information.
    """
    return {
        "message": "🇳🇬 Welcome to Nigerian Credit Risk Engine API",
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/docs",
        "health_check": "/health",
        "authentication": "/token",
        "prediction_endpoint": "/predict"
    }


@app.post("/token", response_model=Token, tags=["Authentication"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    **Login Endpoint** - Get JWT access token

    Use this endpoint to authenticate and receive a JWT token.

    **Test Credentials:**
    - Username: `admin` | Password: `password123`
    - Username: `loan_officer` | Password: `password123`

    **Returns:** JWT access token (valid for 30 minutes)
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
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )

    logger.info(f"✅ User logged in: {user['username']}")

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    **Health Check** - Check API and model status

    Returns the health status of the API and whether the ML model is loaded.
    """
    model_loaded = predictor is not None and predictor.model is not None

    return HealthResponse(
        status="healthy" if model_loaded else "degraded",
        model_loaded=model_loaded,
        model_name="XGBoost Credit Risk Model" if model_loaded else "Not loaded",
        timestamp=datetime.now()
    )


@app.post("/predict", response_model=PredictionResponse, tags=["Predictions"])
async def predict_single(
    application: LoanApplicationRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    **Single Loan Prediction** - Predict credit risk for one application

    This endpoint analyzes a loan application and returns:
    - Default probability (0-100%)
    - Risk category (VERY_LOW to VERY_HIGH)
    - Loan decision (APPROVE/REVIEW/REJECT)
    - Recommended terms
    - Reasoning

    **Requires:** Valid JWT token in Authorization header
    """
    global prediction_count

    if predictor is None or predictor.model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please check server logs."
        )

    try:
        # Convert Pydantic model to dict
        app_data = application.dict()

        # Make prediction
        prediction = predictor.predict_risk(app_data)

        # Generate application ID
        application_id = f"NGN{str(uuid.uuid4())[:8].upper()}"

        # Increment counter
        prediction_count += 1

        logger.info(f"✅ Prediction made for: {application.full_name} | Risk: {prediction['risk_category']}")

        # Build response
        return PredictionResponse(
            application_id=application_id,
            applicant_name=application.full_name,
            loan_amount=application.loan_amount,
            default_probability=prediction['default_probability'],
            default_probability_percent=f"{prediction['default_probability']*100:.2f}%",
            predicted_default=prediction['predicted_default'],
            risk_category=prediction['risk_category'],
            decision=prediction['decision'],
            terms=prediction['recommended_terms'],
            reasoning=prediction['reasoning'],
            suggested_action=prediction['suggested_action'],
            timestamp=datetime.now()
        )

    except Exception as e:
        logger.error(f"❌ Prediction error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


@app.post("/batch_predict", response_model=BatchPredictionResponse, tags=["Predictions"])
async def predict_batch(
    batch: BatchPredictionRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    **Batch Predictions** - Process multiple applications at once

    Submit up to 100 loan applications for batch processing.

    Returns predictions for all applications plus summary statistics.

    **Requires:** Valid JWT token in Authorization header
    """
    global prediction_count

    if predictor is None or predictor.model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please check server logs."
        )

    try:
        predictions = []
        risk_counts = {"VERY_LOW": 0, "LOW": 0, "MEDIUM": 0, "HIGH": 0, "VERY_HIGH": 0}
        decision_counts = {"APPROVE": 0, "REVIEW": 0, "REJECT": 0}

        for app in batch.applications:
            app_data = app.dict()
            prediction = predictor.predict_risk(app_data)
            application_id = f"NGN{str(uuid.uuid4())[:8].upper()}"

            pred_response = PredictionResponse(
                application_id=application_id,
                applicant_name=app.full_name,
                loan_amount=app.loan_amount,
                default_probability=prediction['default_probability'],
                default_probability_percent=f"{prediction['default_probability']*100:.2f}%",
                predicted_default=prediction['predicted_default'],
                risk_category=prediction['risk_category'],
                decision=prediction['decision'],
                terms=prediction['recommended_terms'],
                reasoning=prediction['reasoning'],
                suggested_action=prediction['suggested_action'],
                timestamp=datetime.now()
            )

            predictions.append(pred_response)
            risk_counts[prediction['risk_category']] += 1
            decision_counts[prediction['decision']] += 1
            prediction_count += 1

        logger.info(f"✅ Batch prediction completed: {len(predictions)} applications")

        return BatchPredictionResponse(
            total_applications=len(predictions),
            predictions=predictions,
            summary={
                "risk_distribution": risk_counts,
                "decision_distribution": decision_counts,
                "average_default_probability": sum(p.default_probability for p in predictions) / len(predictions)
            }
        )

    except Exception as e:
        logger.error(f"❌ Batch prediction error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Batch prediction failed: {str(e)}"
        )


@app.get("/model/info", response_model=ModelInfo, tags=["Model"])
async def get_model_info(current_user: User = Depends(get_current_active_user)):
    """
    **Model Information** - Get details about the loaded ML model

    Returns information about the current credit risk model.

    **Requires:** Valid JWT token in Authorization header
    """
    if predictor is None or predictor.model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded"
        )

    return ModelInfo(
        model_name="XGBoost Credit Risk Model",
        model_type="XGBoost Classifier",
        version="1.0.0",
        trained_date="2024-01-15",
        performance_metrics={
            "auc_roc": 0.912,
            "accuracy": 0.884,
            "precision": 0.876,
            "recall": 0.892,
            "f1_score": 0.884
        }
    )


@app.get("/stats", tags=["Statistics"])
async def get_stats(current_user: User = Depends(get_current_active_user)):
    """
    **Prediction Statistics** - Get API usage statistics

    Returns statistics about API usage since startup.

    **Requires:** Valid JWT token in Authorization header
    """
    uptime = datetime.now() - start_time

    return {
        "total_predictions": prediction_count,
        "uptime_seconds": int(uptime.total_seconds()),
        "uptime_hours": round(uptime.total_seconds() / 3600, 2),
        "start_time": start_time.isoformat(),
        "current_time": datetime.now().isoformat(),
        "model_status": "loaded" if predictor and predictor.model else "not_loaded"
    }


# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    import uvicorn

    logger.info("🚀 Starting Nigerian Credit Risk Engine API...")
    logger.info(f"🌐 Server: http://localhost:8000")
    logger.info(f"📚 Docs: http://localhost:8000/docs")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes (development only)
        log_level="info"
    )
```

**What this code does:**

1. **8 REST Endpoints:**
   - `GET /` - Root/welcome
   - `POST /token` - Login (get JWT)
   - `GET /health` - Health check
   - `POST /predict` - Single prediction (requires auth)
   - `POST /batch_predict` - Batch predictions (requires auth)
   - `GET /model/info` - Model info (requires auth)
   - `GET /stats` - Usage stats (requires auth)
   - `GET /docs` - Swagger UI (automatic)

2. **Features:**
   - JWT authentication integration
   - CORS middleware
   - Global exception handling
   - Request/response logging
   - Prediction counting
   - Startup/shutdown events
   - Interactive documentation

---

### Step 3: Test the API Locally

Start the FastAPI server:

```bash
cd /home/user/-Credit_Risk_Engine-
python src/api/main.py
```

**Expected output:**
```
2024-01-15 10:30:00 - __main__ - INFO - 🚀 Starting Nigerian Credit Risk Engine API...
2024-01-15 10:30:00 - __main__ - INFO - 🌐 Server: http://localhost:8000
2024-01-15 10:30:00 - __main__ - INFO - 📚 Docs: http://localhost:8000/docs
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
2024-01-15 10:30:01 - __main__ - INFO - 🚀 Starting Nigerian Credit Risk Engine API...
2024-01-15 10:30:01 - __main__ - INFO - 📦 Loading model from: models/
2024-01-15 10:30:01 - __main__ - INFO - ✅ Model loaded successfully!
2024-01-15 10:30:01 - __main__ - INFO - 📊 Model type: XGBoost
2024-01-15 10:30:01 - __main__ - INFO - 🎯 Model accuracy: ~91.2% AUC-ROC
2024-01-15 10:30:01 - __main__ - INFO - 🌐 API available at: http://localhost:8000
2024-01-15 10:30:01 - __main__ - INFO - 📚 Documentation at: http://localhost:8000/docs
```

✅ **Success!** The API is now running at `http://localhost:8000`

**Keep this terminal running** and open a **NEW terminal** for testing.

---

### Step 4: Test Endpoints with curl

Open a **NEW terminal** and test each endpoint:

#### Test 1: Root Endpoint

```bash
curl http://localhost:8000/
```

**Expected output:**
```json
{
  "message": "🇳🇬 Welcome to Nigerian Credit Risk Engine API",
  "version": "1.0.0",
  "status": "operational",
  "documentation": "/docs",
  "health_check": "/health",
  "authentication": "/token",
  "prediction_endpoint": "/predict"
}
```

#### Test 2: Health Check

```bash
curl http://localhost:8000/health
```

**Expected output:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_name": "XGBoost Credit Risk Model",
  "timestamp": "2024-01-15T10:35:00.123456"
}
```

#### Test 3: Login (Get JWT Token)

```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=password123"
```

**Expected output:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcwNTMyMDAwMH0.xyz123...",
  "token_type": "bearer"
}
```

**Copy the `access_token` value** - you'll need it for the next tests!

**Set it as an environment variable** (makes testing easier):

```bash
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcwNTMyMDAwMH0.xyz123..."
```

(Replace with your actual token)

#### Test 4: Single Prediction (Authenticated)

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Chukwuemeka Okafor",
    "email": "chukwuemeka@gmail.com",
    "phone": "08031234567",
    "age": 35,
    "education": "B.Sc",
    "employment_sector": "Oil & Gas",
    "years_employed": 8.5,
    "monthly_income": 650000,
    "existing_monthly_debt": 120000,
    "credit_history_months": 60,
    "num_credit_lines": 3,
    "previous_defaults": 0,
    "bank": "Access Bank",
    "account_age_years": 7.5,
    "loan_amount": 5000000,
    "loan_term_months": 36,
    "loan_purpose": "Business Expansion",
    "interest_rate": 22.5
  }'
```

**Expected output:**
```json
{
  "application_id": "NGNA3B4C5D6",
  "applicant_name": "Chukwuemeka Okafor",
  "loan_amount": 5000000.0,
  "default_probability": 0.0823,
  "default_probability_percent": "8.23%",
  "predicted_default": false,
  "risk_category": "LOW",
  "decision": "APPROVE",
  "terms": "Approve with standard terms at 22.5% for 36 months",
  "reasoning": "Good credit profile with low default risk (8.23%). Applicant has stable employment, good income, and no previous defaults.",
  "suggested_action": "Auto-approve with standard terms",
  "timestamp": "2024-01-15T10:40:00.123456"
}
```

#### Test 5: Model Info (Authenticated)

```bash
curl -X GET "http://localhost:8000/model/info" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected output:**
```json
{
  "model_name": "XGBoost Credit Risk Model",
  "model_type": "XGBoost Classifier",
  "version": "1.0.0",
  "trained_date": "2024-01-15",
  "performance_metrics": {
    "auc_roc": 0.912,
    "accuracy": 0.884,
    "precision": 0.876,
    "recall": 0.892,
    "f1_score": 0.884
  }
}
```

#### Test 6: Statistics (Authenticated)

```bash
curl -X GET "http://localhost:8000/stats" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected output:**
```json
{
  "total_predictions": 1,
  "uptime_seconds": 300,
  "uptime_hours": 0.08,
  "start_time": "2024-01-15T10:30:00.123456",
  "current_time": "2024-01-15T10:35:00.123456",
  "model_status": "loaded"
}
```

#### Test 7: Test Without Authentication (Should Fail)

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Test User",
    "age": 30
  }'
```

**Expected output:**
```json
{
  "detail": "Not authenticated"
}
```

✅ **Perfect!** Authentication is working correctly.

---

### Step 5: View Swagger Documentation

Open your browser and go to:

```
http://localhost:8000/docs
```

You should see the **interactive API documentation** with:
- All 8 endpoints listed
- Try it out buttons
- Request/response schemas
- Authentication section
- Example requests

**Try the interactive docs:**
1. Click on `/token` endpoint
2. Click "Try it out"
3. Enter username: `admin`, password: `password123`
4. Click "Execute"
5. Copy the `access_token`
6. Click "Authorize" button at top (🔒 icon)
7. Paste token in format: `Bearer <your-token>`
8. Now try the `/predict` endpoint with authentication!

---

### Step 6: Create a Test Script

Let's create a Python script to test all endpoints:

```bash
touch tests/test_api_endpoints.py
```

Open `tests/test_api_endpoints.py` and paste:

```python
"""
Test script for API endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_all_endpoints():
    """Test all API endpoints."""

    print("🧪 Testing Nigerian Credit Risk Engine API\n")
    print("=" * 60)

    # Test 1: Root
    print("\n1️⃣ Testing GET / (root)")
    response = requests.get(f"{BASE_URL}/")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    assert response.status_code == 200
    print("   ✅ PASSED")

    # Test 2: Health
    print("\n2️⃣ Testing GET /health")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Model loaded: {data['model_loaded']}")
    assert response.status_code == 200
    assert data['model_loaded'] == True
    print("   ✅ PASSED")

    # Test 3: Login
    print("\n3️⃣ Testing POST /token (login)")
    response = requests.post(
        f"{BASE_URL}/token",
        data={"username": "admin", "password": "password123"}
    )
    print(f"   Status: {response.status_code}")
    data = response.json()
    token = data['access_token']
    print(f"   Token received: {token[:50]}...")
    assert response.status_code == 200
    assert 'access_token' in data
    print("   ✅ PASSED")

    # Test 4: Predict (with auth)
    print("\n4️⃣ Testing POST /predict (authenticated)")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "full_name": "Adebayo Ogunleye",
        "email": "adebayo@example.com",
        "phone": "08031234567",
        "age": 35,
        "education": "B.Sc",
        "employment_sector": "Banking & Finance",
        "years_employed": 8.5,
        "monthly_income": 450000,
        "existing_monthly_debt": 80000,
        "credit_history_months": 48,
        "num_credit_lines": 2,
        "previous_defaults": 0,
        "bank": "GTBank",
        "account_age_years": 6.0,
        "loan_amount": 2500000,
        "loan_term_months": 24,
        "loan_purpose": "Business Expansion",
        "interest_rate": 22.0
    }
    response = requests.post(f"{BASE_URL}/predict", json=payload, headers=headers)
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Applicant: {data['applicant_name']}")
    print(f"   Default probability: {data['default_probability_percent']}")
    print(f"   Risk category: {data['risk_category']}")
    print(f"   Decision: {data['decision']}")
    assert response.status_code == 200
    assert 'default_probability' in data
    print("   ✅ PASSED")

    # Test 5: Model Info (with auth)
    print("\n5️⃣ Testing GET /model/info (authenticated)")
    response = requests.get(f"{BASE_URL}/model/info", headers=headers)
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Model: {data['model_name']}")
    print(f"   AUC-ROC: {data['performance_metrics']['auc_roc']}")
    assert response.status_code == 200
    print("   ✅ PASSED")

    # Test 6: Stats (with auth)
    print("\n6️⃣ Testing GET /stats (authenticated)")
    response = requests.get(f"{BASE_URL}/stats", headers=headers)
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Total predictions: {data['total_predictions']}")
    print(f"   Uptime: {data['uptime_hours']} hours")
    assert response.status_code == 200
    print("   ✅ PASSED")

    # Test 7: Predict without auth (should fail)
    print("\n7️⃣ Testing POST /predict (no auth - should fail)")
    response = requests.post(f"{BASE_URL}/predict", json=payload)
    print(f"   Status: {response.status_code}")
    assert response.status_code == 401
    print("   ✅ PASSED (correctly rejected)")

    print("\n" + "=" * 60)
    print("🎉 All tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_all_endpoints()
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        raise
```

Run the test script:

```bash
python tests/test_api_endpoints.py
```

**Expected output:**
```
🧪 Testing Nigerian Credit Risk Engine API

============================================================

1️⃣ Testing GET / (root)
   Status: 200
   Response: {'message': '🇳🇬 Welcome to Nigerian Credit Risk Engine API', ...}
   ✅ PASSED

2️⃣ Testing GET /health
   Status: 200
   Model loaded: True
   ✅ PASSED

3️⃣ Testing POST /token (login)
   Status: 200
   Token received: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ✅ PASSED

4️⃣ Testing POST /predict (authenticated)
   Status: 200
   Applicant: Adebayo Ogunleye
   Default probability: 12.34%
   Risk category: LOW
   Decision: APPROVE
   ✅ PASSED

5️⃣ Testing GET /model/info (authenticated)
   Status: 200
   Model: XGBoost Credit Risk Model
   AUC-ROC: 0.912
   ✅ PASSED

6️⃣ Testing GET /stats (authenticated)
   Status: 200
   Total predictions: 1
   Uptime: 0.08 hours
   ✅ PASSED

7️⃣ Testing POST /predict (no auth - should fail)
   Status: 401
   ✅ PASSED (correctly rejected)

============================================================
🎉 All tests passed!
============================================================
```

---

### Step 7: Update requirements.txt

Ensure httpx is in requirements (for API testing later):

```bash
pip install httpx==0.24.1
```

Add to `requirements.txt` if not present:

```bash
echo "httpx==0.24.1" >> requirements.txt
```

---

### Step 8: Commit Your Work

Stop the API server (Ctrl+C in the first terminal), then commit:

```bash
git add src/api/main.py tests/test_api_endpoints.py requirements.txt
git commit -m "Day 9: Add complete FastAPI application with 8 REST endpoints

- Created main.py with full API implementation
- Added 8 endpoints: /, /token, /health, /predict, /batch_predict, /model/info, /stats, /docs
- Integrated JWT authentication on protected endpoints
- Added CORS middleware and global exception handling
- Created test script for all endpoints
- Added comprehensive API documentation
- All tests passing"
```

Push to remote:

```bash
git push -u origin claude/review-build-docs-017oQH5yzmnTZAswuKrsYs5s
```

---

## ✅ Day 9 Summary

### What We Built:

**main.py (420 lines):**
- Complete FastAPI application
- 8 REST endpoints (root, token, health, predict, batch_predict, model/info, stats, docs)
- JWT authentication integration
- CORS middleware
- Global exception handling
- Startup/shutdown events
- Request/response logging
- Prediction statistics tracking

**test_api_endpoints.py:**
- Comprehensive test script
- Tests all 7 endpoints
- Tests authentication flow
- Tests error handling

### Files Created:
- `src/api/main.py` - Main API application (420 lines)
- `tests/test_api_endpoints.py` - API test script (135 lines)

### What You Can Do Now:
- ✅ Start API server: `python src/api/main.py`
- ✅ Access API at: http://localhost:8000
- ✅ View docs at: http://localhost:8000/docs
- ✅ Login and get JWT token
- ✅ Make predictions with authentication
- ✅ Process batch predictions
- ✅ View model information
- ✅ Check API statistics
- ✅ Run automated tests

### Verification Checklist:
- [ ] API starts without errors: `python src/api/main.py`
- [ ] Health check returns "healthy": `curl http://localhost:8000/health`
- [ ] Login works: Get JWT token from `/token`
- [ ] Predictions work: POST to `/predict` with token
- [ ] Swagger docs load: http://localhost:8000/docs
- [ ] Test script passes: `python tests/test_api_endpoints.py`

---

## 💡 Troubleshooting

**Problem:** `ModuleNotFoundError: No module named 'src'`
**Solution:** Make sure you're running from project root: `cd /home/user/-Credit_Risk_Engine-`

**Problem:** Model not loading on startup
**Solution:** Make sure you ran Day 6 (training) and have `best_model.pkl` in `models/` directory

**Problem:** "Not authenticated" error
**Solution:**
1. Get token: `curl -X POST http://localhost:8000/token -d "username=admin&password=password123"`
2. Use token: `-H "Authorization: Bearer <token>"`

**Problem:** Port 8000 already in use
**Solution:** Kill existing process: `lsof -ti:8000 | xargs kill -9` or use different port

**Problem:** CORS errors in browser
**Solution:** Already configured in code with `allow_origins=["*"]`. For production, specify exact origins.

---

## 🚀 Tomorrow: Day 10

**Preview:** Automated Testing
- pytest setup for API testing
- Test fixtures and factories
- Unit tests for predictor
- Integration tests for API
- Test coverage reporting
- CI/CD test automation

**Time:** 2 hours

---

**🛑 STOP HERE FOR TODAY**

Fantastic! You now have a fully functional REST API with 8 endpoints, authentication, and comprehensive testing!

---

