import React, { useState } from 'react';
import { Box, Button, Grid, Paper, TextField, Typography, MenuItem, Alert } from '@mui/material';
import { apiClient } from '../services/api';
import type { LoanApplication, PredictionResult } from '../types';

export default function LoanApplicationPage() {
  const [formData, setFormData] = useState<Partial<LoanApplication>>({
    loanAmount: 2500000,
    monthlyIncome: 450000,
    tenureMonths: 12,
  });
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const prediction = await apiClient.predictSingle(formData as LoanApplication);
      setResult(prediction);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Prediction failed');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field: keyof LoanApplication) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [field]: e.target.value });
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        New Loan Application
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Application Form
            </Typography>
            <Box component="form" onSubmit={handleSubmit}>
              <TextField
                fullWidth
                margin="normal"
                label="BVN"
                required
                value={formData.bvn || ''}
                onChange={handleChange('bvn')}
              />
              <TextField
                fullWidth
                margin="normal"
                label="Loan Amount (₦)"
                type="number"
                required
                value={formData.loanAmount}
                onChange={handleChange('loanAmount')}
              />
              <TextField
                fullWidth
                margin="normal"
                label="Monthly Income (₦)"
                type="number"
                required
                value={formData.monthlyIncome}
                onChange={handleChange('monthlyIncome')}
              />
              <TextField
                fullWidth
                margin="normal"
                label="Tenure (Months)"
                type="number"
                select
                value={formData.tenureMonths}
                onChange={handleChange('tenureMonths')}
              >
                {[3, 6, 12, 24, 36].map((months) => (
                  <MenuItem key={months} value={months}>
                    {months} months
                  </MenuItem>
                ))}
              </TextField>
              <Button
                type="submit"
                variant="contained"
                fullWidth
                sx={{ mt: 2 }}
                disabled={loading}
              >
                {loading ? 'Processing...' : 'Submit Application'}
              </Button>
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          {result && (
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Credit Decision
              </Typography>
              <Alert severity={result.decision === 'APPROVE' ? 'success' : 'error'} sx={{ mb: 2 }}>
                {result.decision}
              </Alert>
              <Typography variant="body1">
                <strong>Risk Category:</strong> {result.riskCategory}
              </Typography>
              <Typography variant="body1">
                <strong>Default Probability:</strong> {result.defaultProbabilityPercent}%
              </Typography>
              {result.approvedAmount && (
                <>
                  <Typography variant="body1">
                    <strong>Approved Amount:</strong> ₦{result.approvedAmount.toLocaleString()}
                  </Typography>
                  <Typography variant="body1">
                    <strong>Interest Rate:</strong> {result.interestRate}%
                  </Typography>
                  <Typography variant="body1">
                    <strong>Monthly Payment:</strong> ₦{result.monthlyPayment?.toLocaleString()}
                  </Typography>
                </>
              )}
            </Paper>
          )}
          {error && <Alert severity="error">{error}</Alert>}
        </Grid>
      </Grid>
    </Box>
  );
}
