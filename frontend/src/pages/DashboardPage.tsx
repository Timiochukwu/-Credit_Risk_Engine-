import React from 'react';
import { Box, Grid, Paper, Typography, Card, CardContent } from '@mui/material';
import { TrendingUp, TrendingDown, Assessment, AccountBalance } from '@mui/icons-material';

export default function DashboardPage() {
  const metrics = [
    { title: 'Total Applications', value: '1,234', change: '+12%', icon: <Assessment />, color: '#1976d2' },
    { title: 'Approval Rate', value: '68.5%', change: '+2.3%', icon: <TrendingUp />, color: '#388e3c' },
    { title: 'Portfolio Value', value: '₦2.5B', change: '+8%', icon: <AccountBalance />, color: '#f57c00' },
    { title: 'NPL Ratio', value: '4.2%', change: '-0.5%', icon: <TrendingDown />, color: '#d32f2f' },
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      <Grid container spacing={3}>
        {metrics.map((metric) => (
          <Grid item xs={12} sm={6} md={3} key={metric.title}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Box sx={{ color: metric.color, mr: 1 }}>{metric.icon}</Box>
                  <Typography variant="h6">{metric.title}</Typography>
                </Box>
                <Typography variant="h4">{metric.value}</Typography>
                <Typography variant="body2" color="textSecondary">
                  {metric.change} from last month
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
      <Box sx={{ mt: 4 }}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Recent Applications
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Application list would appear here...
          </Typography>
        </Paper>
      </Box>
    </Box>
  );
}
