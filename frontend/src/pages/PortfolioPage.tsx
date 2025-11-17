import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

export default function PortfolioPage() {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Portfolio Management
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography>Portfolio analytics and management features...</Typography>
      </Paper>
    </Box>
  );
}
