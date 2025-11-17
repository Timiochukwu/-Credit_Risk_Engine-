"""
Streamlit Dashboard - Nigerian Credit Risk Engine
==================================================

Interactive dashboard for monitoring and analyzing credit risk models.

Features:
- Real-time prediction interface
- Model performance visualization
- Risk analytics
- Batch processing
- Historical trends

Run with:
    streamlit run dashboard/streamlit_app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

try:
    from src.models.predict import CreditRiskPredictor
    from src.data.generate_data import NigerianLoanDataGenerator
    from src.utils.config import NIGERIAN_CITIES, EMPLOYMENT_SECTORS, EDUCATION_LEVELS, NIGERIAN_BANKS
    MODELS_AVAILABLE = True
except:
    MODELS_AVAILABLE = False
    st.warning("⚠️ Models not loaded. Some features may be unavailable.")

# Page config
st.set_page_config(
    page_title="Nigerian Credit Risk Engine",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'predictions' not in st.session_state:
    st.session_state.predictions = []

# Header
st.markdown('<div class="main-header">🏦 Nigerian Credit Risk Engine</div>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("Navigation")
    page = st.radio(
        "Select Page",
        ["🎯 Single Prediction", "📊 Batch Analysis", "📈 Model Performance", "ℹ️ About"]
    )

    st.markdown("---")
    st.markdown("### System Status")
    if MODELS_AVAILABLE:
        st.success("✓ Models Loaded")
    else:
        st.error("✗ Models Not Available")

    st.markdown("---")
    st.markdown("### Quick Stats")
    st.metric("Predictions Today", len(st.session_state.predictions))

# Page 1: Single Prediction
if page == "🎯 Single Prediction":
    st.header("Individual Loan Application Assessment")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Personal Information")
        full_name = st.text_input("Full Name", "Adebayo Ogunleye")
        age = st.number_input("Age", min_value=18, max_value=100, value=35)
        education = st.selectbox("Education Level", EDUCATION_LEVELS, index=3)

        st.subheader("Employment")
        employment_sector = st.selectbox("Employment Sector", EMPLOYMENT_SECTORS, index=1)
        years_employed = st.number_input("Years Employed", min_value=0.0, max_value=50.0, value=8.5, step=0.5)
        monthly_income = st.number_input(
            "Monthly Income (₦)",
            min_value=10000.0,
            max_value=10000000.0,
            value=450000.0,
            step=10000.0
        )

    with col2:
        st.subheader("Credit History")
        existing_monthly_debt = st.number_input(
            "Existing Monthly Debt (₦)",
            min_value=0.0,
            max_value=5000000.0,
            value=80000.0,
            step=10000.0
        )
        credit_history_months = st.number_input("Credit History (months)", min_value=0, max_value=600, value=48)
        num_credit_lines = st.number_input("Number of Credit Lines", min_value=0, max_value=10, value=2)
        previous_defaults = st.number_input("Previous Defaults", min_value=0, max_value=10, value=0)

        st.subheader("Banking Information")
        bank = st.selectbox("Bank", NIGERIAN_BANKS, index=1)
        account_age_years = st.number_input("Account Age (years)", min_value=0.0, max_value=50.0, value=6.0, step=0.5)

    st.subheader("Loan Details")
    col3, col4, col5 = st.columns(3)

    with col3:
        loan_amount = st.number_input(
            "Loan Amount (₦)",
            min_value=50000.0,
            max_value=100000000.0,
            value=2500000.0,
            step=100000.0
        )

    with col4:
        loan_term_months = st.number_input("Loan Term (months)", min_value=3, max_value=60, value=24)

    with col5:
        interest_rate = st.number_input("Interest Rate (%)", min_value=10.0, max_value=40.0, value=22.0, step=0.5)

    loan_purpose = st.text_input("Loan Purpose", "Business Expansion")

    if st.button("🔮 Predict Risk", type="primary"):
        if MODELS_AVAILABLE:
            try:
                # Create predictor
                predictor = CreditRiskPredictor(model_name="xgboost")

                # Create application dict
                application = {
                    "application_id": f"NGN{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "full_name": full_name,
                    "age": age,
                    "education": education,
                    "employment_sector": employment_sector,
                    "years_employed": years_employed,
                    "monthly_income": monthly_income,
                    "existing_monthly_debt": existing_monthly_debt,
                    "credit_history_months": credit_history_months,
                    "num_credit_lines": num_credit_lines,
                    "previous_defaults": previous_defaults,
                    "bank": bank,
                    "account_age_years": account_age_years,
                    "loan_amount": loan_amount,
                    "loan_term_months": loan_term_months,
                    "loan_purpose": loan_purpose,
                    "interest_rate": interest_rate,
                    "monthly_payment": loan_amount / loan_term_months  # Simplified
                }

                # Make prediction
                result = predictor.predict_single(application)

                # Store in session
                st.session_state.predictions.append(result)

                # Display results
                st.markdown("---")
                st.subheader("Risk Assessment Results")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Default Probability", result['default_probability_percent'])

                with col2:
                    risk_color = {
                        'VERY_LOW': '🟢',
                        'LOW': '🟡',
                        'MEDIUM': '🟠',
                        'HIGH': '🔴',
                        'VERY_HIGH': '⛔'
                    }
                    st.metric("Risk Category", f"{risk_color[result['risk_category']]} {result['risk_category']}")

                with col3:
                    st.metric("Decision", result['decision'])

                with col4:
                    st.metric("Application ID", result['application_id'])

                # Detailed analysis
                col1, col2 = st.columns(2)

                with col1:
                    st.info(f"**Reasoning:** {result['reasoning']}")

                with col2:
                    st.success(f"**Suggested Action:** {result['suggested_action']}")

                st.markdown(f"**Proposed Terms:** {result['terms']}")

            except FileNotFoundError:
                st.error("❌ Model files not found. Please train the model first:\n```python src/models/train.py```")
            except Exception as e:
                st.error(f"❌ Prediction error: {str(e)}")
        else:
            st.error("Models not available. Please check installation.")

# Page 2: Batch Analysis
elif page == "📊 Batch Analysis":
    st.header("Batch Loan Application Analysis")

    st.info("Generate and analyze multiple loan applications at once.")

    num_applications = st.slider("Number of Applications to Generate", 10, 500, 100)

    if st.button("Generate & Analyze Batch", type="primary"):
        if MODELS_AVAILABLE:
            with st.spinner(f"Generating {num_applications} applications..."):
                # Generate data
                generator = NigerianLoanDataGenerator(n_samples=num_applications)
                df = generator.generate()

                # Make predictions
                predictor = CreditRiskPredictor(model_name="xgboost")
                applications = df.to_dict('records')

                results_df = predictor.predict_batch(applications)

                # Display summary
                st.subheader("📊 Summary Statistics")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Total Applications", len(results_df))

                with col2:
                    avg_prob = results_df['default_probability'].mean()
                    st.metric("Avg Default Prob", f"{avg_prob:.1%}")

                with col3:
                    approval_rate = (results_df['decision'] == 'APPROVE').sum() / len(results_df)
                    st.metric("Approval Rate", f"{approval_rate:.1%}")

                with col4:
                    total_amount = results_df['loan_amount'].sum()
                    st.metric("Total Loan Amount", f"₦{total_amount:,.0f}")

                # Risk distribution
                st.subheader("Risk Distribution")
                risk_dist = results_df['risk_category'].value_counts()

                fig = px.pie(
                    values=risk_dist.values,
                    names=risk_dist.index,
                    title="Applications by Risk Category"
                )
                st.plotly_chart(fig, use_container_width=True)

                # Decision distribution
                col1, col2 = st.columns(2)

                with col1:
                    decision_dist = results_df['decision'].value_counts()
                    fig = px.bar(
                        x=decision_dist.index,
                        y=decision_dist.values,
                        title="Decision Distribution",
                        labels={'x': 'Decision', 'y': 'Count'}
                    )
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    # Probability distribution
                    fig = px.histogram(
                        results_df,
                        x='default_probability',
                        nbins=50,
                        title="Default Probability Distribution"
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # Data table
                st.subheader("Detailed Results")
                st.dataframe(results_df[['application_id', 'applicant_name', 'loan_amount',
                                        'default_probability_percent', 'risk_category', 'decision']])

# Page 3: Model Performance
elif page == "📈 Model Performance":
    st.header("Model Performance Dashboard")

    st.info("Monitor model performance and track key metrics over time.")

    # Simulated metrics
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    accuracy = np.random.uniform(0.85, 0.92, 30)
    auc = np.random.uniform(0.80, 0.90, 30)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Current Accuracy", f"{accuracy[-1]:.2%}", f"{(accuracy[-1] - accuracy[-2]):.2%}")

    with col2:
        st.metric("Current AUC-ROC", f"{auc[-1]:.2%}", f"{(auc[-1] - auc[-2]):.2%}")

    with col3:
        st.metric("Predictions This Month", len(st.session_state.predictions))

    # Performance over time
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=accuracy, name='Accuracy', mode='lines+markers'))
    fig.add_trace(go.Scatter(x=dates, y=auc, name='AUC-ROC', mode='lines+markers'))
    fig.update_layout(title='Model Performance Over Time', xaxis_title='Date', yaxis_title='Score')
    st.plotly_chart(fig, use_container_width=True)

# Page 4: About
else:
    st.header("About the Nigerian Credit Risk Engine")

    st.markdown("""
    ## Overview

    The Nigerian Credit Risk Engine is an enterprise-grade ML system for assessing loan default risk
    in the Nigerian banking context.

    ### Features

    - **ML Models**: XGBoost, LightGBM, Random Forest
    - **Nigerian Context**: Realistic data generation with Nigerian demographics, banks, sectors
    - **RESTful API**: FastAPI with JWT authentication
    - **Monitoring**: Real-time performance tracking and drift detection
    - **Scalable**: Docker-based deployment

    ### Risk Categories

    - **VERY_LOW** (< 5%): Auto-approve with best terms
    - **LOW** (5-15%): Auto-approve with standard terms
    - **MEDIUM** (15-30%): Approve with conditions
    - **HIGH** (30-50%): Manual review required
    - **VERY_HIGH** (> 50%): Reject

    ### Technology Stack

    - Python 3.8+
    - scikit-learn, XGBoost, LightGBM
    - FastAPI, Streamlit
    - PostgreSQL, MLflow
    - Docker, AWS

    ### Contact

    For more information or support, please contact the development team.
    """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>Nigerian Credit Risk Engine v1.0.0 | Powered by AI</div>",
    unsafe_allow_html=True
)
