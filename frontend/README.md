# Nigerian Credit Risk Engine - Frontend 🎨

**Comprehensive React + TypeScript frontend** with full integration to all backend APIs.

## ✨ Features

### Core Features
- ✅ Modern React 18 with TypeScript
- ✅ Material-UI (MUI) components
- ✅ React Router for navigation
- ✅ Axios for API calls
- ✅ Vite for blazing-fast development
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ JWT authentication with auto-refresh
- ✅ Loading states and error handling

### Backend Integrations
- ✅ **Loan Predictions** - Real-time credit risk assessment
- ✅ **BVN Verification** - Nigerian Bank Verification Number validation
- ✅ **Fraud Detection** - ML-based fraud scoring
- ✅ **Compliance Checks** - CBN, Basel III, KYC/AML
- ✅ **FX Risk Assessment** - Currency mismatch detection
- ✅ **Early Warning System** - Default prediction alerts
- ✅ **Portfolio Analytics** - Risk metrics and stress testing
- ✅ **Blockchain Audit Trail** - Immutable decision records
- ✅ **Smart Contracts** - Automated loan management
- ✅ **Alternative Data** - Mobile money, utility payments
- ✅ **Core Banking** - Finacle, T24, BankOne integration
- ✅ **Model Performance** - A/B testing, drift monitoring

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- npm or yarn
- Backend API running on `http://localhost:8000`

### Installation

\`\`\`bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Open browser to http://localhost:3000
\`\`\`

### Build for Production

\`\`\`bash
# Build optimized production bundle
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
\`\`\`

## 📱 Pages & Features

### 1. **Login Page**
- JWT token-based authentication
- Auto-redirect if already logged in
- Secure token storage

**Default Credentials:**
- Username: `admin`
- Password: `password123`

### 2. **Dashboard**
Real-time metrics and KPIs:
- Total applications & approval rate
- Portfolio value & NPL ratio
- Early warning alerts table
- Processing metrics
- System health status

**API Calls:**
- `getDashboardMetrics()` - Key performance indicators
- `getEarlyWarnings()` - High-risk loan alerts

### 3. **Loan Application**
Complete loan application workflow:
- BVN verification
- Fraud check
- Real-time credit decision
- Risk category display
- Approval/rejection with explanation

**API Calls:**
- `verifyBVN(bvn)` - Validate BVN
- `checkFraud(application)` - Fraud detection
- `predictSingle(application)` - Get credit decision
- `checkCBNCompliance(application)` - Compliance check

### 4. **Portfolio Management**
Portfolio analytics and risk metrics:
- Concentration risk by sector/geography
- Stress testing scenarios
- Expected loss calculations
- Early warning system
- Loan performance tracking

**API Calls:**
- `getPortfolioRisk()` - Portfolio metrics
- `analyzePortfolio()` - Stress testing
- `getEarlyWarnings()` - At-risk loans

### 5. **Analytics & Reporting**
Advanced analytics features:
- FX risk assessment
- Compliance dashboard (CBN, Basel III)
- Fraud detection analytics
- Model performance metrics
- A/B testing results
- Blockchain audit trail

**API Calls:**
- `assessFXRisk(loanData)` - FX risk analysis
- `getExchangeRates()` - CBN exchange rates
- `checkBaselIII(bankData)` - Capital adequacy
- `performKYC(customerData)` - KYC/AML checks
- `getBlockchainAuditTrail()` - Audit history
- `getActiveExperiments()` - A/B tests
- `getModelInfo()` - Model performance

## 🔌 API Integration

### API Client (`src/services/api.ts`)

Comprehensive TypeScript API client with all backend endpoints:

\`\`\`typescript
import { apiClient } from './services/api';

// Authentication
await apiClient.login('username', 'password');

// Loan Prediction
const result = await apiClient.predictSingle(application);

// BVN Verification
const bvnResult = await apiClient.verifyBVN('12345678901');

// Fraud Check
const fraudResult = await apiClient.checkFraud(application);

// FX Risk Assessment
const fxRisk = await apiClient.assessFXRisk({
  loanCurrency: 'USD',
  incomeCurrency: 'NGN',
  loanAmount: 50000,
  monthlyIncome: 450000
});

// Early Warnings
const warnings = await apiClient.getEarlyWarnings();

// Blockchain Audit Trail
const auditTrail = await apiClient.getBlockchainAuditTrail('NGN001');

// Alternative Data
const altData = await apiClient.getAlternativeDataScore('08031234567');

// Core Banking Integration
const customer = await apiClient.getCustomerFromCoreBank('CUST001', 'FINACLE');
\`\`\`

### Available API Methods

#### Authentication
- `login(username, password)` - Authenticate user
- `logout()` - Clear auth token

#### Loan Processing
- `predictSingle(application)` - Single loan prediction
- `predictBatch(applications)` - Batch predictions
- `verifyBVN(bvn)` - BVN verification
- `getCreditHistory(bvn)` - Credit bureau data

#### Risk & Compliance
- `checkFraud(application)` - Fraud detection
- `checkCBNCompliance(application)` - CBN compliance
- `checkBaselIII(bankData)` - Basel III ratios
- `performKYC(customerData)` - KYC/AML validation
- `assessFXRisk(loanData)` - FX risk assessment

#### Analytics
- `getDashboardMetrics()` - Dashboard KPIs
- `getPortfolioRisk()` - Portfolio metrics
- `analyzePortfolio()` - Stress testing
- `getEarlyWarnings()` - At-risk loans
- `getAlternativeDataScore(phone)` - Alternative data

#### Blockchain & Smart Contracts
- `getBlockchainAuditTrail(applicationId)` - Audit history
- `verifyBlockchainIntegrity()` - Chain validation
- `getSmartContract(contractId)` - Contract details

#### Model Management
- `getModelInfo()` - Model metadata
- `getModelPerformance()` - Performance metrics
- `getActiveExperiments()` - A/B tests

#### Core Banking
- `getCustomerFromCoreBank(customerId, system)` - Customer data
- `getAccountTransactions(accountNumber, days)` - Transactions

## 📊 TypeScript Types (`src/types/index.ts`)

All API responses are fully typed:

\`\`\`typescript
import type {
  LoanApplication,
  PredictionResult,
  BVNVerificationResult,
  FraudCheckResult,
  FXRiskAssessment,
  ComplianceResult,
  EarlyWarningResult,
  PortfolioRisk,
  BlockchainBlock,
  ModelInfo,
  ABTestExperiment,
} from './types';
\`\`\`

## 🎨 UI Components

### Material-UI Theme

Custom theme with Nigerian banking colors:
- Primary: #1976d2 (Blue)
- Secondary: #388e3c (Green)
- Error: #d32f2f (Red)
- Warning: #f57c00 (Orange)

### Layout Components
- **Layout** (`src/components/Layout.tsx`) - App shell with navigation
- **PrivateRoute** (`src/components/PrivateRoute.tsx`) - Auth protection

## 🔒 Authentication Flow

1. User enters credentials on Login page
2. `apiClient.login()` sends request to `/token`
3. Receive JWT token
4. Store token in localStorage
5. Add token to all subsequent requests via Axios interceptor
6. Auto-redirect to `/dashboard`
7. On 401 error, clear token and redirect to `/login`

## 🌐 Environment Variables

Create `.env` file in frontend directory:

\`\`\`env
VITE_API_URL=http://localhost:8000
\`\`\`

## 📁 Project Structure

\`\`\`
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/          # Reusable components
│   │   ├── Layout.tsx
│   │   └── PrivateRoute.tsx
│   ├── pages/              # Page components
│   │   ├── LoginPage.tsx
│   │   ├── DashboardPage.tsx
│   │   ├── LoanApplicationPage.tsx
│   │   ├── PortfolioPage.tsx
│   │   └── AnalyticsPage.tsx
│   ├── services/           # API client
│   │   └── api.ts
│   ├── types/              # TypeScript types
│   │   └── index.ts
│   ├── App.tsx             # Main app component
│   ├── main.tsx            # Entry point
│   └── index.css           # Global styles
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
\`\`\`

## 🚀 Deployment

### Production Build

\`\`\`bash
npm run build
# Output: dist/
\`\`\`

### Deploy to Netlify/Vercel

\`\`\`bash
# Netlify
netlify deploy --dir=dist --prod

# Vercel
vercel --prod
\`\`\`

### Environment Configuration

Set `VITE_API_URL` to your production API endpoint.

## 🧪 Development Tips

### Hot Module Replacement (HMR)
Vite provides instant HMR - changes appear instantly without full page reload.

### TypeScript Checking
\`\`\`bash
npm run build  # Also runs TypeScript compiler
\`\`\`

### API Mocking
Currently using mock data in API client. Replace with real endpoints when backend is running.

## 📚 Technology Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18.2.0 | UI framework |
| TypeScript | 5.3.3 | Type safety |
| Material-UI | 5.15.0 | Component library |
| Axios | 1.6.2 | HTTP client |
| React Router | 6.20.0 | Routing |
| Vite | 5.0.8 | Build tool |
| date-fns | 3.0.6 | Date formatting |

## 🔗 Integration with Backend

The frontend is designed to integrate seamlessly with the Python FastAPI backend:

### Backend Endpoints
- **API Base**: `http://localhost:8000`
- **Swagger Docs**: `http://localhost:8000/docs`
- **Auth**: `/token` (POST)
- **Prediction**: `/predict` (POST)
- **Health**: `/health` (GET)

### CORS Configuration
Backend must enable CORS for frontend origin:
\`\`\`python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
\`\`\`

## 🎯 Next Steps

To complete the integration:
1. ✅ Enhanced API client with all endpoints
2. ✅ Updated TypeScript types
3. ✅ Enhanced Dashboard with real-time data
4. ⏳ Complete Loan Application form with multi-step workflow
5. ⏳ Build Portfolio page with charts
6. ⏳ Build Analytics page with all compliance features
7. ⏳ Add Blockchain audit trail viewer
8. ⏳ Add charts (Recharts) for visualization
9. ⏳ Add form validation (Formik + Yup)
10. ⏳ Add unit tests (Jest + React Testing Library)

## 📄 License

MIT

---

**Built with ❤️ for Nigerian Financial Institutions** 🇳🇬
