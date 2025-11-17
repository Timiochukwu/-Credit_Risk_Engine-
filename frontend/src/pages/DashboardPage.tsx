import React, { useEffect, useState } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  CircularProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Assessment,
  AccountBalance,
  Warning,
  CheckCircle,
  Schedule,
} from '@mui/icons-material';
import { apiClient } from '../services/api';
import type { DashboardMetrics, EarlyWarningResult } from '../types';

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [warnings, setWarnings] = useState<EarlyWarningResult[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [metricsData, warningsData] = await Promise.all([
        apiClient.getDashboardMetrics(),
        apiClient.getEarlyWarnings(),
      ]);
      setMetrics(metricsData);
      setWarnings(warningsData);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !metrics) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  const metricCards = [
    {
      title: 'Total Applications',
      value: metrics.totalApplications.toLocaleString(),
      subtitle: `+${metrics.applicationsToday} today`,
      icon: <Assessment />,
      color: '#1976d2',
    },
    {
      title: 'Approval Rate',
      value: `${metrics.approvalRate}%`,
      subtitle: '+2.3% from last month',
      icon: <TrendingUp />,
      color: '#388e3c',
    },
    {
      title: 'Portfolio Value',
      value: `₦${(metrics.portfolioValue / 1000000000).toFixed(2)}B`,
      subtitle: '+8% growth',
      icon: <AccountBalance />,
      color: '#f57c00',
    },
    {
      title: 'NPL Ratio',
      value: `${metrics.nplRatio}%`,
      subtitle: '-0.5% improvement',
      icon: <TrendingDown />,
      color: metrics.nplRatio > 5 ? '#d32f2f' : '#388e3c',
    },
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom fontWeight={600}>
        Dashboard
      </Typography>

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
                <Typography variant="h4" fontWeight={600}>
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

      {/* Early Warnings */}
      {warnings.length > 0 && (
        <Paper sx={{ p: 3, mb: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Warning sx={{ color: '#f57c00', mr: 1 }} />
            <Typography variant="h6" fontWeight={600}>
              Early Warning Alerts
            </Typography>
          </Box>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Loan ID</TableCell>
                  <TableCell>Customer</TableCell>
                  <TableCell>Risk Level</TableCell>
                  <TableCell>Warning Score</TableCell>
                  <TableCell>Default Prob (3mo)</TableCell>
                  <TableCell>Action Required</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {warnings.map((warning) => (
                  <TableRow key={warning.loanId}>
                    <TableCell>{warning.loanId}</TableCell>
                    <TableCell>{warning.customerName}</TableCell>
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
                    <TableCell>{warning.warningScore}/100</TableCell>
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

      {/* Quick Stats */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom fontWeight={600}>
              Processing Metrics
            </Typography>
            <Box sx={{ mt: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Schedule sx={{ mr: 1, color: '#1976d2' }} />
                  <Typography>Avg Processing Time</Typography>
                </Box>
                <Typography fontWeight={600}>{metrics.avgProcessingTime}s</Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <CheckCircle sx={{ mr: 1, color: '#388e3c' }} />
                  <Typography>Pending Review</Typography>
                </Box>
                <Typography fontWeight={600}>{metrics.pendingReview}</Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom fontWeight={600}>
              System Status
            </Typography>
            <Box sx={{ mt: 2 }}>
              <Chip label="API: Online" color="success" sx={{ mr: 1, mb: 1 }} />
              <Chip label="Model: Loaded" color="success" sx={{ mr: 1, mb: 1 }} />
              <Chip label="Blockchain: Valid" color="success" sx={{ mr: 1, mb: 1 }} />
              <Chip label="Drift: Low" color="success" sx={{ mb: 1 }} />
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
