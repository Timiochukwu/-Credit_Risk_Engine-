import React, { useEffect, useState } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Tooltip,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Assessment,
  AccountBalance,
  Warning,
  CheckCircle,
  Schedule,
  Refresh,
  MoreVert,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { apiClient } from '../services/api';
import type { DashboardMetrics, EarlyWarningResult } from '../types';
import StatCard from '../components/StatCard';
import EmptyState from '../components/EmptyState';

export default function DashboardPageEnhanced() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [warnings, setWarnings] = useState<EarlyWarningResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const isTablet = useMediaQuery(theme.breakpoints.down('md'));

  useEffect(() => {
    fetchDashboardData();
    // Auto-refresh every 60 seconds
    const interval = setInterval(fetchDashboardData, 60000);
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      if (metrics) setRefreshing(true);
      else setLoading(true);

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
      setRefreshing(false);
    }
  };

  // Mock data for charts (replace with actual API data)
  const applicationTrendData = [
    { month: 'Jan', applications: 450, approved: 320 },
    { month: 'Feb', applications: 520, approved: 380 },
    { month: 'Mar', applications: 610, approved: 450 },
    { month: 'Apr', applications: 580, approved: 420 },
    { month: 'May', applications: 720, approved: 550 },
    { month: 'Jun', applications: 850, approved: 650 },
  ];

  const riskDistributionData = [
    { name: 'Very Low', value: 35, color: '#4CAF50' },
    { name: 'Low', value: 28, color: '#8BC34A' },
    { name: 'Medium', value: 20, color: '#FF9800' },
    { name: 'High', value: 12, color: '#FF5722' },
    { name: 'Very High', value: 5, color: '#F44336' },
  ];

  const portfolioPerformanceData = [
    { quarter: 'Q1', npl: 2.8, target: 3.5 },
    { quarter: 'Q2', npl: 2.5, target: 3.5 },
    { quarter: 'Q3', npl: 2.2, target: 3.5 },
    { quarter: 'Q4', npl: 1.9, target: 3.5 },
  ];

  if (loading || !metrics) {
    return (
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
          <Typography variant="h4" fontWeight={700}>
            Dashboard
          </Typography>
        </Box>
        <Grid container spacing={3}>
          {[1, 2, 3, 4].map((i) => (
            <Grid item xs={12} sm={6} md={3} key={i}>
              <StatCard
                title="Loading..."
                value="---"
                icon={<Assessment />}
                loading={true}
              />
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header with Refresh */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 4,
          flexWrap: 'wrap',
          gap: 2,
        }}
      >
        <Box>
          <Typography variant="h4" fontWeight={700} gutterBottom>
            Dashboard
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Real-time credit risk analytics and portfolio insights
          </Typography>
        </Box>
        <Tooltip title="Refresh data">
          <IconButton
            onClick={fetchDashboardData}
            disabled={refreshing}
            sx={{
              backgroundColor: 'background.paper',
              boxShadow: 1,
              '&:hover': { backgroundColor: 'primary.lighter' },
            }}
          >
            <Refresh
              sx={{
                animation: refreshing ? 'spin 1s linear infinite' : 'none',
                '@keyframes spin': {
                  '0%': { transform: 'rotate(0deg)' },
                  '100%': { transform: 'rotate(360deg)' },
                },
              }}
            />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Key Metrics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Applications"
            value={metrics.totalApplications.toLocaleString()}
            subtitle={`+${metrics.applicationsToday} today`}
            icon={<Assessment />}
            color="#1565C0"
            trend="up"
            trendValue="+12.5%"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Approval Rate"
            value={`${metrics.approvalRate}%`}
            subtitle="vs 74.2% last month"
            icon={<TrendingUp />}
            color="#2E7D32"
            trend="up"
            trendValue="+2.3%"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Portfolio Value"
            value={`₦${(metrics.portfolioValue / 1000000000).toFixed(2)}B`}
            subtitle="Active loans"
            icon={<AccountBalance />}
            color="#F57C00"
            trend="up"
            trendValue="+8.1%"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="NPL Ratio"
            value={`${metrics.nplRatio}%`}
            subtitle="vs 5.2% target"
            icon={<TrendingDown />}
            color={metrics.nplRatio > 5 ? '#D32F2F' : '#2E7D32'}
            trend={metrics.nplRatio <= 3 ? 'down' : 'up'}
            trendValue={metrics.nplRatio <= 3 ? '-0.5%' : '+0.3%'}
          />
        </Grid>
      </Grid>

      {/* Charts Section */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Application Trend Chart */}
        <Grid item xs={12} lg={8}>
          <Paper
            sx={{
              p: 3,
              height: '100%',
              background: 'linear-gradient(135deg, #FFFFFF 0%, #F5F7FA 100%)',
            }}
          >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Box>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Application Trends
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Monthly application volume and approval rates
                </Typography>
              </Box>
              <Chip label="6 Months" size="small" color="primary" variant="outlined" />
            </Box>
            <ResponsiveContainer width="100%" height={isMobile ? 250 : 300}>
              <AreaChart data={applicationTrendData}>
                <defs>
                  <linearGradient id="applicationsGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#1565C0" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#1565C0" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="approvedGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#2E7D32" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#2E7D32" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#E0E0E0" />
                <XAxis dataKey="month" stroke="#5F6368" style={{ fontSize: 12 }} />
                <YAxis stroke="#5F6368" style={{ fontSize: 12 }} />
                <RechartsTooltip
                  contentStyle={{
                    backgroundColor: '#FFFFFF',
                    border: 'none',
                    borderRadius: 12,
                    boxShadow: '0px 4px 12px rgba(0,0,0,0.15)',
                  }}
                />
                <Legend wrapperStyle={{ fontSize: 14 }} />
                <Area
                  type="monotone"
                  dataKey="applications"
                  stroke="#1565C0"
                  strokeWidth={3}
                  fill="url(#applicationsGradient)"
                  name="Applications"
                />
                <Area
                  type="monotone"
                  dataKey="approved"
                  stroke="#2E7D32"
                  strokeWidth={3}
                  fill="url(#approvedGradient)"
                  name="Approved"
                />
              </AreaChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Risk Distribution Pie Chart */}
        <Grid item xs={12} lg={4}>
          <Paper
            sx={{
              p: 3,
              height: '100%',
              background: 'linear-gradient(135deg, #FFFFFF 0%, #F5F7FA 100%)',
            }}
          >
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Risk Distribution
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Portfolio by risk category
            </Typography>
            <ResponsiveContainer width="100%" height={isMobile ? 200 : 280}>
              <PieChart>
                <Pie
                  data={riskDistributionData}
                  cx="50%"
                  cy="50%"
                  innerRadius={isMobile ? 50 : 70}
                  outerRadius={isMobile ? 80 : 100}
                  paddingAngle={2}
                  dataKey="value"
                  label={(entry) => `${entry.value}%`}
                  labelLine={false}
                >
                  {riskDistributionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <RechartsTooltip
                  contentStyle={{
                    backgroundColor: '#FFFFFF',
                    border: 'none',
                    borderRadius: 12,
                    boxShadow: '0px 4px 12px rgba(0,0,0,0.15)',
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
            <Box sx={{ mt: 2, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {riskDistributionData.map((item) => (
                <Chip
                  key={item.name}
                  label={item.name}
                  size="small"
                  sx={{
                    backgroundColor: `${item.color}20`,
                    color: item.color,
                    fontWeight: 600,
                    borderColor: item.color,
                  }}
                  variant="outlined"
                />
              ))}
            </Box>
          </Paper>
        </Grid>

        {/* NPL Trend Chart */}
        <Grid item xs={12} md={6}>
          <Paper
            sx={{
              p: 3,
              background: 'linear-gradient(135deg, #FFFFFF 0%, #F5F7FA 100%)',
            }}
          >
            <Typography variant="h6" fontWeight={600} gutterBottom>
              NPL Performance
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Non-performing loan ratio vs target
            </Typography>
            <ResponsiveContainer width="100%" height={isMobile ? 200 : 240}>
              <LineChart data={portfolioPerformanceData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E0E0E0" />
                <XAxis dataKey="quarter" stroke="#5F6368" style={{ fontSize: 12 }} />
                <YAxis stroke="#5F6368" style={{ fontSize: 12 }} />
                <RechartsTooltip
                  contentStyle={{
                    backgroundColor: '#FFFFFF',
                    border: 'none',
                    borderRadius: 12,
                    boxShadow: '0px 4px 12px rgba(0,0,0,0.15)',
                  }}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="npl"
                  stroke="#2E7D32"
                  strokeWidth={3}
                  dot={{ r: 5, fill: '#2E7D32' }}
                  name="Actual NPL %"
                />
                <Line
                  type="monotone"
                  dataKey="target"
                  stroke="#9E9E9E"
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  dot={false}
                  name="Target %"
                />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Quick Stats */}
        <Grid item xs={12} md={6}>
          <Paper
            sx={{
              p: 3,
              height: '100%',
              background: 'linear-gradient(135deg, #FFFFFF 0%, #F5F7FA 100%)',
            }}
          >
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Processing Metrics
            </Typography>
            <Box sx={{ mt: 3, display: 'flex', flexDirection: 'column', gap: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                  <Box
                    sx={{
                      width: 40,
                      height: 40,
                      borderRadius: 2,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      backgroundColor: '#E3F2FD',
                    }}
                  >
                    <Schedule sx={{ color: '#1565C0' }} />
                  </Box>
                  <Typography variant="body1" fontWeight={500}>
                    Avg Processing Time
                  </Typography>
                </Box>
                <Typography variant="h6" fontWeight={700} color="primary">
                  {metrics.avgProcessingTime}s
                </Typography>
              </Box>

              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                  <Box
                    sx={{
                      width: 40,
                      height: 40,
                      borderRadius: 2,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      backgroundColor: '#E8F5E9',
                    }}
                  >
                    <CheckCircle sx={{ color: '#2E7D32' }} />
                  </Box>
                  <Typography variant="body1" fontWeight={500}>
                    Pending Review
                  </Typography>
                </Box>
                <Typography variant="h6" fontWeight={700} color="success.main">
                  {metrics.pendingReview}
                </Typography>
              </Box>

              <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
                <Typography variant="overline" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
                  System Status
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  <Chip label="API Online" color="success" size="small" icon={<CheckCircle />} />
                  <Chip label="Model Active" color="success" size="small" icon={<CheckCircle />} />
                  <Chip label="Blockchain OK" color="success" size="small" icon={<CheckCircle />} />
                  <Chip label="Low Drift" color="success" size="small" icon={<CheckCircle />} />
                </Box>
              </Box>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Early Warnings Table */}
      {warnings.length > 0 ? (
        <Paper sx={{ p: { xs: 2, md: 3 } }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 3, gap: 2 }}>
            <Box
              sx={{
                width: 48,
                height: 48,
                borderRadius: 3,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: '#FFF3E0',
              }}
            >
              <Warning sx={{ color: '#F57C00', fontSize: 28 }} />
            </Box>
            <Box sx={{ flex: 1 }}>
              <Typography variant="h6" fontWeight={600}>
                Early Warning Alerts
              </Typography>
              <Typography variant="body2" color="text.secondary">
                High-risk loans requiring immediate attention
              </Typography>
            </Box>
            <Chip label={`${warnings.length} Alerts`} color="warning" />
          </Box>

          {isMobile ? (
            // Mobile Card View
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {warnings.slice(0, 5).map((warning) => (
                <Paper
                  key={warning.loanId}
                  variant="outlined"
                  sx={{
                    p: 2,
                    borderLeft: 4,
                    borderLeftColor:
                      warning.riskLevel === 'CRITICAL' || warning.riskLevel === 'HIGH'
                        ? 'error.main'
                        : warning.riskLevel === 'MEDIUM'
                        ? 'warning.main'
                        : 'success.main',
                  }}
                >
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="subtitle2" fontWeight={600}>
                      {warning.loanId}
                    </Typography>
                    <Chip
                      label={warning.riskLevel}
                      size="small"
                      color={
                        warning.riskLevel === 'CRITICAL' || warning.riskLevel === 'HIGH'
                          ? 'error'
                          : warning.riskLevel === 'MEDIUM'
                          ? 'warning'
                          : 'success'
                      }
                    />
                  </Box>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {warning.customerName}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Default Prob: {(warning.defaultProbability3Months * 100).toFixed(1)}% | Score:{' '}
                    {warning.warningScore}/100
                  </Typography>
                </Paper>
              ))}
            </Box>
          ) : (
            // Desktop Table View
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
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {warnings.slice(0, 5).map((warning) => (
                    <TableRow key={warning.loanId} hover>
                      <TableCell>
                        <Typography variant="body2" fontWeight={600}>
                          {warning.loanId}
                        </Typography>
                      </TableCell>
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
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="body2" fontWeight={600}>
                            {warning.warningScore}/100
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography
                          variant="body2"
                          fontWeight={600}
                          color={warning.defaultProbability3Months > 0.5 ? 'error.main' : 'text.primary'}
                        >
                          {(warning.defaultProbability3Months * 100).toFixed(1)}%
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="caption" color="text.secondary">
                          {warning.intervention.actions[0]}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <IconButton size="small">
                          <MoreVert fontSize="small" />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </Paper>
      ) : (
        <Paper>
          <EmptyState
            icon={<CheckCircle sx={{ fontSize: 64, color: 'success.main' }} />}
            title="All Clear!"
            description="No early warning alerts at this time. Your portfolio is performing well."
          />
        </Paper>
      )}
    </Box>
  );
}
