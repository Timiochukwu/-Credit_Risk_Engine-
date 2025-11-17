/**
 * API Client for Nigerian Credit Risk Engine
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import type { LoanApplication, PredictionResult, AuthTokens, DashboardMetrics, PortfolioRisk } from '../types';

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
          // Handle unauthorized
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

  // Authentication
  async login(username: string, password: string): Promise<AuthTokens> {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    const response = await this.client.post<AuthTokens>('/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    this.setToken(response.data.accessToken);
    return response.data;
  }

  async logout() {
    this.clearToken();
  }

  // Loan Prediction
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

  // Dashboard & Analytics
  async getDashboardMetrics(): Promise<DashboardMetrics> {
    const response = await this.client.get<DashboardMetrics>('/dashboard/metrics');
    return response.data;
  }

  async getPortfolioRisk(): Promise<PortfolioRisk> {
    const response = await this.client.get<PortfolioRisk>('/analytics/portfolio');
    return response.data;
  }

  // Model Information
  async getModelInfo() {
    const response = await this.client.get('/model/info');
    return response.data;
  }

  // Health Check
  async healthCheck() {
    const response = await this.client.get('/health');
    return response.data;
  }

  // BVN Verification
  async verifyBVN(bvn: string) {
    const response = await this.client.post('/integrations/bvn/verify', { bvn });
    return response.data;
  }

  // Fraud Detection
  async checkFraud(application: LoanApplication) {
    const response = await this.client.post('/security/fraud/check', application);
    return response.data;
  }
}

export const apiClient = new APIClient();
apiClient.loadToken();

export default apiClient;
