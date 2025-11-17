import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Alert,
  Divider,
  LinearProgress,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Warning,
  PieChart,
  BarChart,
  Assessment,
} from '@mui/icons-material';
import { apiClient } from '../services/api';
import type { PortfolioRisk, EarlyWarningResult } from '../types';

export default function PortfolioPage() {
  const [portfolioRisk, setPortfolioRisk] = useState<PortfolioRisk | null>(null);
  const [earlyWarnings, setEarlyWarnings] = useState<EarlyWarningResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchPortfolioData();
  }, []);

  const fetchPortfolioData = async () => {
    try {
      setLoading(true);
      const [riskData, warningsData] = await Promise.all([
        apiClient.getPortfolioRisk(),
        apiClient.getEarlyWarnings(),
      ]);
      setPortfolioRisk(riskData);
      setEarlyWarnings(warningsData);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load portfolio data');
    } finally {
      setLoading(false);
    }
  };

  if (loading || !portfolioRisk) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  const metricCards = [
    {
      title: 'Total Portfolio Value',
      value: `₦${(portfolioRisk.totalExposure / 1000000000).toFixed(2)}B`,
      subtitle: `${portfolioRisk.numberOfLoans} active loans`,
      icon: <TrendingUp />,
      color: '#1976d2',
    },
    {
      title: 'Expected Loss',
      value: `₦${(portfolioRisk.expectedLoss / 1000000).toFixed(2)}M`,
      subtitle: `${portfolioRisk.expectedLossRate}% of portfolio`,
      icon: <TrendingDown />,
      color: '#f57c00',
    },
    {
      title: 'Concentration Risk',
      value: portfolioRisk.concentrationRisk.maxSectorExposure,
      subtitle: `${portfolioRisk.concentrationRisk.topSector} sector`,
      icon: <PieChart />,
      color: '#9c27b0',
    },
    {
      title: 'Risk Rating',
      value: portfolioRisk.riskRating,
      subtitle: `Score: ${portfolioRisk.overallRiskScore}/100`,
      icon: <Assessment />,
      color: portfolioRisk.riskRating === 'HIGH' ? '#d32f2f' : portfolioRisk.riskRating === 'MEDIUM' ? '#f57c00' : '#388e3c',
    },
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom fontWeight={600}>
        Portfolio Management
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {metricCards.map((metric) => (
          <Grid item xs={12} sm={6} md={3} key={metric.title}>
            <Card elevation={2}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Box sx={{ color: metric.color, mr: 1 }}>{metric.icon}</Box>
                  <Typography variant="subtitle2" color="textSecondary">
                    {metric.title}
                  </Typography>
                </Box>
                <Typography variant="h5" fontWeight={600}>
                  {metric.value}
                </Typography>
                <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                  {metric.subtitle}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Concentration Risk */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <PieChart sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="h6" fontWeight={600}>
                Sector Concentration
              </Typography>
            </Box>
            <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
              Top Sector: <strong>{portfolioRisk.concentrationRisk.topSector}</strong>
            </Typography>
            <Box sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Exposure</Typography>
                <Typography variant="body2" fontWeight={600}>
                  {portfolioRisk.concentrationRisk.maxSectorExposure}
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={parseFloat(portfolioRisk.concentrationRisk.maxSectorExposure)}
                color={parseFloat(portfolioRisk.concentrationRisk.maxSectorExposure) > 40 ? 'error' : 'primary'}
                sx={{ height: 8, borderRadius: 1 }}
              />
            </Box>
            <Alert severity={parseFloat(portfolioRisk.concentrationRisk.maxSectorExposure) > 40 ? 'warning' : 'info'}>
              {parseFloat(portfolioRisk.concentrationRisk.maxSectorExposure) > 40
                ? 'High concentration risk - diversification recommended'
                : 'Concentration within acceptable limits'}
            </Alert>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <BarChart sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="h6" fontWeight={600}>
                Geographic Concentration
              </Typography>
            </Box>
            <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
              Top Region: <strong>{portfolioRisk.concentrationRisk.topRegion}</strong>
            </Typography>
            <Box sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Exposure</Typography>
                <Typography variant="body2" fontWeight={600}>
                  {portfolioRisk.concentrationRisk.maxRegionExposure}
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={parseFloat(portfolioRisk.concentrationRisk.maxRegionExposure)}
                color={parseFloat(portfolioRisk.concentrationRisk.maxRegionExposure) > 50 ? 'error' : 'primary'}
                sx={{ height: 8, borderRadius: 1 }}
              />
            </Box>
            <Alert severity={parseFloat(portfolioRisk.concentrationRisk.maxRegionExposure) > 50 ? 'warning' : 'info'}>
              {parseFloat(portfolioRisk.concentrationRisk.maxRegionExposure) > 50
                ? 'High geographic concentration - diversify regions'
                : 'Geographic distribution is healthy'}
            </Alert>
          </Paper>
        </Grid>
      </Grid>

      {/* Stress Testing */}
      {portfolioRisk.stressTesting && (
        <Paper sx={{ p: 3, mb: 4 }}>
          <Typography variant="h6" gutterBottom fontWeight={600}>
            Stress Testing Scenarios
          </Typography>
          <Divider sx={{ my: 2 }} />
          <Grid container spacing={3}>
            {portfolioRisk.stressTesting.scenarios.map((scenario, index) => (
              <Grid item xs={12} sm={6} md={4} key={index}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                      {scenario.scenario}
                    </Typography>
                    <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                      {scenario.description}
                    </Typography>
                    <Box sx={{ mb: 1 }}>
                      <Typography variant="caption" color="textSecondary">
                        Expected Loss Impact
                      </Typography>
                      <Typography variant="h6" color="error">
                        +₦{(scenario.expectedLossImpact / 1000000).toFixed(2)}M
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="caption" color="textSecondary">
                        Default Rate
                      </Typography>
                      <Typography variant="h6" color="warning.main">
                        {scenario.defaultRate}
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Paper>
      )}

      {/* Early Warnings */}
      {earlyWarnings.length > 0 && (
        <Paper sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Warning sx={{ color: '#f57c00', mr: 1 }} />
            <Typography variant="h6" fontWeight={600}>
              Early Warning System
            </Typography>
            <Chip
              label={`${earlyWarnings.length} at-risk loans`}
              color="warning"
              size="small"
              sx={{ ml: 2 }}
            />
          </Box>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Loan ID</TableCell>
                  <TableCell>Customer</TableCell>
                  <TableCell>Outstanding</TableCell>
                  <TableCell>Risk Level</TableCell>
                  <TableCell>Warning Score</TableCell>
                  <TableCell>Default Prob (3mo)</TableCell>
                  <TableCell>Recommended Action</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {earlyWarnings.map((warning) => (
                  <TableRow key={warning.loanId}>
                    <TableCell>{warning.loanId}</TableCell>
                    <TableCell>{warning.customerName}</TableCell>
                    <TableCell>₦{warning.outstandingBalance?.toLocaleString()}</TableCell>
                    <TableCell>
                      <Chip
                        label={warning.riskLevel}
                        color={
                          warning.riskLevel === 'CRITICAL' || warning.riskLevel === 'HIGH'
                            ? 'error'
                            : warning.riskLevel === 'MEDIUM'
                            ? 'warning'
                            : 'success'
                        }
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Typography variant="body2" sx={{ mr: 1 }}>
                          {warning.warningScore}/100
                        </Typography>
                        <LinearProgress
                          variant="determinate"
                          value={warning.warningScore}
                          color={warning.warningScore > 70 ? 'error' : warning.warningScore > 40 ? 'warning' : 'success'}
                          sx={{ width: 60, height: 6 }}
                        />
                      </Box>
                    </TableCell>
                    <TableCell>{(warning.defaultProbability3Months * 100).toFixed(1)}%</TableCell>
                    <TableCell>
                      <Typography variant="caption">{warning.intervention.actions[0]}</Typography>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      )}
    </Box>
  );
}
