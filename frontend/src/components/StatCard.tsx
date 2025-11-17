import React from 'react';
import { Card, CardContent, Box, Typography, Skeleton } from '@mui/material';
import { TrendingUp, TrendingDown } from '@mui/icons-material';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  color?: string;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  loading?: boolean;
}

export default function StatCard({
  title,
  value,
  subtitle,
  icon,
  color = '#1565C0',
  trend,
  trendValue,
  loading = false,
}: StatCardProps) {
  if (loading) {
    return (
      <Card
        elevation={0}
        sx={{
          height: '100%',
          background: 'linear-gradient(135deg, #FFFFFF 0%, #F5F7FA 100%)',
          border: '1px solid',
          borderColor: 'divider',
        }}
      >
        <CardContent sx={{ p: 3 }}>
          <Skeleton variant="text" width="60%" height={24} />
          <Skeleton variant="text" width="40%" height={48} sx={{ mt: 2 }} />
          <Skeleton variant="text" width="50%" height={20} sx={{ mt: 1 }} />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card
      elevation={0}
      sx={{
        height: '100%',
        background: 'linear-gradient(135deg, #FFFFFF 0%, #F5F7FA 100%)',
        border: '1px solid',
        borderColor: 'divider',
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        '&:hover': {
          borderColor: color,
          boxShadow: `0px 8px 24px ${color}20`,
          transform: 'translateY(-4px)',
        },
      }}
    >
      <CardContent sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="subtitle2" color="text.secondary" fontWeight={600}>
            {title}
          </Typography>
          <Box
            sx={{
              width: 48,
              height: 48,
              borderRadius: 3,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              background: `linear-gradient(135deg, ${color}15 0%, ${color}05 100%)`,
              color: color,
            }}
          >
            {icon}
          </Box>
        </Box>

        <Typography
          variant="h3"
          fontWeight={700}
          sx={{
            background: `linear-gradient(135deg, ${color} 0%, ${color}80 100%)`,
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            mb: 1,
          }}
        >
          {value}
        </Typography>

        {(subtitle || trend) && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {trend && trendValue && (
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 0.5,
                  px: 1,
                  py: 0.5,
                  borderRadius: 1,
                  backgroundColor:
                    trend === 'up'
                      ? 'success.lighter'
                      : trend === 'down'
                      ? 'error.lighter'
                      : 'grey.100',
                }}
              >
                {trend === 'up' ? (
                  <TrendingUp sx={{ fontSize: 16, color: 'success.main' }} />
                ) : trend === 'down' ? (
                  <TrendingDown sx={{ fontSize: 16, color: 'error.main' }} />
                ) : null}
                <Typography
                  variant="caption"
                  fontWeight={600}
                  color={trend === 'up' ? 'success.main' : trend === 'down' ? 'error.main' : 'text.secondary'}
                >
                  {trendValue}
                </Typography>
              </Box>
            )}
            {subtitle && (
              <Typography variant="body2" color="text.secondary">
                {subtitle}
              </Typography>
            )}
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
