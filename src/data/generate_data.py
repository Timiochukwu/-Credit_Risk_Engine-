"""
Nigerian Loan Data Generator
=============================

This module generates synthetic but realistic loan application data for Nigerian banks.

Key Features:
- Realistic Nigerian names, addresses, and phone numbers
- Loan amounts and terms matching Nigerian banking practices
- Correlated features (e.g., higher income → better credit history)
- Class imbalance reflecting real default rates (~12%)
- Nigerian-specific sectors and demographics

The data includes:
1. Applicant demographics (age, education, employment)
2. Financial information (income, existing debt, credit history)
3. Loan details (amount, term, purpose)
4. Target variable (default/no default)
"""

import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
from typing import Dict, List, Tuple
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import (
    NIGERIAN_CITIES, NIGERIAN_STATES, NIGERIAN_BANKS, EMPLOYMENT_SECTORS,
    EDUCATION_LEVELS, LOAN_AMOUNT_MIN, LOAN_AMOUNT_MAX, LOAN_TERM_MIN,
    LOAN_TERM_MAX, INTEREST_RATE_MIN, INTEREST_RATE_MAX, EXPECTED_DEFAULT_RATE,
    RANDOM_SEED, SYNTHETIC_DATA_DIR, CURRENCY
)

# Set random seeds for reproducibility
np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

# Initialize Faker with Nigerian locale
fake = Faker(['en_US'])  # No direct Nigerian locale, but we'll customize
Faker.seed(RANDOM_SEED)


class NigerianLoanDataGenerator:
    """
    Generates realistic Nigerian loan application data.

    The generator creates correlated features to simulate real-world patterns:
    - Higher education → Higher income
    - Higher income → Lower default probability
    - Longer employment → Better credit history
    - Higher debt-to-income ratio → Higher default probability
    """

    def __init__(self, n_samples: int = 10000, default_rate: float = EXPECTED_DEFAULT_RATE):
        """
        Initialize the data generator.

        Args:
            n_samples: Number of loan applications to generate
            default_rate: Expected proportion of defaults (0.12 = 12%)
        """
        self.n_samples = n_samples
        self.default_rate = default_rate
        self.data = None

    def _generate_nigerian_name(self) -> Dict[str, str]:
        """
        Generate realistic Nigerian names from major ethnic groups.

        Returns:
            Dict with first_name and last_name
        """
        # Common Nigerian first names
        yoruba_names = ["Adebayo", "Oluwaseun", "Temitope", "Ayodeji", "Oluwatoyin",
                       "Babatunde", "Oluwakemi", "Adeyemi", "Funmilayo", "Olamide"]
        igbo_names = ["Chukwuemeka", "Ifeoma", "Ngozi", "Chidinma", "Obinna",
                     "Chinonso", "Chiamaka", "Ikechukwu", "Amarachi", "Chinedu"]
        hausa_names = ["Ibrahim", "Fatima", "Musa", "Aisha", "Yusuf",
                      "Hauwa", "Abdullahi", "Zainab", "Ahmad", "Halima"]

        # Common Nigerian surnames
        yoruba_surnames = ["Adewale", "Ogunleye", "Adeleke", "Okafor", "Ayodele",
                          "Babangida", "Fashola", "Tinubu", "Abiola", "Obasanjo"]
        igbo_surnames = ["Okonkwo", "Nwankwo", "Okafor", "Ezeh", "Okeke",
                        "Anyanwu", "Eze", "Chukwu", "Nwosu", "Igwe"]
        hausa_surnames = ["Buhari", "Shehu", "Abubakar", "Bello", "Aliyu",
                         "Sani", "Garba", "Usman", "Mohammed", "Hassan"]

        # Randomly choose ethnic group
        ethnic_choice = random.choice(['yoruba', 'igbo', 'hausa'])

        if ethnic_choice == 'yoruba':
            first_name = random.choice(yoruba_names)
            last_name = random.choice(yoruba_surnames)
        elif ethnic_choice == 'igbo':
            first_name = random.choice(igbo_names)
            last_name = random.choice(igbo_surnames)
        else:
            first_name = random.choice(hausa_names)
            last_name = random.choice(hausa_surnames)

        return {
            "first_name": first_name,
            "last_name": last_name,
            "full_name": f"{first_name} {last_name}"
        }

    def _generate_nigerian_phone(self) -> str:
        """
        Generate realistic Nigerian phone number.

        Nigerian format: +234 XXX XXX XXXX
        Common prefixes: 0803, 0805, 0806, 0807, 0809, 0810, 0813, 0814, etc.
        """
        prefixes = ['0803', '0805', '0806', '0807', '0809', '0810', '0813',
                   '0814', '0815', '0816', '0817', '0818', '0901', '0902', '0903']
        prefix = random.choice(prefixes)
        suffix = ''.join([str(random.randint(0, 9)) for _ in range(7)])
        return f"{prefix}{suffix}"

    def _generate_email(self, name: str) -> str:
        """Generate email address based on name."""
        domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com']
        # Clean name and make lowercase
        clean_name = name.lower().replace(' ', '.')
        domain = random.choice(domains)
        # Add random numbers sometimes
        if random.random() > 0.5:
            clean_name += str(random.randint(1, 999))
        return f"{clean_name}@{domain}"

    def _generate_address(self) -> Dict[str, str]:
        """Generate Nigerian address."""
        city = random.choice(NIGERIAN_CITIES)
        state_idx = NIGERIAN_CITIES.index(city)
        state = NIGERIAN_STATES[state_idx] if state_idx < len(NIGERIAN_STATES) else random.choice(NIGERIAN_STATES)

        # Nigerian address format
        street_number = random.randint(1, 300)
        street_names = ["Allen Avenue", "Admiralty Way", "Victoria Island", "Lekki Road",
                       "Awolowo Road", "Broad Street", "Marina Road", "Independence Avenue",
                       "Herbert Macaulay Way", "Ahmadu Bello Way"]
        street = random.choice(street_names)

        return {
            "address": f"{street_number} {street}",
            "city": city,
            "state": state
        }

    def _calculate_education_score(self, education: str) -> float:
        """Convert education level to numeric score (0-1)."""
        education_scores = {
            "SSCE": 0.3,
            "OND": 0.5,
            "HND": 0.65,
            "B.Sc": 0.8,
            "M.Sc": 0.9,
            "PhD": 1.0
        }
        return education_scores.get(education, 0.5)

    def generate(self) -> pd.DataFrame:
        """
        Generate complete dataset with all features.

        Returns:
            DataFrame with loan application data
        """
        print(f"\n{'='*60}")
        print(f"Generating {self.n_samples:,} Nigerian Loan Applications")
        print(f"{'='*60}\n")

        data = []

        for i in range(self.n_samples):
            if (i + 1) % 1000 == 0:
                print(f"  Generated {i + 1:,} / {self.n_samples:,} applications...")

            # Basic Information
            name_data = self._generate_nigerian_name()
            address_data = self._generate_address()

            # Demographics
            # Age: Normal distribution, mean 35, std 10, range 22-65
            age = int(np.clip(np.random.normal(35, 10), 22, 65))

            # Education: Weighted towards B.Sc and HND
            education = np.random.choice(
                EDUCATION_LEVELS,
                p=[0.15, 0.15, 0.25, 0.30, 0.10, 0.05]  # Weights for each level
            )
            education_score = self._calculate_education_score(education)

            # Employment
            employment_sector = random.choice(EMPLOYMENT_SECTORS)

            # Years employed (correlated with age)
            # Younger people have fewer years employed
            max_years = age - 22  # Assuming started working at 22
            years_employed = np.clip(np.random.exponential(scale=5), 0, max_years)

            # Income (monthly, in Naira)
            # Correlated with education and years employed
            # Nigerian salary ranges: ₦30k - ₦5M per month
            base_income = 50_000  # Base salary
            education_multiplier = 1 + (education_score * 5)  # Up to 6x
            experience_multiplier = 1 + (years_employed * 0.05)  # 5% per year
            sector_multiplier = np.random.uniform(0.8, 1.5)  # Sector variation

            monthly_income = base_income * education_multiplier * experience_multiplier * sector_multiplier
            monthly_income = int(np.clip(monthly_income, 30_000, 5_000_000))

            # Existing monthly debt obligations
            # People with higher income tend to have more debt (mortgages, car loans)
            # But debt-to-income ratio should be realistic
            avg_dti = np.random.beta(2, 5)  # Skewed towards lower DTI
            existing_debt = int(monthly_income * avg_dti)

            # Credit history (months) - how long they've had credit
            # Correlated with age and years employed
            max_credit_history = min(age - 18, years_employed * 12) * 12  # Convert to months
            credit_history_months = int(np.clip(
                np.random.exponential(scale=36),  # Mean of 36 months
                0,
                max_credit_history
            ))

            # Number of existing credit lines
            # More common for higher income individuals
            if monthly_income < 100_000:
                num_credit_lines = np.random.choice([0, 1, 2], p=[0.4, 0.4, 0.2])
            elif monthly_income < 500_000:
                num_credit_lines = np.random.choice([1, 2, 3], p=[0.3, 0.5, 0.2])
            else:
                num_credit_lines = np.random.choice([2, 3, 4, 5], p=[0.2, 0.4, 0.3, 0.1])

            # Previous defaults (binary: 0 or 1)
            # Lower probability for higher income/education
            default_prob_factor = max(0.01, 1 - (education_score * 0.5 + (monthly_income / 5_000_000) * 0.5))
            previous_defaults = np.random.choice([0, 1], p=[1 - default_prob_factor * 0.15, default_prob_factor * 0.15])

            # Bank relationship
            bank = random.choice(NIGERIAN_BANKS)
            account_age_years = np.clip(np.random.exponential(scale=3), 0.5, age - 18)

            # Loan Details
            # Loan amount - correlated with income
            # Rule of thumb: loan shouldn't exceed 6 months of income
            max_loan = monthly_income * 6
            loan_amount = int(np.random.uniform(
                LOAN_AMOUNT_MIN,
                min(max_loan, LOAN_AMOUNT_MAX)
            ))

            # Loan term (months)
            # Larger loans typically have longer terms
            if loan_amount < 500_000:
                loan_term = random.randint(3, 12)
            elif loan_amount < 2_000_000:
                loan_term = random.randint(6, 24)
            else:
                loan_term = random.randint(12, 60)

            # Loan purpose
            loan_purposes = [
                "Business Expansion", "Working Capital", "Equipment Purchase",
                "Education", "Medical Emergency", "Debt Consolidation",
                "Home Renovation", "Agriculture", "Inventory", "Vehicle Purchase"
            ]
            loan_purpose = random.choice(loan_purposes)

            # Interest rate (offered by bank)
            # Higher risk customers get higher rates
            base_rate = INTEREST_RATE_MEAN
            risk_adjustment = (previous_defaults * 5) - (education_score * 3)
            interest_rate = np.clip(
                base_rate + risk_adjustment + np.random.uniform(-2, 2),
                INTEREST_RATE_MIN,
                INTEREST_RATE_MAX
            )

            # Calculate monthly payment
            monthly_rate = interest_rate / 100 / 12
            if monthly_rate > 0:
                monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**loan_term) / \
                                ((1 + monthly_rate)**loan_term - 1)
            else:
                monthly_payment = loan_amount / loan_term

            # Total debt after new loan
            total_monthly_debt = existing_debt + monthly_payment
            debt_to_income = total_monthly_debt / monthly_income if monthly_income > 0 else 1

            # Target Variable: DEFAULT
            # Calculate default probability based on multiple factors
            default_prob = 0.1  # Base probability

            # Adjust based on features (logistic relationship)
            # Negative factors (increase default risk)
            if debt_to_income > 0.4:
                default_prob += (debt_to_income - 0.4) * 0.5
            if previous_defaults > 0:
                default_prob += 0.3
            if credit_history_months < 12:
                default_prob += 0.15
            if years_employed < 2:
                default_prob += 0.1
            if age < 25:
                default_prob += 0.05

            # Positive factors (decrease default risk)
            if education_score > 0.7:
                default_prob -= 0.1
            if monthly_income > 500_000:
                default_prob -= 0.1
            if account_age_years > 5:
                default_prob -= 0.05
            if num_credit_lines >= 2 and previous_defaults == 0:
                default_prob -= 0.05

            # Clip probability to valid range
            default_prob = np.clip(default_prob, 0, 1)

            # Generate default outcome
            defaulted = np.random.random() < default_prob

            # Create record
            record = {
                # Personal Information
                "application_id": f"NGN{i+1:06d}",
                "first_name": name_data["first_name"],
                "last_name": name_data["last_name"],
                "full_name": name_data["full_name"],
                "email": self._generate_email(name_data["full_name"]),
                "phone": self._generate_nigerian_phone(),
                "address": address_data["address"],
                "city": address_data["city"],
                "state": address_data["state"],

                # Demographics
                "age": age,
                "education": education,
                "employment_sector": employment_sector,
                "years_employed": round(years_employed, 1),

                # Financial Information
                "monthly_income": monthly_income,
                "existing_monthly_debt": existing_debt,
                "credit_history_months": credit_history_months,
                "num_credit_lines": num_credit_lines,
                "previous_defaults": previous_defaults,

                # Banking Information
                "bank": bank,
                "account_age_years": round(account_age_years, 1),

                # Loan Information
                "loan_amount": loan_amount,
                "loan_term_months": loan_term,
                "loan_purpose": loan_purpose,
                "interest_rate": round(interest_rate, 2),
                "monthly_payment": round(monthly_payment, 2),

                # Derived Features
                "debt_to_income_ratio": round(debt_to_income, 3),
                "loan_to_income_ratio": round(loan_amount / (monthly_income * 12), 3),

                # Target Variable
                "defaulted": int(defaulted),

                # Metadata
                "application_date": fake.date_between(start_date='-2y', end_date='today').strftime('%Y-%m-%d'),
                "currency": CURRENCY
            }

            data.append(record)

        # Convert to DataFrame
        self.data = pd.DataFrame(data)

        # Print summary statistics
        print(f"\n{'='*60}")
        print(f"Data Generation Complete!")
        print(f"{'='*60}")
        print(f"\nDataset Statistics:")
        print(f"  Total Applications: {len(self.data):,}")
        print(f"  Defaults: {self.data['defaulted'].sum():,} ({self.data['defaulted'].mean()*100:.1f}%)")
        print(f"  Non-Defaults: {(~self.data['defaulted'].astype(bool)).sum():,} ({(~self.data['defaulted'].astype(bool)).mean()*100:.1f}%)")
        print(f"\nLoan Amount Range: ₦{self.data['loan_amount'].min():,.0f} - ₦{self.data['loan_amount'].max():,.0f}")
        print(f"Average Loan Amount: ₦{self.data['loan_amount'].mean():,.0f}")
        print(f"\nIncome Range: ₦{self.data['monthly_income'].min():,.0f} - ₦{self.data['monthly_income'].max():,.0f}")
        print(f"Average Income: ₦{self.data['monthly_income'].mean():,.0f}")
        print(f"\nAverage Debt-to-Income Ratio: {self.data['debt_to_income_ratio'].mean():.2%}")

        return self.data

    def save(self, filename: str = "nigerian_loan_data.csv") -> str:
        """
        Save generated data to CSV file.

        Args:
            filename: Name of output file

        Returns:
            Path to saved file
        """
        if self.data is None:
            raise ValueError("No data to save. Run generate() first.")

        output_path = SYNTHETIC_DATA_DIR / filename
        self.data.to_csv(output_path, index=False)
        print(f"\n✓ Data saved to: {output_path}")
        return str(output_path)


def main():
    """Main function to generate and save Nigerian loan data."""
    print("\n" + "="*60)
    print("NIGERIAN CREDIT RISK DATA GENERATOR")
    print("="*60)

    # Generate data
    generator = NigerianLoanDataGenerator(n_samples=10000)
    data = generator.generate()

    # Save data
    output_file = generator.save()

    print(f"\n✓ Dataset ready for model training!")
    print(f"✓ File: {output_file}")
    print(f"✓ Shape: {data.shape}")
    print(f"\n{'='*60}\n")

    return data


if __name__ == "__main__":
    main()
