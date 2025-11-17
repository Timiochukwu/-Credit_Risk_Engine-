/**
 * TypeScript type definitions for Nigerian Credit Risk Engine
 */

export interface LoanApplication {
  applicationId?: string;
  bvn: string;
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  dateOfBirth: string;
  gender: string;
  maritalStatus: string;
  education: string;
  employmentStatus: string;
  employmentSector: string;
  monthlyIncome: number;
  loanAmount: number;
  loanPurpose: string;
  tenureMonths: number;
  hasExistingLoans: boolean;
  existingLoanAmount?: number;
  creditScore?: number;
  address: string;
  city: string;
  state: string;
}

export interface PredictionResult {
  applicationId: string;
  defaultProbability: number;
  defaultProbabilityPercent: number;
  riskCategory: 'VERY_LOW' | 'LOW' | 'MEDIUM' | 'HIGH' | 'VERY_HIGH';
  decision: 'APPROVE' | 'REJECT' | 'REVIEW';
  approvedAmount?: number;
  interestRate?: number;
  monthlyPayment?: number;
  explanation?: string;
  timestamp: string;
}

export interface User {
  username: string;
  email: string;
  fullName: string;
  role: string;
}

export interface AuthTokens {
  accessToken: string;
  tokenType: string;
}

export interface DashboardMetrics {
  totalApplications: number;
  approvalRate: number;
  averageRiskScore: number;
  portfolioValue: number;
  nplRatio: number;
}

export interface PortfolioRisk {
  totalLoans: number;
  totalOutstanding: number;
  expectedLoss: number;
  concentration: {
    sector: Record<string, number>;
    geography: Record<string, number>;
  };
}

export interface FXRisk {
  fxRiskScore: number;
  riskLevel: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  currencyMismatch: boolean;
  devaluationImpact?: {
    scenario: string;
    paymentIncrease: number;
    newDTI: number;
  };
}
