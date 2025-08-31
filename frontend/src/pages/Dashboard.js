import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Alert,
  CircularProgress,
  Chip,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip,
  TextField,
  MenuItem,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  TrendingUp as TrendingUpIcon,
  Warning as WarningIcon,
  Security as SecurityIcon,
  Visibility as VisibilityIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { dashboardAPI, formatRiskScore } from '../services/api';
import toast from 'react-hot-toast';

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [flaggedContent, setFlaggedContent] = useState([]);
  const [trends, setTrends] = useState([]);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState('all');
  const [sortBy, setSortBy] = useState('date');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError('');

    try {
      const [statsResponse, flaggedResponse, trendsResponse] = await Promise.all([
        dashboardAPI.getStats(),
        dashboardAPI.getFlaggedContent(),
        dashboardAPI.getTrends()
      ]);

      if (statsResponse.success) {
        setStats(statsResponse.dashboard_stats);
      }

      if (flaggedResponse.success) {
        setFlaggedContent(flaggedResponse.flagged_content_data?.flagged_content || []);
      }

      if (trendsResponse.success) {
        setTrends(trendsResponse.trend_analysis || {});
      }
    } catch (err) {
      let errorMessage = 'Failed to load dashboard data';
      
      if (err.response?.data?.detail) {
        if (Array.isArray(err.response.data.detail)) {
          errorMessage = err.response.data.detail.map(e => e.msg || e).join(', ');
        } else {
          errorMessage = err.response.data.detail;
        }
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    fetchDashboardData();
    toast.success('Dashboard refreshed');
  };

  const getRiskColor = (score) => {
    const riskInfo = formatRiskScore(score);
    return riskInfo.color;
  };

  const getRiskLevel = (score) => {
    const riskInfo = formatRiskScore(score);
    return riskInfo.text;
  };

  const getFilteredContent = () => {
    let filtered = [...flaggedContent];

    if (filter === 'high-risk') {
      filtered = filtered.filter(item => item.risk_score >= 7);
    } else if (filter === 'medium-risk') {
      filtered = filtered.filter(item => item.risk_score >= 4 && item.risk_score < 7);
    } else if (filter === 'low-risk') {
      filtered = filtered.filter(item => item.risk_score < 4);
    }

    // Sort
    filtered.sort((a, b) => {
      if (sortBy === 'date') {
        return new Date(b.flagged_date) - new Date(a.flagged_date);
      } else if (sortBy === 'risk') {
        return b.risk_score - a.risk_score;
      }
      return 0;
    });

    return filtered;
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress size={60} />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Box>
          <Box display="flex" alignItems="center" gap={2} mb={1}>
            <DashboardIcon sx={{ fontSize: 40, color: 'primary.main' }} />
            <Typography variant="h3" component="h1" fontWeight="bold">
              Regulatory Dashboard
            </Typography>
          </Box>
          <Typography variant="h6" color="text.secondary">
            Monitor investment fraud patterns and trends
          </Typography>
        </Box>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={handleRefresh}
          disabled={loading}
        >
          Refresh
        </Button>
      </Box>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 4 }}>
          {error}
        </Alert>
      )}

      {/* Statistics Cards */}
      {stats && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="between">
                  <Box>
                    <Typography color="textSecondary" gutterBottom variant="body2">
                      Total Flagged Content
                    </Typography>
                    <Typography variant="h4" fontWeight="bold">
                      {stats.fraud_detection?.total_flagged_content?.toLocaleString() || '0'}
                    </Typography>
                  </Box>
                  <SecurityIcon color="primary" sx={{ fontSize: 40 }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="between">
                  <Box>
                    <Typography color="textSecondary" gutterBottom variant="body2">
                      High Risk Content
                    </Typography>
                    <Typography variant="h4" fontWeight="bold" color="error.main">
                      {stats.fraud_detection?.high_risk_content?.toLocaleString() || '0'}
                    </Typography>
                  </Box>
                  <WarningIcon color="error" sx={{ fontSize: 40 }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="between">
                  <Box>
                    <Typography color="textSecondary" gutterBottom variant="body2">
                      Avg Risk Score
                    </Typography>
                    <Typography variant="h4" fontWeight="bold">
                      {stats.fraud_detection?.average_risk_score?.toFixed(1) || '0.0'}
                    </Typography>
                  </Box>
                  <TrendingUpIcon color="warning" sx={{ fontSize: 40 }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="between">
                  <Box>
                    <Typography color="textSecondary" gutterBottom variant="body2">
                      Verified Advisors
                    </Typography>
                    <Typography variant="h4" fontWeight="bold" color="success.main">
                      {stats.advisor_verification?.active_advisors?.toLocaleString() || '0'}
                    </Typography>
                  </Box>
                  <SecurityIcon color="success" sx={{ fontSize: 40 }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Trends Section */}
      {trends && trends.fraud_type_trends && Object.keys(trends.fraud_type_trends).length > 0 && (
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Typography variant="h5" fontWeight="bold" gutterBottom>
              Fraud Trends & Patterns
            </Typography>
            <Grid container spacing={2}>
              {Object.entries(trends.fraud_type_trends).map(([fraudType, data], index) => {
                const totalCount = Object.values(data).reduce((sum, count) => sum + count, 0);
                return (
                  <Grid item xs={12} md={6} key={index}>
                    <Paper variant="outlined" sx={{ p: 2 }}>
                      <Typography variant="h6" gutterBottom>
                        {fraudType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Recent activity in this fraud category
                      </Typography>
                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Chip
                          label={`${totalCount} incidents`}
                          color="warning"
                          size="small"
                        />
                        <Typography variant="body2" color="text.secondary">
                          {totalCount > 0 ? '↗️ Active' : '➡️ Stable'}
                        </Typography>
                      </Box>
                    </Paper>
                  </Grid>
                );
              })}
            </Grid>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
              Monitoring period: {trends.period || '7 days'} ({trends.start_date} to {trends.end_date})
            </Typography>
          </CardContent>
        </Card>
      )}

      {/* Flagged Content Table */}
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
            <Typography variant="h5" fontWeight="bold">
              Recent Flagged Content
            </Typography>
            <Box display="flex" gap={2}>
              <TextField
                select
                size="small"
                label="Filter"
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                sx={{ minWidth: 120 }}
              >
                <MenuItem value="all">All Risk Levels</MenuItem>
                <MenuItem value="high-risk">High Risk</MenuItem>
                <MenuItem value="medium-risk">Medium Risk</MenuItem>
                <MenuItem value="low-risk">Low Risk</MenuItem>
              </TextField>
              
              <TextField
                select
                size="small"
                label="Sort by"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                sx={{ minWidth: 120 }}
              >
                <MenuItem value="date">Date</MenuItem>
                <MenuItem value="risk">Risk Score</MenuItem>
              </TextField>
            </Box>
          </Box>

          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Date</TableCell>
                  <TableCell>Content Type</TableCell>
                  <TableCell>Risk Score</TableCell>
                  <TableCell>Risk Level</TableCell>
                  <TableCell>Source</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {getFilteredContent().length > 0 ? (
                  getFilteredContent().map((item) => (
                    <TableRow key={item.id} hover>
                      <TableCell>
                        {new Date(item.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={item.fraud_type?.replace(/_/g, ' ') || 'Unknown'}
                          size="small"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        <Typography
                          fontWeight="bold"
                          sx={{ color: getRiskColor(item.risk_score) }}
                        >
                          {item.risk_score.toFixed(1)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={getRiskLevel(item.risk_score)}
                          size="small"
                          sx={{
                            backgroundColor: getRiskColor(item.risk_score),
                            color: 'white',
                          }}
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" noWrap>
                          {item.source || 'Unknown'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Box display="flex" gap={1}>
                          <Tooltip title="View Details">
                            <IconButton size="small" color="primary">
                              <VisibilityIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Download Report">
                            <IconButton size="small" color="secondary">
                              <DownloadIcon />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      <Typography variant="body2" color="text.secondary" py={4}>
                        No flagged content found
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Information Section */}
      <Alert severity="info" sx={{ mt: 4 }}>
        <Typography variant="h6" gutterBottom>
          Dashboard Features
        </Typography>
        <Typography variant="body2">
          • Real-time monitoring of fraud detection activities
          <br />
          • Statistical analysis of threat patterns and trends
          <br />
          • Risk assessment and classification of flagged content
          <br />
          • Export capabilities for regulatory reporting
          <br />
          • Advanced filtering and sorting options
        </Typography>
      </Alert>
    </Container>
  );
};

export default Dashboard;
