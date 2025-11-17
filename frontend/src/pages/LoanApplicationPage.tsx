import React, { useState } from 'react';
import {
  Box,
  Button,
  Grid,
  Paper,
  TextField,
  Typography,
  MenuItem,
  Alert,
  Stepper,
  Step,
  StepLabel,
  CircularProgress,
  Chip,
  Divider,
  Card,
  CardContent,
  LinearProgress,
} from '@mui/material';
import {
  CheckCircle,
  Error,
  Warning,
  AccountBalance,
  Security,
  Assessment,
} from '@mui/icons-material';
import { apiClient } from '../services/api';
import type {
  LoanApplication,
  PredictionResult,
  BVNVerificationResult,
  FraudCheckResult,
  ComplianceResult,
  FXRiskAssessment,
} from '../types';

const steps = ['BVN Verification', 'Personal Details', 'Loan Details', 'Verification', 'Decision'];

export default function LoanApplicationPage() {
  const [activeStep, setActiveStep] = useState(0);
  const [formData, setFormData] = useState<Partial<LoanApplication>>({
    loanAmount: 2500000,
    monthlyIncome: 450000,
    tenureMonths: 12,
    loanCurrency: 'NGN',
    incomeCurrency: 'NGN',
  });

  // Results from different checks
  const [bvnResult, setBvnResult] = useState<BVNVerificationResult | null>(null);
  const [fraudResult, setFraudResult] = useState<FraudCheckResult | null>(null);
  const [complianceResult, setComplianceResult] = useState<ComplianceResult | null>(null);
  const [fxRiskResult, setFxRiskResult] = useState<FXRiskAssessment | null>(null);
  const [creditDecision, setCreditDecision] = useState<PredictionResult | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (field: keyof LoanApplication) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [field]: e.target.value });
  };

  const verifyBVN = async () => {
    if (!formData.bvn || formData.bvn.length !== 11) {
      setError('BVN must be 11 digits');
      return;
    }

    setLoading(true);
    setError('');
    try {
      const result = await apiClient.verifyBVN(formData.bvn);
      setBvnResult(result);

      if (result.isValid) {
        // Auto-populate fields from BVN
        setFormData({
          ...formData,
          firstName: result.firstName,
          lastName: result.lastName,
          phone: result.phone,
          dateOfBirth: result.dateOfBirth,
        });
        setActiveStep(1);
      } else {
        setError('BVN verification failed: ' + result.message);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'BVN verification failed');
    } finally {
      setLoading(false);
    }
  };

  const handleNext = async () => {
    if (activeStep === 0) {
      await verifyBVN();
    } else if (activeStep === 3) {
      // Run all verifications in parallel
      await runVerifications();
    } else {
      setActiveStep((prev) => prev + 1);
    }
  };

  const runVerifications = async () => {
    setLoading(true);
    setError('');
    try {
      // Run fraud check, compliance, and FX risk in parallel
      const [fraud, compliance, fxRisk, credit] = await Promise.all([
        apiClient.checkFraud(formData as LoanApplication),
        apiClient.checkCBNCompliance(formData as LoanApplication),
        apiClient.assessFXRisk({
          loanCurrency: formData.loanCurrency || 'NGN',
          incomeCurrency: formData.incomeCurrency || 'NGN',
          loanAmount: formData.loanAmount || 0,
          monthlyIncome: formData.monthlyIncome || 0,
        }),
        apiClient.predictSingle(formData as LoanApplication),
      ]);

      setFraudResult(fraud);
      setComplianceResult(compliance);
      setFxRiskResult(fxRisk);
      setCreditDecision(credit);
      setActiveStep(4);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Verification failed');
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    setActiveStep((prev) => prev - 1);
  };

  const renderStepContent = () => {
    switch (activeStep) {
      case 0:
        return (
          <Box>
            <Typography variant="body1" color="textSecondary" sx={{ mb: 3 }}>
              Enter your Bank Verification Number (BVN) to begin the loan application process.
            </Typography>
            <TextField
              fullWidth
              label="BVN"
              required
              value={formData.bvn || ''}
              onChange={handleChange('bvn')}
              inputProps={{ maxLength: 11 }}
              helperText="11-digit Bank Verification Number"
            />
            {bvnResult && bvnResult.isValid && (
              <Alert severity="success" sx={{ mt: 2 }} icon={<CheckCircle />}>
                BVN verified successfully! Welcome, {bvnResult.firstName} {bvnResult.lastName}
              </Alert>
            )}
          </Box>
        );

      case 1:
        return (
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="First Name"
                required
                value={formData.firstName || ''}
                onChange={handleChange('firstName')}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Last Name"
                required
                value={formData.lastName || ''}
                onChange={handleChange('lastName')}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Email"
                type="email"
                required
                value={formData.email || ''}
                onChange={handleChange('email')}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Phone"
                required
                value={formData.phone || ''}
                onChange={handleChange('phone')}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Date of Birth"
                type="date"
                required
                value={formData.dateOfBirth || ''}
                onChange={handleChange('dateOfBirth')}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="State of Residence"
                select
                value={formData.stateOfResidence || ''}
                onChange={handleChange('stateOfResidence')}
              >
                {['Lagos', 'Abuja', 'Rivers', 'Kano', 'Oyo', 'Delta'].map((state) => (
                  <MenuItem key={state} value={state}>
                    {state}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Residential Address"
                required
                value={formData.address || ''}
                onChange={handleChange('address')}
              />
            </Grid>
          </Grid>
        );

      case 2:
        return (
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Loan Amount (₦)"
                type="number"
                required
                value={formData.loanAmount}
                onChange={handleChange('loanAmount')}
                inputProps={{ min: 50000, max: 50000000, step: 50000 }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Tenure (Months)"
                select
                required
                value={formData.tenureMonths}
                onChange={handleChange('tenureMonths')}
              >
                {[3, 6, 12, 18, 24, 36, 48, 60].map((months) => (
                  <MenuItem key={months} value={months}>
                    {months} months
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Employment Status"
                select
                required
                value={formData.employmentStatus || ''}
                onChange={handleChange('employmentStatus')}
              >
                {['EMPLOYED', 'SELF_EMPLOYED', 'UNEMPLOYED', 'STUDENT', 'RETIRED'].map((status) => (
                  <MenuItem key={status} value={status}>
                    {status.replace('_', ' ')}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Monthly Income (₦)"
                type="number"
                required
                value={formData.monthlyIncome}
                onChange={handleChange('monthlyIncome')}
                inputProps={{ min: 0 }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Monthly Expenses (₦)"
                type="number"
                required
                value={formData.monthlyExpenses || 0}
                onChange={handleChange('monthlyExpenses')}
                inputProps={{ min: 0 }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Existing Loans (₦)"
                type="number"
                value={formData.existingLoans || 0}
                onChange={handleChange('existingLoans')}
                inputProps={{ min: 0 }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Loan Currency"
                select
                value={formData.loanCurrency || 'NGN'}
                onChange={handleChange('loanCurrency')}
              >
                {['NGN', 'USD', 'GBP', 'EUR'].map((currency) => (
                  <MenuItem key={currency} value={currency}>
                    {currency}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Income Currency"
                select
                value={formData.incomeCurrency || 'NGN'}
                onChange={handleChange('incomeCurrency')}
              >
                {['NGN', 'USD', 'GBP', 'EUR'].map((currency) => (
                  <MenuItem key={currency} value={currency}>
                    {currency}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Loan Purpose"
                multiline
                rows={3}
                value={formData.loanPurpose || ''}
                onChange={handleChange('loanPurpose')}
                helperText="Please describe how you intend to use this loan"
              />
            </Grid>
          </Grid>
        );

      case 3:
        return (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Assessment sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              Ready to Process Application
            </Typography>
            <Typography variant="body1" color="textSecondary" sx={{ mb: 3 }}>
              We will now verify your application through our comprehensive risk assessment system:
            </Typography>
            <Grid container spacing={2} sx={{ mt: 2 }}>
              <Grid item xs={12} sm={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Security color="primary" sx={{ mb: 1 }} />
                    <Typography variant="subtitle2">Fraud Detection</Typography>
                    <Typography variant="caption" color="textSecondary">
                      ML-based fraud scoring
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Card variant="outlined">
                  <CardContent>
                    <AccountBalance color="primary" sx={{ mb: 1 }} />
                    <Typography variant="subtitle2">CBN Compliance</Typography>
                    <Typography variant="caption" color="textSecondary">
                      Regulatory compliance check
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Assessment color="primary" sx={{ mb: 1 }} />
                    <Typography variant="subtitle2">FX Risk Assessment</Typography>
                    <Typography variant="caption" color="textSecondary">
                      Currency mismatch analysis
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Card variant="outlined">
                  <CardContent>
                    <CheckCircle color="primary" sx={{ mb: 1 }} />
                    <Typography variant="subtitle2">Credit Decision</Typography>
                    <Typography variant="caption" color="textSecondary">
                      AI-powered risk scoring
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Box>
        );

      case 4:
        return (
          <Box>
            {/* Credit Decision */}
            {creditDecision && (
              <Alert
                severity={creditDecision.decision === 'APPROVE' ? 'success' : creditDecision.decision === 'REVIEW' ? 'warning' : 'error'}
                icon={creditDecision.decision === 'APPROVE' ? <CheckCircle /> : <Warning />}
                sx={{ mb: 3 }}
              >
                <Typography variant="h6" gutterBottom>
                  Application {creditDecision.decision}
                </Typography>
                <Typography variant="body2">
                  Risk Category: <strong>{creditDecision.riskCategory}</strong>
                </Typography>
                <Typography variant="body2">
                  Default Probability: <strong>{creditDecision.defaultProbabilityPercent}%</strong>
                </Typography>
              </Alert>
            )}

            {creditDecision && creditDecision.decision === 'APPROVE' && (
              <Paper sx={{ p: 3, mb: 3, bgcolor: 'success.light', color: 'success.contrastText' }}>
                <Typography variant="h6" gutterBottom>
                  Loan Terms
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2">Approved Amount:</Typography>
                    <Typography variant="h6">₦{creditDecision.approvedAmount?.toLocaleString()}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2">Interest Rate:</Typography>
                    <Typography variant="h6">{creditDecision.interestRate}% p.a.</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2">Monthly Payment:</Typography>
                    <Typography variant="h6">₦{creditDecision.monthlyPayment?.toLocaleString()}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2">Tenure:</Typography>
                    <Typography variant="h6">{formData.tenureMonths} months</Typography>
                  </Grid>
                </Grid>
              </Paper>
            )}

            {/* Verification Results */}
            <Grid container spacing={2}>
              {/* Fraud Check */}
              {fraudResult && (
                <Grid item xs={12} sm={6}>
                  <Card>
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                        <Security sx={{ mr: 1 }} />
                        <Typography variant="h6">Fraud Check</Typography>
                      </Box>
                      <Chip
                        label={fraudResult.riskLevel}
                        color={fraudResult.riskLevel === 'LOW' ? 'success' : fraudResult.riskLevel === 'MEDIUM' ? 'warning' : 'error'}
                        size="small"
                        sx={{ mb: 1 }}
                      />
                      <Typography variant="body2" color="textSecondary">
                        Fraud Score: {fraudResult.fraudScore}/100
                      </Typography>
                      <LinearProgress
                        variant="determinate"
                        value={fraudResult.fraudScore}
                        color={fraudResult.fraudScore < 30 ? 'success' : fraudResult.fraudScore < 70 ? 'warning' : 'error'}
                        sx={{ mt: 1 }}
                      />
                    </CardContent>
                  </Card>
                </Grid>
              )}

              {/* Compliance */}
              {complianceResult && (
                <Grid item xs={12} sm={6}>
                  <Card>
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                        <AccountBalance sx={{ mr: 1 }} />
                        <Typography variant="h6">CBN Compliance</Typography>
                      </Box>
                      <Chip
                        label={complianceResult.isCompliant ? 'COMPLIANT' : 'NON-COMPLIANT'}
                        color={complianceResult.isCompliant ? 'success' : 'error'}
                        size="small"
                        sx={{ mb: 1 }}
                      />
                      {complianceResult.violations && complianceResult.violations.length > 0 && (
                        <Typography variant="caption" color="error">
                          {complianceResult.violations.length} violation(s) found
                        </Typography>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              )}

              {/* FX Risk */}
              {fxRiskResult && (
                <Grid item xs={12} sm={6}>
                  <Card>
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                        <Assessment sx={{ mr: 1 }} />
                        <Typography variant="h6">FX Risk</Typography>
                      </Box>
                      <Chip
                        label={fxRiskResult.riskLevel}
                        color={fxRiskResult.riskLevel === 'LOW' ? 'success' : fxRiskResult.riskLevel === 'MEDIUM' ? 'warning' : 'error'}
                        size="small"
                        sx={{ mb: 1 }}
                      />
                      <Typography variant="body2" color="textSecondary">
                        FX Risk Score: {fxRiskResult.fxRiskScore}/100
                      </Typography>
                      {fxRiskResult.currencyMismatch && (
                        <Alert severity="warning" sx={{ mt: 1 }}>
                          Currency mismatch detected
                        </Alert>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              )}
            </Grid>
          </Box>
        );

      default:
        return null;
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom fontWeight={600}>
        New Loan Application
      </Typography>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <>
            {renderStepContent()}

            <Divider sx={{ my: 3 }} />

            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Button disabled={activeStep === 0 || activeStep === 4} onClick={handleBack}>
                Back
              </Button>
              {activeStep < 4 && (
                <Button variant="contained" onClick={handleNext} disabled={loading}>
                  {activeStep === 3 ? 'Process Application' : 'Next'}
                </Button>
              )}
            </Box>
          </>
        )}
      </Paper>
    </Box>
  );
}
