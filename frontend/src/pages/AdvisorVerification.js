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
} from '@mui/material';
import {
  VerifiedUser as VerifiedUserIcon,
  Search as SearchIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { advisorAPI, formatRiskScore } from '../services/api';
import toast from 'react-hot-toast';

const AdvisorVerification = () => {
  const [searchType, setSearchType] = useState('sebi');
  const [searchValue, setSearchValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');

  const handleSearch = async () => {
    if (!searchValue.trim()) {
      toast.error('Please enter a search value');
      return;
    }

    setLoading(true);
    setError('');
    setResults(null);

    try {
      const searchData = searchType === 'sebi' 
        ? { sebi_number: searchValue.trim() }
        : { name: searchValue.trim() };

      const response = await advisorAPI.verify(searchData);
      
      if (response.success) {
        setResults(response.verification_result);
        
        if (response.verification_result.is_verified) {
          toast.success('Advisor verified successfully!');
        } else {
          toast.warning('Advisor verification failed');
        }
      } else {
        throw new Error('Verification failed');
      }
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Verification failed';
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

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box textAlign="center" mb={4}>
        <VerifiedUserIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
        <Typography variant="h3" component="h1" fontWeight="bold" gutterBottom>
          Advisor Verification
        </Typography>
        <Typography variant="h6" color="text.secondary">
          Verify SEBI registration and check advisor credentials
        </Typography>
      </Box>

      {/* Search Form */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Search for Advisor
          </Typography>
          
          <Grid container spacing={3} alignItems="end">
            <Grid item xs={12} md={3}>
              <TextField
                select
                fullWidth
                label="Search Type"
                value={searchType}
                onChange={(e) => setSearchType(e.target.value)}
                SelectProps={{
                  native: true,
                }}
              >
                <option value="sebi">SEBI Number</option>
                <option value="name">Advisor Name</option>
              </TextField>
            </Grid>
            
            <Grid item xs={12} md={7}>
              <TextField
                fullWidth
                label={searchType === 'sebi' ? 'Enter SEBI Registration Number' : 'Enter Advisor Name'}
                placeholder={searchType === 'sebi' ? 'e.g., INA000001234' : 'e.g., Rajesh Kumar'}
                value={searchValue}
                onChange={(e) => setSearchValue(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
            </Grid>
            
            <Grid item xs={12} md={2}>
              <Button
                fullWidth
                variant="contained"
                startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <SearchIcon />}
                onClick={handleSearch}
                disabled={loading}
                sx={{ height: 56 }}
              >
                {loading ? 'Searching...' : 'Search'}
              </Button>
            </Grid>
          </Grid>

          {searchType === 'sebi' && (
            <Alert severity="info" sx={{ mt: 2 }}>
              <Typography variant="body2">
                SEBI registration numbers follow the format: INA followed by 9 digits (e.g., INA000001234)
              </Typography>
            </Alert>
          )}
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
                Verification Results
              </Typography>
              <Box display="flex" alignItems="center" gap={2}>
                {results.is_verified ? (
                  <Chip
                    icon={<CheckCircleIcon />}
                    label="VERIFIED"
                    color="success"
                    variant="outlined"
                  />
                ) : (
                  <Chip
                    icon={<ErrorIcon />}
                    label="NOT VERIFIED"
                    color="error"
                    variant="outlined"
                  />
                )}
                <Chip
                  label={`Risk Score: ${results.risk_score.toFixed(1)}`}
                  sx={{
                    backgroundColor: getRiskColor(results.risk_score),
                    color: 'white',
                    fontWeight: 'bold',
                  }}
                />
              </Box>
            </Box>

            <Divider sx={{ mb: 3 }} />

            {results.advisor_details ? (
              <Grid container spacing={3}>
                {/* Advisor Details */}
                <Grid item xs={12} md={8}>
                  <Typography variant="h6" gutterBottom>
                    Advisor Information
                  </Typography>
                  
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <Paper variant="outlined" sx={{ p: 2 }}>
                        <Typography variant="body2" color="text.secondary">
                          SEBI Number
                        </Typography>
                        <Typography variant="body1" fontWeight="bold">
                          {results.advisor_details.sebi_number}
                        </Typography>
                      </Paper>
                    </Grid>
                    
                    <Grid item xs={12} sm={6}>
                      <Paper variant="outlined" sx={{ p: 2 }}>
                        <Typography variant="body2" color="text.secondary">
                          Name
                        </Typography>
                        <Typography variant="body1" fontWeight="bold">
                          {results.advisor_details.name}
                        </Typography>
                      </Paper>
                    </Grid>
                    
                    <Grid item xs={12} sm={6}>
                      <Paper variant="outlined" sx={{ p: 2 }}>
                        <Typography variant="body2" color="text.secondary">
                          Firm Name
                        </Typography>
                        <Typography variant="body1" fontWeight="bold">
                          {results.advisor_details.firm_name}
                        </Typography>
                      </Paper>
                    </Grid>
                    
                    <Grid item xs={12} sm={6}>
                      <Paper variant="outlined" sx={{ p: 2 }}>
                        <Typography variant="body2" color="text.secondary">
                          Status
                        </Typography>
                        <Chip
                          label={results.advisor_details.status}
                          color={results.advisor_details.status === 'Active' ? 'success' : 'error'}
                          size="small"
                        />
                      </Paper>
                    </Grid>
                    
                    <Grid item xs={12} sm={6}>
                      <Paper variant="outlined" sx={{ p: 2 }}>
                        <Typography variant="body2" color="text.secondary">
                          Location
                        </Typography>
                        <Typography variant="body1" fontWeight="bold">
                          {results.advisor_details.location}
                        </Typography>
                      </Paper>
                    </Grid>
                    
                    <Grid item xs={12} sm={6}>
                      <Paper variant="outlined" sx={{ p: 2 }}>
                        <Typography variant="body2" color="text.secondary">
                          Specialization
                        </Typography>
                        <Typography variant="body1" fontWeight="bold">
                          {results.advisor_details.specialization}
                        </Typography>
                      </Paper>
                    </Grid>
                    
                    <Grid item xs={12} sm={6}>
                      <Paper variant="outlined" sx={{ p: 2 }}>
                        <Typography variant="body2" color="text.secondary">
                          Registration Date
                        </Typography>
                        <Typography variant="body1" fontWeight="bold">
                          {new Date(results.advisor_details.registration_date).toLocaleDateString()}
                        </Typography>
                      </Paper>
                    </Grid>
                    
                    <Grid item xs={12} sm={6}>
                      <Paper variant="outlined" sx={{ p: 2 }}>
                        <Typography variant="body2" color="text.secondary">
                          Validity Date
                        </Typography>
                        <Typography variant="body1" fontWeight="bold">
                          {new Date(results.advisor_details.validity_date).toLocaleDateString()}
                        </Typography>
                      </Paper>
                    </Grid>
                  </Grid>
                </Grid>

                {/* Risk Assessment */}
                <Grid item xs={12} md={4}>
                  <Typography variant="h6" gutterBottom>
                    Risk Assessment
                  </Typography>
                  
                  <Paper 
                    variant="outlined" 
                    sx={{ 
                      p: 3, 
                      textAlign: 'center',
                      backgroundColor: `${getRiskColor(results.risk_score)}10`
                    }}
                  >
                    <Typography variant="h3" fontWeight="bold" sx={{ color: getRiskColor(results.risk_score) }}>
                      {results.risk_score.toFixed(1)}
                    </Typography>
                    <Typography variant="h6" sx={{ color: getRiskColor(results.risk_score) }}>
                      {getRiskLevel(results.risk_score)}
                    </Typography>
                  </Paper>

                  <Typography variant="h6" sx={{ mt: 3, mb: 2 }}>
                    Recommendations
                  </Typography>
                  
                  <List dense>
                    {results.recommendations.map((recommendation, index) => (
                      <ListItem key={index} sx={{ px: 0 }}>
                        <ListItemIcon>
                          <InfoIcon color="primary" />
                        </ListItemIcon>
                        <ListItemText 
                          primary={recommendation}
                          primaryTypographyProps={{ variant: 'body2' }}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Grid>
              </Grid>
            ) : (
              // Not Found or Multiple Matches
              <Box>
                <Alert severity="warning" sx={{ mb: 3 }}>
                  <Typography variant="body1">
                    {results.message}
                  </Typography>
                </Alert>

                {results.matches && (
                  <Box>
                    <Typography variant="h6" gutterBottom>
                      Multiple Matches Found
                    </Typography>
                    <Grid container spacing={2}>
                      {results.matches.map((match, index) => (
                        <Grid item xs={12} md={6} key={index}>
                          <Paper variant="outlined" sx={{ p: 2 }}>
                            <Typography variant="body1" fontWeight="bold">
                              {match.name}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              {match.sebi_number}
                            </Typography>
                            <Typography variant="body2">
                              {match.firm_name}
                            </Typography>
                          </Paper>
                        </Grid>
                      ))}
                    </Grid>
                  </Box>
                )}

                <Typography variant="h6" sx={{ mt: 3, mb: 2 }}>
                  Recommendations
                </Typography>
                
                <List dense>
                  {results.recommendations.map((recommendation, index) => (
                    <ListItem key={index} sx={{ px: 0 }}>
                      <ListItemIcon>
                        <WarningIcon color="warning" />
                      </ListItemIcon>
                      <ListItemText 
                        primary={recommendation}
                        primaryTypographyProps={{ variant: 'body2' }}
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}
          </CardContent>
        </Card>
      )}

      {/* Information Section */}
      {!results && (
        <Alert severity="info" sx={{ mt: 4 }}>
          <Typography variant="h6" gutterBottom>
            About Advisor Verification
          </Typography>
          <Typography variant="body2">
            • Verify SEBI registration status and validity
            <br />
            • Check advisor credentials and background
            <br />
            • Get risk assessment and recommendations
            <br />
            • Protect yourself from fake advisors and scams
          </Typography>
        </Alert>
      )}
    </Container>
  );
};

export default AdvisorVerification;
