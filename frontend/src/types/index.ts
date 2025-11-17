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
  loanCurrency?: string;
  incomeCurrency?: string;
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
  access_token: string;
  token_type: string;
}

export interface DashboardMetrics {
  totalApplications: number;
  approvalRate: number;
  averageRiskScore: number;
  portfolioValue: number;
  nplRatio: number;
  applicationsToday?: number;
  pendingReview?: number;
  avgProcessingTime?: number;
}

export interface PortfolioRisk {
  totalLoans: number;
  totalOutstanding: number;
  expectedLoss: number;
  nplAmount?: number;
  concentration: {
    sector: Record<string, number>;
    geography: Record<string, number>;
  };
}

export interface FXRiskAssessment {
  fxRiskScore: number;
  riskLevel: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  currencyMismatch: boolean;
  exchangeRate: {
    official: number;
    parallel: number;
    premium: number;
  };
  devaluationImpact?: {
    scenario: string;
    paymentIncrease: number;
    newDTI: number;
    defaultRiskIncrease?: string;
  };
  hedgingRequired: boolean;
}

export interface BVNVerificationResult {
  valid: boolean;
  bvn: string;
  firstName?: string;
  lastName?: string;
  dateOfBirth?: string;
  phone?: string;
  verified: boolean;
  message: string;
}

export interface FraudCheckResult {
  fraudScore: number;
  isFraud: boolean;
  riskLevel: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  indicators: string[];
  recommendation: 'APPROVE' | 'REJECT' | 'REVIEW';
}

export interface ComplianceResult {
  compliant: boolean;
  checks: {
    [key: string]: {
      passed: boolean;
      message: string;
    };
  };
  overallStatus: string;
}

export interface EarlyWarningResult {
  loanId: string;
  customerName: string;
  warningScore: number;
  riskLevel: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  daysOverdue: number;
  defaultProbability3Months: number;
  warningSignals: string[];
  intervention: {
    urgency: string;
    actions: string[];
  };
}

export interface AlternativeDataScore {
  mobileMoneyScore: number;
  utilityPaymentScore: number;
  ajoParticipation: boolean;
  ajoTrustworthiness?: number;
  socialMediaScore: number;
  compositeScore: number;
}

export interface BlockchainBlock {
  index: number;
  timestamp: string;
  type: string;
  applicationId: string;
  data: any;
  hash: string;
  previousHash: string;
}

export interface SmartContract {
  contractId: string;
  borrower: string;
  loanAmount: number;
  monthlyPayment: number;
  status: 'PENDING' | 'ACTIVE' | 'FULFILLED' | 'DEFAULTED';
  payments: {
    total: number;
    paid: number;
    pending: number;
    late: number;
  };
  nextPaymentDue?: string;
}

export interface ModelInfo {
  modelName: string;
  version: string;
  trainedDate: string;
  metrics: {
    aucRoc: number;
    accuracy: number;
    precision: number;
    recall: number;
    f1Score: number;
  };
  featuresCount: number;
  trainingDataSize: number;
}

export interface ABTestExperiment {
  experimentId: string;
  name: string;
  status: 'ACTIVE' | 'COMPLETED' | 'PAUSED';
  variants: {
    name: string;
    trafficPercent: number;
    predictions: number;
    avgProbability: number;
  }[];
  startDate: string;
  endDate?: string;
}

export interface ChartDataPoint {
  name: string;
  value: number;
  label?: string;
}

export interface StressTestResult {
  scenario: string;
  additionalLoss: number;
  nplIncrease: number;
}
