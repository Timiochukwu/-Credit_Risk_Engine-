"""
Setup script for Nigerian Credit Risk Engine
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nigerian-credit-risk-engine",
    version="1.0.0",
    author="Credit Risk Team",
    author_email="team@creditrisk.ng",
    description="Enterprise-grade credit risk assessment for Nigerian financial institutions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/nigerian-credit-risk-engine",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "scikit-learn>=1.3.0",
        "xgboost>=2.0.0",
        "lightgbm>=4.0.0",
        "fastapi>=0.103.0",
        "uvicorn>=0.23.0",
        "streamlit>=1.26.0",
        "pydantic>=2.0.0",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "python-dotenv>=1.0.0",
        "mlflow>=2.6.0",
        "plotly>=5.16.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "flake8>=6.1.0",
            "mypy>=1.5.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "credit-risk-train=src.models.train:main",
            "credit-risk-api=src.api.main:main",
        ],
    },
)
