# 🔒 Security Fixes Implementation Guide

**Nigerian Credit Risk Engine - Comprehensive Security Remediation**

---

## 📊 Implementation Status

### ✅ Phase 1: COMPLETED (Configuration Layer)
- [x] **Issue #1:** Hardcoded SECRET_KEY - FIXED ✅
- [x] **Issue #2:** Hardcoded DB_PASSWORD - FIXED ✅
- [x] **Issue #7:** CORS Configuration - FIXED ✅
- [x] Security configuration added
- [x] Requirements.txt updated with security dependencies
- [x] Comprehensive .env.example created

**Commit:** `e5b9f7c` - "security: Add critical security configuration and validation (Phase 1)"

---

## 🚧 Phase 2: IN PROGRESS (Implementation Layer)

### Critical Issues Remaining

#### 🔴 Issue #3: Database Implementation (CRITICAL)
**Status:** Pending
**File:** Create `src/database/`
**Priority:** HIGH

**What's Needed:**
1. Create SQLAlchemy models
2. Implement database session management
3. Add Alembic migrations
4. Replace in-memory data with database queries

**Implementation Steps:**

```python
# src/database/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

class LoanApplication(Base):
    __tablename__ = "loan_applications"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(String, unique=True, nullable=False, index=True)
    applicant_name = Column(String, nullable=False)
    bvn = Column(String(11), nullable=False)
    monthly_income = Column(Float, nullable=False)
    loan_amount = Column(Float, nullable=False)
    loan_term_months = Column(Integer, nullable=False)
    status = Column(String, default="pending")  # pending, approved, rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(String, nullable=False, index=True)
    default_probability = Column(Float, nullable=False)
    risk_category = Column(String, nullable=False)
    decision = Column(String, nullable=False)
    model_version = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

# src/database/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from src.utils.config import DATABASE_URL, DB_POOL_SIZE, DB_MAX_OVERFLOW

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_MAX_OVERFLOW,
    pool_pre_ping=True,
    pool_recycle=3600
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency for FastAPI endpoints."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

#### 🔴 Issue #4: JWT in localStorage (HIGH)
**Status:** Pending
**File:** `src/api/auth.py`, `frontend/src/services/api.ts`
**Priority:** HIGH

**What's Needed:**
1. Change JWT from response body to httpOnly cookie
2. Update frontend to handle cookie-based auth
3. Add CSRF protection

**Backend Implementation:**

```python
# src/api/auth.py - Update login endpoint
from fastapi import Response
from src.utils.config import SESSION_COOKIE_SECURE, SESSION_COOKIE_HTTPONLY

@app.post("/token")
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": user.username})

    # Set httpOnly cookie instead of returning token
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=SESSION_COOKIE_HTTPONLY,
        secure=SESSION_COOKIE_SECURE,
        samesite="lax",
        max_age=1800  # 30 minutes
    )

    return {"message": "Login successful", "username": user.username}
```

**Frontend Implementation:**

```typescript
// frontend/src/services/api.ts
// Remove localStorage usage
class ApiClient {
  async login(username: string, password: string) {
    const response = await axios.post('/token',
      { username, password },
      { withCredentials: true }  // Enable cookies
    );
    // Token now in httpOnly cookie, not localStorage
    return response.data;
  }

  async makeRequest(url: string, data: any) {
    return axios.post(url, data, {
      withCredentials: true  // Send cookies with request
    });
  }
}
```

---

#### 🔴 Issue #5: Rate Limiting (HIGH)
**Status:** Pending
**File:** `src/api/main.py`
**Priority:** HIGH

**What's Needed:**
1. Add slowapi middleware
2. Configure rate limits per endpoint
3. Add Redis for distributed rate limiting

**Implementation:**

```python
# src/api/main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from src.utils.config import (
    RATE_LIMIT_ENABLED,
    RATE_LIMIT_LOGIN,
    RATE_LIMIT_PREDICTION,
    RATE_LIMIT_GENERAL,
    RATE_LIMIT_STORAGE_URL
)

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=RATE_LIMIT_STORAGE_URL,
    enabled=RATE_LIMIT_ENABLED
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Apply rate limits to endpoints
@app.post("/token")
@limiter.limit(RATE_LIMIT_LOGIN)
async def login(request: Request, ...):
    # ... existing code
    pass

@app.post("/predict")
@limiter.limit(RATE_LIMIT_PREDICTION)
async def predict_single(request: Request, ...):
    # ... existing code
    pass

@app.get("/health")
@limiter.limit(RATE_LIMIT_GENERAL)
async def health_check(request: Request):
    # ... existing code
    pass
```

---

#### 🔴 Issue #6: Fake User Database (HIGH)
**Status:** Pending (blocked by Issue #3)
**File:** `src/api/auth.py`
**Priority:** HIGH

**What's Needed:**
1. Remove fake_users_db
2. Implement database-backed user authentication
3. Add user registration endpoint
4. Add password policies

**Implementation:**

```python
# src/api/auth.py - Replace fake_users_db
from src.database.models import User
from src.database.session import get_db
from sqlalchemy.orm import Session

def get_user(db: Session, username: str) -> Optional[User]:
    """Get user from database."""
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    """Authenticate user against database."""
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

@app.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect credentials")
    # ... rest of login logic
```

---

#### 🟡 Issue #7: Input Validation (MEDIUM)
**Status:** Pending
**File:** `src/api/schemas.py`
**Priority:** HIGH

**What's Needed:**
1. Add BVN validation
2. Add business rule validators
3. Add loan amount limits
4. Add interest rate validation

**Implementation:**

```python
# src/api/schemas.py - Enhanced validation
from pydantic import BaseModel, Field, validator
from typing import Optional

class LoanApplicationRequest(BaseModel):
    # Required BVN
    bvn: str = Field(
        ...,
        min_length=11,
        max_length=11,
        description="Bank Verification Number (11 digits, mandatory)"
    )

    # Age validation
    age: int = Field(
        ...,
        ge=18,
        le=65,
        description="Age must be between 18-65"
    )

    # Loan amount with limits
    loan_amount: float = Field(
        ...,
        gt=50_000,  # Min ₦50k
        le=100_000_000,  # Max ₦100M
        description="Loan amount in Naira"
    )

    # Monthly income validation
    monthly_income: float = Field(
        ...,
        ge=30_000,  # Nigerian minimum wage
        description="Monthly income in Naira"
    )

    # Interest rate with CBN limits
    interest_rate: float = Field(
        ...,
        gt=0,
        le=30,  # CBN maximum
        description="Annual interest rate (%)"
    )

    # BVN format validator
    @validator('bvn')
    def validate_bvn_format(cls, v):
        if not v.isdigit():
            raise ValueError('BVN must contain only digits')
        if len(v) != 11:
            raise ValueError('BVN must be exactly 11 digits')
        return v

    # Loan-to-income ratio validator
    @validator('loan_amount')
    def validate_loan_to_income(cls, v, values):
        if 'monthly_income' in values:
            annual_income = values['monthly_income'] * 12
            if v > annual_income * 6:  # Max 6x annual income
                raise ValueError(
                    f'Loan amount (₦{v:,.0f}) exceeds 6x annual income '
                    f'(₦{annual_income * 6:,.0f})'
                )
        return v

    # Debt-to-income validator
    @validator('existing_monthly_debt')
    def validate_dti(cls, v, values):
        if 'monthly_income' in values:
            dti = v / values['monthly_income']
            if dti > 0.40:  # CBN maximum 40%
                raise ValueError(
                    f'Debt-to-income ratio ({dti:.1%}) exceeds CBN limit of 40%'
                )
        return v

    class Config:
        schema_extra = {
            "example": {
                "bvn": "12345678901",
                "full_name": "Adebayo Ogunleye",
                "age": 35,
                "monthly_income": 450000,
                "loan_amount": 2500000,
                # ... other fields
            }
        }
```

---

## 📊 Phase 2 Summary

### ✅ Completed
1. Enhanced configuration with production validation
2. Added security dependencies to requirements.txt
3. Created comprehensive .env.example
4. Environment-aware security warnings

### 🚧 In Progress
- Database layer implementation
- Rate limiting implementation
- Input validation enhancements

### ⏳ Pending
- JWT cookie migration
- Sentry integration
- Prometheus metrics
- Structured logging
- User authentication refactor

---

## 🔧 Quick Implementation Commands

### Install New Dependencies
```bash
pip install -r requirements.txt
```

### Create Database Tables
```bash
# After implementing models
alembic init alembic
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

### Run with Security Validations
```bash
# Development (warnings only)
API_ENV=development uvicorn src.api.main:app --reload

# Production (strict validation)
API_ENV=production \
SECRET_KEY=$(openssl rand -hex 32) \
DB_PASSWORD=$(openssl rand -base64 24) \
ALLOWED_ORIGINS=https://app.example.com \
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

### Generate Secure Keys
```bash
# SECRET_KEY (64 characters)
openssl rand -hex 32

# DB_PASSWORD (24+ characters)
openssl rand -base64 24

# API keys (32+ characters)
openssl rand -base64 32
```

---

## 📈 Implementation Timeline

| Phase | Tasks | Estimated Time | Priority |
|-------|-------|----------------|----------|
| **Phase 1** ✅ | Configuration | 2 hours | CRITICAL |
| **Phase 2** 🚧 | Database + Auth | 8 hours | CRITICAL |
| **Phase 3** ⏳ | Rate Limiting + Validation | 4 hours | HIGH |
| **Phase 4** ⏳ | Monitoring + Logging | 4 hours | HIGH |
| **Phase 5** ⏳ | Testing | 6 hours | HIGH |

**Total Estimated Time:** ~24 hours (3 days)

---

## 🎯 Success Criteria

Before deploying to production:

- [ ] All CRITICAL issues resolved
- [ ] All HIGH priority issues resolved
- [ ] Database implemented with proper ORM
- [ ] Rate limiting active on all endpoints
- [ ] JWT in httpOnly cookies (not localStorage)
- [ ] Input validation with business rules
- [ ] Sentry configured for error tracking
- [ ] Prometheus metrics exposed
- [ ] 200+ tests written and passing
- [ ] Security audit performed
- [ ] Penetration testing completed

---

## 📞 Next Steps

1. **Continue Implementation:**
   ```bash
   # Create database layer
   mkdir -p src/database
   touch src/database/__init__.py
   touch src/database/models.py
   touch src/database/session.py
   ```

2. **Test Configurations:**
   ```bash
   # Test production validation
   API_ENV=production python -c "from src.utils.config import SECRET_KEY"
   # Should raise ValueError if SECRET_KEY not set
   ```

3. **Review Code:**
   ```bash
   # Run linting
   flake8 src/
   black src/
   mypy src/
   ```

---

**Last Updated:** 2025-11-20
**Phase 1 Commit:** e5b9f7c
**Status:** Phase 1 Complete ✅ | Phase 2 In Progress 🚧
