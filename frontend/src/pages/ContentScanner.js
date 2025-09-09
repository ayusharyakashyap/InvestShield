import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Grid,
  Alert,
  CircularProgress,
  Chip,
  Divider,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Tab,
  Tabs,
} from '@mui/material';
import {
  TextSnippet as TextSnippetIcon,
  Link as LinkIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Search as SearchIcon,
  TrendingUp as TrendingUpIcon,
} from '@mui/icons-material';
import { scannerAPI, formatRiskScore } from '../services/api';
import toast from 'react-hot-toast';

const ContentScanner = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [content, setContent] = useState('');
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');

  const handleAnalyze = async () => {
    const isTextTab = activeTab === 0;
    const inputValue = isTextTab ? content : url;

    if (!inputValue.trim()) {
      toast.error(`Please enter ${isTextTab ? 'content' : 'a URL'} to analyze`);
      return;
    }

    setLoading(true);
    setError('');
    setResults(null);

    try {
      const requestData = isTextTab 
        ? { text: inputValue.trim() }
        : { url: inputValue.trim(), source: 'web' };

      const response = isTextTab 
        ? await scannerAPI.analyze(requestData)
        : await scannerAPI.analyzeUrl(requestData);
      
      if (response.success) {
        setResults(response.analysis);
        
        const riskScore = response.analysis.risk_score;
        if (riskScore >= 70) {
          toast.error('High risk content detected!');
        } else if (riskScore >= 40) {
          toast('⚠️ Medium risk content detected', {
            icon: '⚠️',
            style: {
              borderRadius: '10px',
              background: '#ff9800',
              color: '#fff',
            },
          });
        } else {
          toast.success('Content appears safe');
        }
      } else {
        throw new Error('Analysis failed');
      }
    } catch (err) {
      let errorMessage = 'Analysis failed';
      
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

  const getRiskColor = (score) => {
    const riskInfo = formatRiskScore(score);
    return riskInfo.color;
  };

  const getRiskLevel = (score) => {
    const riskInfo = formatRiskScore(score);
    return riskInfo.text;
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return '#4caf50';
    if (confidence >= 0.6) return '#ff9800';
    return '#f44336';
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box textAlign="center" mb={4}>
        <TrendingUpIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2, transform: 'rotate(45deg)' }} />
        <Typography variant="h3" component="h1" fontWeight="bold" gutterBottom>
          Content Scanner
        </Typography>
        <Typography variant="h6" color="text.secondary">
          Analyze suspicious content and detect potential investment scams
        </Typography>
      </Box>

      {/* Input Form */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Tabs 
            value={activeTab} 
            onChange={(e, newValue) => setActiveTab(newValue)}
            sx={{ mb: 3 }}
          >
            <Tab 
              icon={<TextSnippetIcon />} 
              label="Analyze Text" 
              iconPosition="start"
            />
            <Tab 
              icon={<LinkIcon />} 
              label="Analyze URL" 
              iconPosition="start"
            />
          </Tabs>

          {activeTab === 0 ? (
            // Text Analysis Tab
            <Box>
              <Typography variant="h6" gutterBottom>
                Enter Content to Analyze
              </Typography>
              <TextField
                fullWidth
                multiline
                rows={8}
                label="Paste content here..."
                placeholder="Enter investment advice, social media posts, messages, or any content you want to analyze for fraud indicators..."
                value={content}
                onChange={(e) => setContent(e.target.value)}
                sx={{ mb: 3 }}
              />
              <Alert severity="info" sx={{ mb: 3 }}>
                <Typography variant="body2">
                  Our AI analyzes text for fraud indicators including guaranteed returns, urgency tactics, 
                  fake testimonials, and other suspicious patterns commonly used in investment scams.
                </Typography>
              </Alert>
            </Box>
          ) : (
            // URL Analysis Tab
            <Box>
              <Typography variant="h6" gutterBottom>
                Enter URL to Analyze
              </Typography>
              <TextField
                fullWidth
                label="Enter website URL"
                placeholder="https://example.com/investment-opportunity"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                sx={{ mb: 3 }}
              />
              <Alert severity="info" sx={{ mb: 3 }}>
                <Typography variant="body2">
                  Enter the URL of a website, social media post, or investment platform. 
                  We'll analyze the content for potential fraud indicators and suspicious patterns.
                </Typography>
              </Alert>
            </Box>
          )}

          <Button
            variant="contained"
            size="large"
            startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <SearchIcon />}
            onClick={handleAnalyze}
            disabled={loading}
            fullWidth
          >
            {loading ? 'Analyzing Content...' : 'Analyze Content'}
          </Button>
        </CardContent>
      </Card>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 4 }}>
          {error}
        </Alert>
      )}

      {/* Results */}
      {results && (
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between" mb={3}>
              <Typography variant="h5" fontWeight="bold">
                Analysis Results
              </Typography>
              <Box display="flex" alignItems="center" gap={2}>
                <Chip
                  label={`Risk Score: ${results.risk_score.toFixed(1)}`}
                  sx={{
                    backgroundColor: getRiskColor(results.risk_score),
                    color: 'white',
                    fontWeight: 'bold',
                  }}
                />
                <Chip
                  label={getRiskLevel(results.risk_score)}
                  variant="outlined"
                  color={results.risk_score >= 60 ? 'error' : results.risk_score >= 40 ? 'warning' : 'success'}
                />
              </Box>
            </Box>

            <Divider sx={{ mb: 3 }} />

            <Grid container spacing={3}>
              {/* Risk Assessment */}
              <Grid item xs={12} md={4}>
                <Paper 
                  variant="outlined" 
                  sx={{ 
                    p: 3, 
                    textAlign: 'center',
                    backgroundColor: `${getRiskColor(results.risk_score)}10`
                  }}
                >
                  <Typography variant="h2" fontWeight="bold" sx={{ color: getRiskColor(results.risk_score) }}>
                    {results.risk_score.toFixed(1)}
                  </Typography>
                  <Typography variant="h6" sx={{ color: getRiskColor(results.risk_score) }}>
                    {getRiskLevel(results.risk_score)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    Risk Score (0-100)
                  </Typography>
                </Paper>

                {/* Analysis Status */}
                <Paper variant="outlined" sx={{ p: 2, mt: 2 }}>
                  <Typography variant="h6" gutterBottom>
                    Analysis Status
                  </Typography>
                  <Chip
                    label={results.is_suspicious ? 'SUSPICIOUS' : 'LEGITIMATE'}
                    color={results.is_suspicious ? 'error' : 'success'}
                    sx={{ mb: 1 }}
                  />
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    Fraud Type: {results.fraud_type || 'N/A'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Confidence: {results.confidence_score?.toFixed(1) || 'N/A'}%
                  </Typography>
                </Paper>
              </Grid>

              {/* Analysis Details */}
              <Grid item xs={12} md={8}>
                <Typography variant="h6" gutterBottom>
                  Detailed Analysis
                </Typography>
                
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Paper variant="outlined" sx={{ p: 2 }}>
                      <Typography variant="body2" color="text.secondary">
                        Keywords Found
                      </Typography>
                      <Typography variant="h6" fontWeight="bold">
                        {results.keywords_found?.length || 0}
                      </Typography>
                    </Paper>
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <Paper variant="outlined" sx={{ p: 2 }}>
                      <Typography variant="body2" color="text.secondary">
                        Confidence Score
                      </Typography>
                      <Typography variant="h6" fontWeight="bold">
                        {results.confidence_score?.toFixed(1) || 'N/A'}%
                      </Typography>
                    </Paper>
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <Paper variant="outlined" sx={{ p: 2 }}>
                      <Typography variant="body2" color="text.secondary">
                        Analysis Status
                      </Typography>
                      <Typography variant="h6" fontWeight="bold">
                        {results.is_suspicious ? 'Suspicious' : 'Legitimate'}
                      </Typography>
                    </Paper>
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <Paper variant="outlined" sx={{ p: 2 }}>
                      <Typography variant="body2" color="text.secondary">
                        Fraud Type
                      </Typography>
                      <Typography variant="h6" fontWeight="bold">
                        {results.fraud_type || 'N/A'}
                      </Typography>
                    </Paper>
                  </Grid>
                </Grid>

                {/* Keywords Found */}
                {results.keywords_found && results.keywords_found.length > 0 && (
                  <Box sx={{ mt: 3 }}>
                    <Typography variant="h6" gutterBottom>
                      Suspicious Keywords Detected
                    </Typography>
                    <Box display="flex" flexWrap="wrap" gap={1}>
                      {results.keywords_found.map((keyword, index) => (
                        <Chip
                          key={index}
                          label={keyword}
                          color="error"
                          variant="outlined"
                          size="small"
                        />
                      ))}
                    </Box>
                  </Box>
                )}

                {/* Explanation */}
                {results.explanation && (
                  <Box sx={{ mt: 3 }}>
                    <Typography variant="h6" gutterBottom>
                      Analysis Explanation
                    </Typography>
                    <Paper variant="outlined" sx={{ p: 2 }}>
                      <Typography variant="body2">
                        {results.explanation}
                      </Typography>
                    </Paper>
                  </Box>
                )}

                {/* Recommendations */}
                <Box sx={{ mt: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Recommendations
                  </Typography>
                  <List dense>
                    {(results.recommendations || []).map((recommendation, index) => (
                      <ListItem key={index} sx={{ px: 0 }}>
                        <ListItemIcon>
                          {results.risk_score >= 60 ? (
                            <ErrorIcon color="error" />
                          ) : results.risk_score >= 40 ? (
                            <WarningIcon color="warning" />
                          ) : (
                            <CheckCircleIcon color="success" />
                          )}
                        </ListItemIcon>
                        <ListItemText 
                          primary={recommendation}
                          primaryTypographyProps={{ variant: 'body2' }}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Information Section */}
      {!results && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <WarningIcon color="error" sx={{ fontSize: 40, mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Fraud Detection
                </Typography>
                <Typography variant="body2">
                  Advanced AI algorithms detect common fraud patterns, suspicious keywords, 
                  and manipulation tactics used in investment scams.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <TrendingUpIcon color="primary" sx={{ fontSize: 40, mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Risk Scoring
                </Typography>
                <Typography variant="body2">
                  Get a comprehensive risk score from 0-10 based on multiple factors 
                  including keywords, sentiment, urgency, and ML predictions.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <CheckCircleIcon color="success" sx={{ fontSize: 40, mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Actionable Insights
                </Typography>
                <Typography variant="body2">
                  Receive detailed recommendations and insights to help you make 
                  informed decisions about investment opportunities.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </Container>
  );
};

export default ContentScanner;
