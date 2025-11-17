"""
Configuration Module for Nigerian Credit Risk Engine
=====================================================

This module centralizes all configuration settings for the application.
It uses environment variables for sensitive data and provides defaults for development.

Nigerian Banking Context:
- Interest rates reflect CBN (Central Bank of Nigeria) policies
- Loan amounts are in Naira (NGN)
- Default rates consider Nigerian economic conditions
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================
# PROJECT PATHS
# ============================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SYNTHETIC_DATA_DIR = DATA_DIR / "synthetic"
MODELS_DIR = BASE_DIR / "models"

# Create directories if they don't exist
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, SYNTHETIC_DATA_DIR, MODELS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ============================================
# NIGERIAN BANKING PARAMETERS
# ============================================
# These reflect real Nigerian banking conditions

# Naira currency
CURRENCY = "NGN"

# Interest rates (Annual %) - Based on CBN rates
# Nigerian banks typically charge 15-30% for personal loans
INTEREST_RATE_MIN = 15.0
INTEREST_RATE_MAX = 30.0
INTEREST_RATE_MEAN = 22.0  # Average rate

# Loan amounts in Naira
# Microloans: ₦50,000 - ₦500,000
# SME loans: ₦500,000 - ₦50,000,000
# Corporate: ₦50M+
LOAN_AMOUNT_MIN = 50_000  # ₦50k
LOAN_AMOUNT_MAX = 100_000_000  # ₦100M

# Loan terms (months)
LOAN_TERM_MIN = 3
LOAN_TERM_MAX = 60  # 5 years

# Default rate (% of loans that default)
# Nigeria has higher default rates due to economic volatility
EXPECTED_DEFAULT_RATE = 0.12  # 12% (higher than developed markets)

# ============================================
# NIGERIAN DEMOGRAPHIC DATA
# ============================================
# Major Nigerian cities for address generation
NIGERIAN_CITIES = [
    "Lagos", "Kano", "Ibadan", "Abuja", "Port Harcourt",
    "Benin City", "Maiduguri", "Zaria", "Aba", "Jos",
    "Ilorin", "Oyo", "Enugu", "Kaduna", "Warri"
]

# Nigerian states
NIGERIAN_STATES = [
    "Lagos", "Kano", "Oyo", "FCT", "Rivers",
    "Edo", "Borno", "Kaduna", "Abia", "Plateau",
    "Kwara", "Enugu", "Delta", "Anambra", "Ogun"
]

# Common Nigerian banks
NIGERIAN_BANKS = [
    "Access Bank", "GTBank", "Zenith Bank", "First Bank",
    "UBA", "Fidelity Bank", "Union Bank", "Sterling Bank",
    "Stanbic IBTC", "Ecobank", "FCMB", "Wema Bank",
    "Polaris Bank", "Providus Bank", "Keystone Bank"
]

# Employment sectors in Nigeria
EMPLOYMENT_SECTORS = [
    "Oil & Gas", "Banking & Finance", "Telecommunications",
    "Manufacturing", "Retail", "Agriculture", "Construction",
    "Healthcare", "Education", "Government", "Technology",
    "Transportation", "Real Estate", "Hospitality"
]

# Education levels
EDUCATION_LEVELS = [
    "SSCE",  # Senior Secondary Certificate
    "OND",   # Ordinary National Diploma
    "HND",   # Higher National Diploma
    "B.Sc",  # Bachelor's degree
    "M.Sc",  # Master's degree
    "PhD"
]

# ============================================
# MODEL CONFIGURATION
# ============================================
# Random seed for reproducibility
RANDOM_SEED = 42

# Train/test split ratio
TEST_SIZE = 0.2
VALIDATION_SIZE = 0.1

# Class imbalance handling
# Since defaults are minority class (12%), we need to handle imbalance
IMBALANCE_STRATEGY = "smote"  # Synthetic Minority Over-sampling Technique

# Model hyperparameters (default values)
MODEL_PARAMS = {
    "xgboost": {
        "n_estimators": 200,
        "max_depth": 6,
        "learning_rate": 0.1,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "scale_pos_weight": 7.33,  # Ratio of negative to positive (88/12)
        "random_state": RANDOM_SEED
    },
    "lightgbm": {
        "n_estimators": 200,
        "max_depth": 6,
        "learning_rate": 0.1,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "is_unbalance": True,
        "random_state": RANDOM_SEED
    },
    "random_forest": {
        "n_estimators": 200,
        "max_depth": 10,
        "min_samples_split": 5,
        "min_samples_leaf": 2,
        "class_weight": "balanced",
        "random_state": RANDOM_SEED
    }
}

# Risk thresholds
# These determine loan approval decisions
RISK_THRESHOLDS = {
    "very_low": 0.05,   # < 5% default probability -> Auto-approve
    "low": 0.15,         # 5-15% -> Approve with standard terms
    "medium": 0.30,      # 15-30% -> Approve with higher interest
    "high": 0.50,        # 30-50% -> Manual review required
    "very_high": 1.0     # > 50% -> Auto-reject
}

# ============================================
# API CONFIGURATION
# ============================================
API_TITLE = "Nigerian Credit Risk Engine API"
API_VERSION = "1.0.0"
API_DESCRIPTION = "Enterprise-grade credit risk assessment for Nigerian financial institutions"

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# CORS (Cross-Origin Resource Sharing)
# In production, replace with actual frontend URLs
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8501").split(",")

# ============================================
# DATABASE CONFIGURATION
# ============================================
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "credit_risk_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# ============================================
# MLFLOW CONFIGURATION
# ============================================
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
MLFLOW_EXPERIMENT_NAME = "nigerian-credit-risk"

# ============================================
# MONITORING CONFIGURATION
# ============================================
# Model performance monitoring thresholds
MONITORING_THRESHOLDS = {
    "min_accuracy": 0.85,      # Alert if accuracy drops below 85%
    "min_auc_roc": 0.80,        # Alert if AUC-ROC drops below 80%
    "max_false_positive_rate": 0.15,  # Alert if FPR exceeds 15%
    "max_false_negative_rate": 0.20,  # Alert if FNR exceeds 20%
}

# Data drift detection
DATA_DRIFT_THRESHOLD = 0.1  # Alert if feature distribution changes by more than 10%

# ============================================
# LOGGING CONFIGURATION
# ============================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ============================================
# FEATURE ENGINEERING PARAMETERS
# ============================================
# These will be used to create derived features

# Debt-to-Income ratio thresholds (Nigerian context)
# Nigerian banks typically require DTI < 40%
DTI_THRESHOLD = 0.40

# Credit utilization thresholds
CREDIT_UTILIZATION_THRESHOLD = 0.70  # 70%

# Minimum income for loan eligibility (in Naira)
MINIMUM_INCOME = 30_000  # ₦30k/month (roughly $65)

# Age-related parameters
MINIMUM_AGE = 18
MAXIMUM_AGE = 65
PRIME_WORKING_AGE_START = 25
PRIME_WORKING_AGE_END = 55

# ============================================
# DATA GENERATION PARAMETERS
# ============================================
# For synthetic Nigerian loan data
DEFAULT_SAMPLE_SIZE = 10_000
OUTLIER_PERCENTAGE = 0.05  # 5% of data will be outliers

print(f"✓ Configuration loaded successfully")
print(f"✓ Base directory: {BASE_DIR}")
print(f"✓ Data directory: {DATA_DIR}")
print(f"✓ Currency: {CURRENCY}")
print(f"✓ Expected default rate: {EXPECTED_DEFAULT_RATE * 100}%")
