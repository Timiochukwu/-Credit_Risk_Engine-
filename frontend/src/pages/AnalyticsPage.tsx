import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Button,
  TextField,
  Alert,
  Chip,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Divider,
  LinearProgress,
  CircularProgress,
} from '@mui/material';
import {
  TrendingUp,
  AccountBalance,
  Security,
  Assessment,
  Science,
  Link as LinkIcon,
  AttachMoney,
} from '@mui/icons-material';
import { apiClient } from '../services/api';
import type {
  FXRiskAssessment,
  ComplianceResult,
  ModelInfo,
  ABTestExperiment,
  BlockchainBlock,
} from '../types';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

export default function AnalyticsPage() {
  const [activeTab, setActiveTab] = useState(0);

  // FX Risk State
  const [fxRiskData, setFxRiskData] = useState({
    loanCurrency: 'USD',
    incomeCurrency: 'NGN',
    loanAmount: 50000,
    monthlyIncome: 450000,
  });
  const [fxRiskResult, setFxRiskResult] = useState<FXRiskAssessment | null>(null);
  const [fxLoading, setFxLoading] = useState(false);

  // Compliance State
  const [complianceResult, setComplianceResult] = useState<ComplianceResult | null>(null);
  const [complianceLoading, setComplianceLoading] = useState(false);

  // Model Performance State
  const [modelInfo, setModelInfo] = useState<ModelInfo | null>(null);
  const [experiments, setExperiments] = useState<ABTestExperiment[]>([]);
  const [modelLoading, setModelLoading] = useState(false);

  // Blockchain State
  const [blockchainApplicationId, setBlockchainApplicationId] = useState('NGN001');
  const [blockchainAudit, setBlockchainAudit] = useState<BlockchainBlock[]>([]);
  const [blockchainLoading, setBlockchainLoading] = useState(false);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const assessFXRisk = async () => {
    setFxLoading(true);
    try {
      const result = await apiClient.assessFXRisk(fxRiskData);
      setFxRiskResult(result);
    } catch (error) {
      console.error('FX Risk assessment failed:', error);
    } finally {
      setFxLoading(false);
    }
  };

  const checkCompliance = async () => {
    setComplianceLoading(true);
    try {
      const result = await apiClient.checkCBNCompliance({
        bvn: '12345678901',
        loanAmount: 5000000,
        monthlyIncome: 450000,
        existingLoans: 0,
      } as any);
      setComplianceResult(result);
    } catch (error) {
      console.error('Compliance check failed:', error);
    } finally {
      setComplianceLoading(false);
    }
  };

  const loadModelPerformance = async () => {
    setModelLoading(true);
    try {
      const [info, exp] = await Promise.all([
        apiClient.getModelInfo(),
        apiClient.getActiveExperiments(),
      ]);
      setModelInfo(info);
      setExperiments(exp);
    } catch (error) {
      console.error('Failed to load model performance:', error);
    } finally {
      setModelLoading(false);
    }
  };

  const loadBlockchainAudit = async () => {
    setBlockchainLoading(true);
    try {
      const audit = await apiClient.getBlockchainAuditTrail(blockchainApplicationId);
      setBlockchainAudit(audit);
    } catch (error) {
      console.error('Failed to load blockchain audit:', error);
    } finally {
      setBlockchainLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom fontWeight={600}>
        Analytics & Reporting
      </Typography>

      <Paper sx={{ mb: 3 }}>
        <Tabs value={activeTab} onChange={handleTabChange} variant="scrollable" scrollButtons="auto">
          <Tab label="FX Risk Assessment" icon={<AttachMoney />} iconPosition="start" />
          <Tab label="Compliance Dashboard" icon={<AccountBalance />} iconPosition="start" />
          <Tab label="Model Performance" icon={<Science />} iconPosition="start" />
          <Tab label="Blockchain Audit" icon={<LinkIcon />} iconPosition="start" />
        </Tabs>
      </Paper>

      {/* FX Risk Assessment Tab */}
      <TabPanel value={activeTab} index={0}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={5}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom fontWeight={600}>
                FX Risk Calculator
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
                Assess currency mismatch risk for foreign currency loans
              </Typography>

              <TextField
                fullWidth
                select
                label="Loan Currency"
                value={fxRiskData.loanCurrency}
                onChange={(e) => setFxRiskData({ ...fxRiskData, loanCurrency: e.target.value })}
                sx={{ mb: 2 }}
                SelectProps={{ native: true }}
              >
                <option value="NGN">NGN</option>
                <option value="USD">USD</option>
                <option value="GBP">GBP</option>
                <option value="EUR">EUR</option>
              </TextField>

              <TextField
                fullWidth
                select
                label="Income Currency"
                value={fxRiskData.incomeCurrency}
                onChange={(e) => setFxRiskData({ ...fxRiskData, incomeCurrency: e.target.value })}
                sx={{ mb: 2 }}
                SelectProps={{ native: true }}
              >
                <option value="NGN">NGN</option>
                <option value="USD">USD</option>
                <option value="GBP">GBP</option>
                <option value="EUR">EUR</option>
              </TextField>

              <TextField
                fullWidth
                type="number"
                label="Loan Amount"
                value={fxRiskData.loanAmount}
                onChange={(e) => setFxRiskData({ ...fxRiskData, loanAmount: Number(e.target.value) })}
                sx={{ mb: 2 }}
              />

              <TextField
                fullWidth
                type="number"
                label="Monthly Income"
                value={fxRiskData.monthlyIncome}
                onChange={(e) => setFxRiskData({ ...fxRiskData, monthlyIncome: Number(e.target.value) })}
                sx={{ mb: 3 }}
              />

              <Button variant="contained" fullWidth onClick={assessFXRisk} disabled={fxLoading}>
                {fxLoading ? 'Assessing...' : 'Assess FX Risk'}
              </Button>
            </Paper>
          </Grid>

          <Grid item xs={12} md={7}>
            {fxRiskResult && (
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom fontWeight={600}>
                  FX Risk Assessment Results
                </Typography>

                <Alert
                  severity={
                    fxRiskResult.riskLevel === 'LOW'
                      ? 'success'
                      : fxRiskResult.riskLevel === 'MEDIUM'
                      ? 'warning'
                      : 'error'
                  }
                  sx={{ mb: 3 }}
                >
                  <Typography variant="h6">Risk Level: {fxRiskResult.riskLevel}</Typography>
                  <Typography variant="body2">FX Risk Score: {fxRiskResult.fxRiskScore}/100</Typography>
                </Alert>

                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography variant="caption" color="textSecondary">
                          Currency Mismatch
                        </Typography>
                        <Typography variant="h6">
                          {fxRiskResult.currencyMismatch ? 'YES' : 'NO'}
                        </Typography>
                        {fxRiskResult.currencyMismatch && (
                          <Chip label="High Risk" color="error" size="small" sx={{ mt: 1 }} />
                        )}
                      </CardContent>
                    </Card>
                  </Grid>

                  <Grid item xs={12} sm={6}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography variant="caption" color="textSecondary">
                          Official Exchange Rate
                        </Typography>
                        <Typography variant="h6">
                          ₦{fxRiskResult.exchangeRate.official.toFixed(2)}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          Premium: {fxRiskResult.exchangeRate.premium}%
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>

                  {fxRiskResult.devaluationImpact && (
                    <Grid item xs={12}>
                      <Card variant="outlined" sx={{ bgcolor: 'warning.light' }}>
                        <CardContent>
                          <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                            Devaluation Impact Analysis
                          </Typography>
                          <Typography variant="body2">
                            Scenario: {fxRiskResult.devaluationImpact.scenario}
                          </Typography>
                          <Typography variant="body2">
                            Payment Increase: +₦{fxRiskResult.devaluationImpact.paymentIncrease.toLocaleString()}
                          </Typography>
                          <Typography variant="body2">
                            New DTI Ratio: {fxRiskResult.devaluationImpact.newDTI}%
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  )}
                </Grid>
              </Paper>
            )}
          </Grid>
        </Grid>
      </TabPanel>

      {/* Compliance Dashboard Tab */}
      <TabPanel value={activeTab} index={1}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" gutterBottom fontWeight={600}>
                CBN Compliance Check
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                Verify compliance with Central Bank of Nigeria regulations
              </Typography>
              <Button variant="contained" onClick={checkCompliance} disabled={complianceLoading}>
                {complianceLoading ? 'Checking...' : 'Run Compliance Check'}
              </Button>
            </Paper>
          </Grid>

          {complianceResult && (
            <>
              <Grid item xs={12}>
                <Alert severity={complianceResult.isCompliant ? 'success' : 'error'}>
                  <Typography variant="h6">
                    {complianceResult.isCompliant ? 'COMPLIANT' : 'NON-COMPLIANT'}
                  </Typography>
                  <Typography variant="body2">
                    Compliance Score: {complianceResult.complianceScore}/100
                  </Typography>
                </Alert>
              </Grid>

              {complianceResult.violations && complianceResult.violations.length > 0 && (
                <Grid item xs={12}>
                  <Paper sx={{ p: 3 }}>
                    <Typography variant="h6" gutterBottom color="error">
                      Violations Found ({complianceResult.violations.length})
                    </Typography>
                    <TableContainer>
                      <Table>
                        <TableHead>
                          <TableRow>
                            <TableCell>Rule</TableCell>
                            <TableCell>Severity</TableCell>
                            <TableCell>Description</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {complianceResult.violations.map((violation, index) => (
                            <TableRow key={index}>
                              <TableCell>{violation.rule}</TableCell>
                              <TableCell>
                                <Chip
                                  label={violation.severity}
                                  color={violation.severity === 'HIGH' ? 'error' : 'warning'}
                                  size="small"
                                />
                              </TableCell>
                              <TableCell>{violation.description}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </Paper>
                </Grid>
              )}

              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <AccountBalance sx={{ mr: 1, color: 'primary.main' }} />
                      <Typography variant="h6">Basel III Compliance</Typography>
                    </Box>
                    <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                      Capital adequacy ratios and risk-weighted assets
                    </Typography>
                    <Button variant="outlined" size="small">
                      Check Basel III
                    </Button>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Security sx={{ mr: 1, color: 'primary.main' }} />
                      <Typography variant="h6">KYC/AML Validation</Typography>
                    </Box>
                    <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                      Know Your Customer and Anti-Money Laundering checks
                    </Typography>
                    <Button variant="outlined" size="small">
                      Perform KYC/AML
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
            </>
          )}
        </Grid>
      </TabPanel>

      {/* Model Performance Tab */}
      <TabPanel value={activeTab} index={2}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" gutterBottom fontWeight={600}>
                Model Performance Metrics
              </Typography>
              <Button variant="contained" onClick={loadModelPerformance} disabled={modelLoading}>
                {modelLoading ? 'Loading...' : 'Load Model Performance'}
              </Button>
            </Paper>
          </Grid>

          {modelInfo && (
            <>
              <Grid item xs={12} md={4}>
                <Card>
                  <CardContent>
                    <Typography variant="subtitle2" color="textSecondary">
                      Model Name
                    </Typography>
                    <Typography variant="h6">{modelInfo.modelName}</Typography>
                    <Typography variant="caption">Version: {modelInfo.version}</Typography>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={4}>
                <Card>
                  <CardContent>
                    <Typography variant="subtitle2" color="textSecondary">
                      Accuracy
                    </Typography>
                    <Typography variant="h6">{(modelInfo.metrics.accuracy * 100).toFixed(2)}%</Typography>
                    <LinearProgress
                      variant="determinate"
                      value={modelInfo.metrics.accuracy * 100}
                      color="success"
                      sx={{ mt: 1 }}
                    />
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={4}>
                <Card>
                  <CardContent>
                    <Typography variant="subtitle2" color="textSecondary">
                      AUC Score
                    </Typography>
                    <Typography variant="h6">{modelInfo.metrics.auc.toFixed(4)}</Typography>
                    <LinearProgress
                      variant="determinate"
                      value={modelInfo.metrics.auc * 100}
                      color="primary"
                      sx={{ mt: 1 }}
                    />
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12}>
                <Paper sx={{ p: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Model Metrics
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6} sm={3}>
                      <Typography variant="caption" color="textSecondary">
                        Precision
                      </Typography>
                      <Typography variant="h6">{(modelInfo.metrics.precision * 100).toFixed(2)}%</Typography>
                    </Grid>
                    <Grid item xs={6} sm={3}>
                      <Typography variant="caption" color="textSecondary">
                        Recall
                      </Typography>
                      <Typography variant="h6">{(modelInfo.metrics.recall * 100).toFixed(2)}%</Typography>
                    </Grid>
                    <Grid item xs={6} sm={3}>
                      <Typography variant="caption" color="textSecondary">
                        F1 Score
                      </Typography>
                      <Typography variant="h6">{(modelInfo.metrics.f1Score * 100).toFixed(2)}%</Typography>
                    </Grid>
                    <Grid item xs={6} sm={3}>
                      <Typography variant="caption" color="textSecondary">
                        Gini Coefficient
                      </Typography>
                      <Typography variant="h6">{modelInfo.metrics.giniCoefficient.toFixed(4)}</Typography>
                    </Grid>
                  </Grid>
                </Paper>
              </Grid>
            </>
          )}

          {experiments.length > 0 && (
            <Grid item xs={12}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Active A/B Tests
                </Typography>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Experiment</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Control</TableCell>
                        <TableCell>Treatment</TableCell>
                        <TableCell>Traffic Split</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {experiments.map((exp) => (
                        <TableRow key={exp.experimentId}>
                          <TableCell>{exp.experimentName}</TableCell>
                          <TableCell>
                            <Chip
                              label={exp.status}
                              color={exp.status === 'ACTIVE' ? 'success' : 'default'}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>{exp.controlModelVersion}</TableCell>
                          <TableCell>{exp.treatmentModelVersion}</TableCell>
                          <TableCell>{(exp.trafficSplit.treatment * 100).toFixed(0)}%</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Paper>
            </Grid>
          )}
        </Grid>
      </TabPanel>

      {/* Blockchain Audit Tab */}
      <TabPanel value={activeTab} index={3}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" gutterBottom fontWeight={600}>
                Blockchain Audit Trail
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
                View immutable audit trail for loan applications
              </Typography>

              <Box sx={{ display: 'flex', gap: 2 }}>
                <TextField
                  label="Application ID"
                  value={blockchainApplicationId}
                  onChange={(e) => setBlockchainApplicationId(e.target.value)}
                  sx={{ flex: 1 }}
                />
                <Button variant="contained" onClick={loadBlockchainAudit} disabled={blockchainLoading}>
                  {blockchainLoading ? 'Loading...' : 'Load Audit Trail'}
                </Button>
              </Box>
            </Paper>
          </Grid>

          {blockchainAudit.length > 0 && (
            <Grid item xs={12}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Audit Trail ({blockchainAudit.length} blocks)
                </Typography>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Block #</TableCell>
                        <TableCell>Timestamp</TableCell>
                        <TableCell>Event Type</TableCell>
                        <TableCell>Decision</TableCell>
                        <TableCell>Hash</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {blockchainAudit.map((block) => (
                        <TableRow key={block.index}>
                          <TableCell>{block.index}</TableCell>
                          <TableCell>{new Date(block.timestamp).toLocaleString()}</TableCell>
                          <TableCell>
                            <Chip label={block.data.eventType} size="small" />
                          </TableCell>
                          <TableCell>
                            {block.data.decision && (
                              <Chip
                                label={block.data.decision}
                                color={
                                  block.data.decision === 'APPROVE'
                                    ? 'success'
                                    : block.data.decision === 'REJECT'
                                    ? 'error'
                                    : 'warning'
                                }
                                size="small"
                              />
                            )}
                          </TableCell>
                          <TableCell>
                            <Typography variant="caption" sx={{ fontFamily: 'monospace' }}>
                              {block.hash.substring(0, 16)}...
                            </Typography>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Paper>
            </Grid>
          )}
        </Grid>
      </TabPanel>
    </Box>
  );
}
