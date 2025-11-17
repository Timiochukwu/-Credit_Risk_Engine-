import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

export default function AnalyticsPage() {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Analytics & Reporting
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography>Advanced analytics and reporting features...</Typography>
      </Paper>
    </Box>
  );
}
