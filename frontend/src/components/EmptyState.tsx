import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import { Inbox } from '@mui/icons-material';

interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
}

export default function EmptyState({
  icon,
  title,
  description,
  actionLabel,
  onAction,
}: EmptyStateProps) {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        py: 8,
        px: 3,
        textAlign: 'center',
      }}
    >
      <Box
        sx={{
          width: 120,
          height: 120,
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: 'grey.100',
          color: 'grey.400',
          mb: 3,
        }}
      >
        {icon || <Inbox sx={{ fontSize: 64 }} />}
      </Box>

      <Typography variant="h5" fontWeight={600} gutterBottom>
        {title}
      </Typography>

      <Typography variant="body1" color="text.secondary" sx={{ mb: 3, maxWidth: 400 }}>
        {description}
      </Typography>

      {actionLabel && onAction && (
        <Button variant="contained" size="large" onClick={onAction}>
          {actionLabel}
        </Button>
      )}
    </Box>
  );
}
