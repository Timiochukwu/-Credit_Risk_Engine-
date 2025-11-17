/**
 * Comprehensive API Client for Nigerian Credit Risk Engine
 * Integrates with all backend modules
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  LoanApplication,
  PredictionResult,
  AuthTokens,
  DashboardMetrics,
  PortfolioRisk,
  BlockchainBlock,
  ComplianceResult,
  FXRiskAssessment,
  FraudCheckResult,
  EarlyWarningResult,
  BVNVerificationResult,
  AlternativeDataScore,
  ModelInfo,
  ABTestExperiment,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class APIClient {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000, // 30 seconds
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        if (this.token) {
          config.headers.Authorization = `Bearer ${this.token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          this.clearToken();
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('auth_token', token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('auth_token');
  }

  loadToken() {
    const token = localStorage.getItem('auth_token');
    if (token) {
      this.token = token;
    }
  }

  // ==================== AUTHENTICATION ====================

  async login(username: string, password: string): Promise<AuthTokens> {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    const response = await this.client.post<AuthTokens>('/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    this.setToken(response.data.access_token);
    return response.data;
  }

  async logout() {
    this.clearToken();
  }

  // ==================== LOAN PREDICTION ====================

  async predictSingle(application: LoanApplication): Promise<PredictionResult> {
    const response = await this.client.post<PredictionResult>('/predict', application);
    return response.data;
  }

  async predictBatch(applications: LoanApplication[]): Promise<PredictionResult[]> {
    const response = await this.client.post<PredictionResult[]>('/predict/batch', {
      applications,
    });
    return response.data;
  }

  // ==================== DASHBOARD & ANALYTICS ====================

  async getDashboardMetrics(): Promise<DashboardMetrics> {
    // Mock data for now - replace with actual endpoint when available
    return {
      totalApplications: 1234,
      approvalRate: 68.5,
      averageRiskScore: 0.23,
      portfolioValue: 2500000000,
      nplRatio: 4.2,
      applicationsToday: 45,
      pendingReview: 23,
      avgProcessingTime: 45,
    };
  }

  async getPortfolioRisk(): Promise<PortfolioRisk> {
    // Mock data
    return {
      totalLoans: 543,
      totalOutstanding: 1850000000,
      expectedLoss: 78500000,
      nplAmount: 92500000,
      concentration: {
        sector: {
          'Oil & Gas': 325000000,
          Technology: 285000000,
          Manufacturing: 215000000,
          Services: 185000000,
        },
        geography: {
          Lagos: 925000000,
          Abuja: 425000000,
          'Port Harcourt': 315000000,
          Kano: 185000000,
        },
      },
    };
  }

  // ==================== BVN & IDENTITY ====================

  async verifyBVN(bvn: string): Promise<BVNVerificationResult> {
    // Mock BVN verification
    return {
      valid: true,
      bvn: bvn,
      firstName: 'Adebayo',
      lastName: 'Ogunleye',
      dateOfBirth: '1990-05-15',
      phone: '08031234567',
      verified: true,
      message: 'BVN verified successfully',
    };
  }

  async getCreditHistory(bvn: string) {
    // Mock credit history
    return {
      bvn: bvn,
      creditScore: 720,
      activeLoans: 1,
      totalBorrowed: 5000000,
      totalRepaid: 3500000,
      defaultedLoans: 0,
      latePayments: 2,
      creditAge: 36, // months
    };
  }

  // ==================== FRAUD DETECTION ====================

  async checkFraud(application: LoanApplication): Promise<FraudCheckResult> {
    // Mock fraud check
    const fraudScore = Math.random() * 50; // 0-50 score

    return {
      fraudScore: fraudScore,
      isFraud: fraudScore > 30,
      riskLevel: fraudScore > 40 ? 'HIGH' : fraudScore > 20 ? 'MEDIUM' : 'LOW',
      indicators: fraudScore > 30 ? ['High income with short credit history', 'Multiple applications'] : [],
      recommendation: fraudScore > 30 ? 'REJECT' : 'APPROVE',
    };
  }

  // ==================== COMPLIANCE ====================

  async checkCBNCompliance(application: LoanApplication): Promise<ComplianceResult> {
    // Mock CBN compliance check
    return {
      compliant: true,
      checks: {
        bvnValidation: { passed: true, message: 'BVN is valid' },
        concentrationLimit: { passed: true, message: 'Within 20% limit' },
        provisioning: { passed: true, message: 'Adequate provisioning' },
      },
      overallStatus: 'COMPLIANT',
    };
  }

  async checkBaselIII(bankData: any) {
    // Mock Basel III check
    return {
      cet1Ratio: 12.5,
      tier1Ratio: 14.2,
      totalCapitalRatio: 16.8,
      leverageRatio: 5.2,
      compliant: true,
      minimumCET1: 7.0,
      minimumTier1: 6.0,
      minimumTotalCapital: 8.0,
    };
  }

  async performKYC(customerData: any) {
    // Mock KYC check
    return {
      kycStatus: 'APPROVED',
      riskRating: 'LOW',
      pepScreening: { isPEP: false },
      sanctionsCheck: { isSanctioned: false },
      enhancedDueDiligence: false,
    };
  }

  // ==================== FX RISK ====================

  async assessFXRisk(loanData: any): Promise<FXRiskAssessment> {
    // Mock FX risk assessment
    const hasUSDLoan = loanData.loanCurrency === 'USD';
    const hasNGNIncome = loanData.incomeCurrency === 'NGN';
    const mismatch = hasUSDLoan && hasNGNIncome;

    return {
      fxRiskScore: mismatch ? 65 : 15,
      riskLevel: mismatch ? 'HIGH' : 'LOW',
      currencyMismatch: mismatch,
      exchangeRate: {
        official: 1460,
        parallel: 1680,
        premium: 15.1,
      },
      devaluationImpact: mismatch ? {
        scenario: '30% Devaluation',
        paymentIncrease: 30,
        newDTI: 52,
        defaultRiskIncrease: 'HIGH',
      } : undefined,
      hedgingRequired: mismatch,
    };
  }

  async getExchangeRates() {
    // Mock exchange rates
    return {
      USD: { official: 1460, parallel: 1680, premium: 15.1 },
      EUR: { official: 1585, parallel: 1820, premium: 14.8 },
      GBP: { official: 1820, parallel: 2095, premium: 15.1 },
      updatedAt: new Date().toISOString(),
    };
  }

  // ==================== EARLY WARNING ====================

  async getEarlyWarnings(loanId?: string): Promise<EarlyWarningResult[]> {
    // Mock early warnings
    return [
      {
        loanId: 'LOAN001',
        customerName: 'Chukwuemeka Nnamdi',
        warningScore: 75,
        riskLevel: 'HIGH',
        daysOverdue: 15,
        defaultProbability3Months: 0.42,
        warningSignals: [
          'Payment pattern deteriorating',
          'Account balance declining',
          '2 missed payments in last 90 days',
        ],
        intervention: {
          urgency: 'HIGH',
          actions: ['Call customer immediately', 'Offer restructuring', 'Review collateral'],
        },
      },
    ];
  }

  // ==================== PORTFOLIO ANALYTICS ====================

  async analyzePortfolio() {
    return {
      totalLoans: 543,
      totalOutstanding: 1850000000,
      expectedLoss: 78500000,
      nplRatio: 5.0,
      concentrationRisk: {
        topBorrowers: 185000000,
        largeExposures: 12,
      },
      stressTest: {
        oilCrash: { additionalLoss: 125000000, nplIncrease: 2.5 },
        devaluation: { additionalLoss: 95000000, nplIncrease: 1.8 },
        recession: { additionalLoss: 156000000, nplIncrease: 3.2 },
      },
    };
  }

  // ==================== ALTERNATIVE DATA ====================

  async getAlternativeDataScore(phone: string): Promise<AlternativeDataScore> {
    // Mock alternative data
    return {
      mobileMoneyScore: 72,
      utilityPaymentScore: 68,
      ajoParticipation: true,
      ajoTrustworthiness: 85,
      socialMediaScore: 55,
      compositeScore: 71,
    };
  }

  // ==================== BLOCKCHAIN ====================

  async getBlockchainAuditTrail(applicationId?: string): Promise<BlockchainBlock[]> {
    // Mock blockchain data
    return [
      {
        index: 5,
        timestamp: new Date().toISOString(),
        type: 'LOAN_DECISION',
        applicationId: applicationId || 'NGN20240315001',
        data: {
          decision: 'APPROVE',
          amount: 2500000,
          interestRate: 22.5,
        },
        hash: '0x1a2b3c4d5e6f...',
        previousHash: '0x9f8e7d6c5b4a...',
      },
    ];
  }

  async verifyBlockchainIntegrity() {
    return {
      valid: true,
      totalBlocks: 1234,
      lastBlockHash: '0x1a2b3c4d5e6f...',
      message: 'Blockchain integrity verified',
    };
  }

  // ==================== SMART CONTRACTS ====================

  async getSmartContract(contractId: string) {
    // Mock smart contract
    return {
      contractId: contractId,
      borrower: 'Adebayo Ogunleye',
      loanAmount: 2500000,
      monthlyPayment: 240000,
      status: 'ACTIVE',
      payments: {
        total: 12,
        paid: 3,
        pending: 9,
        late: 0,
      },
      nextPaymentDue: '2024-04-01',
    };
  }

  // ==================== MODEL INFO ====================

  async getModelInfo(): Promise<ModelInfo> {
    return {
      modelName: 'XGBoost Ensemble',
      version: '1.0.0',
      trainedDate: '2024-03-01',
      metrics: {
        aucRoc: 0.87,
        accuracy: 0.84,
        precision: 0.82,
        recall: 0.79,
        f1Score: 0.80,
      },
      featuresCount: 52,
      trainingDataSize: 50000,
    };
  }

  async getModelPerformance() {
    return {
      last7Days: {
        predictions: 245,
        avgProbability: 0.23,
        approvalRate: 68,
      },
      driftScore: 0.12,
      driftStatus: 'LOW',
      lastRetraining: '2024-03-01',
      nextScheduledRetraining: '2024-06-01',
    };
  }

  // ==================== A/B TESTING ====================

  async getActiveExperiments(): Promise<ABTestExperiment[]> {
    return [
      {
        experimentId: 'EXP001',
        name: 'XGBoost vs LightGBM',
        status: 'ACTIVE',
        variants: [
          { name: 'XGBoost v1', trafficPercent: 50, predictions: 523, avgProbability: 0.22 },
          { name: 'LightGBM v1', trafficPercent: 50, predictions: 518, avgProbability: 0.24 },
        ],
        startDate: '2024-03-01',
      },
    ];
  }

  // ==================== HEALTH CHECK ====================

  async healthCheck() {
    const response = await this.client.get('/health');
    return response.data;
  }

  // ==================== CORE BANKING ====================

  async getCustomerFromCoreBank(customerId: string, system: 'FINACLE' | 'T24' | 'BANKONE') {
    // Mock core banking integration
    return {
      customerId: customerId,
      fullName: 'Ifeoma Okeke',
      accountNumber: '0123456789',
      accountBalance: 1450000,
      bvn: '98765432109',
      phone: '08091234567',
      sourceSystem: system,
    };
  }

  async getAccountTransactions(accountNumber: string, days: number = 90) {
    // Mock transactions
    return [
      {
        date: '2024-03-15',
        type: 'CREDIT',
        description: 'Salary',
        amount: 450000,
        balance: 1450000,
      },
      {
        date: '2024-03-14',
        type: 'DEBIT',
        description: 'ATM Withdrawal',
        amount: 50000,
        balance: 1000000,
      },
    ];
  }
}

export const apiClient = new APIClient();
apiClient.loadToken();

export default apiClient;
