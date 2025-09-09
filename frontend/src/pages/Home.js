import React from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
  Paper,
} from '@mui/material';
import {
  Security as SecurityIcon,
  VerifiedUser as VerifiedUserIcon,
  Scanner as ScannerIcon,
  Dashboard as DashboardIcon,
  Shield as ShieldIcon,
} from '@mui/icons-material';
import { Link } from 'react-router-dom';

const features = [
  {
    title: 'Advisor Verification',
    description: 'Verify SEBI registration numbers and check advisor credentials against our comprehensive database.',
    icon: <VerifiedUserIcon sx={{ fontSize: 40 }} />,
    link: '/advisor-verification',
    color: '#3b82f6',
  },
  {
    title: 'Content Scanner',
    description: 'AI-powered detection of fraudulent investment content from social media and messaging apps.',
    icon: <ScannerIcon sx={{ fontSize: 40 }} />,
    link: '/content-scanner',
    color: '#10b981',
  },
  {
    title: 'Regulatory Dashboard',
    description: 'Real-time monitoring and trend analysis for regulators and financial institutions.',
    icon: <DashboardIcon sx={{ fontSize: 40 }} />,
    link: '/dashboard',
    color: '#f59e0b',
  },
];

const stats = [
  { label: 'Advisors Verified', value: '10,000+', color: '#3b82f6' },
  { label: 'Fraudulent Content Detected', value: '5,000+', color: '#ef4444' },
  { label: 'Users Protected', value: '50,000+', color: '#10b981' },
  { label: 'Detection Accuracy', value: '95%', color: '#8b5cf6' },
];

const Home = () => {
  return (
    <Box>
      {/* Hero Section */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, #1e293b 0%, #334155 50%, #475569 100%)',
          color: 'white',
          py: 8,
          position: 'relative',
          overflow: 'hidden',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'radial-gradient(circle at 30% 20%, rgba(59, 130, 246, 0.1) 0%, transparent 50%)',
            pointerEvents: 'none',
          }
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={6} alignItems="center">
            <Grid item xs={12} md={6}>
              <Typography variant="h2" component="h1" fontWeight="bold" gutterBottom>
                Protect Your Investments with
                <Box 
                  component="span" 
                  display="block" 
                  className="text-gradient"
                  sx={{ 
                    fontSize: { xs: '2.5rem', md: '3.75rem' },
                    lineHeight: 1.2,
                    fontWeight: 800,
                    background: 'linear-gradient(135deg, #60a5fa 0%, #a78bfa 50%, #fbbf24 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    backgroundClip: 'text',
                    textShadow: 'none',
                    filter: 'brightness(1.1) contrast(1.2)',
                  }}
                >
                  AI-Powered Fraud Detection
                </Box>
              </Typography>
              <Typography variant="h6" sx={{ mb: 4, opacity: 0.9 }}>
                InvestShield uses advanced AI and machine learning to detect investment fraud,
                verify advisor credentials, and protect retail investors from financial scams.
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Button
                  variant="contained"
                  size="large"
                  component={Link}
                  to="/content-scanner"
                  sx={{
                    backgroundColor: 'white',
                    color: 'primary.main',
                    '&:hover': {
                      backgroundColor: 'grey.100',
                    },
                  }}
                >
                  Start Scanning
                </Button>
                <Button
                  variant="outlined"
                  size="large"
                  component={Link}
                  to="/advisor-verification"
                  sx={{
                    borderColor: 'white',
                    color: 'white',
                    '&:hover': {
                      borderColor: 'white',
                      backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    },
                  }}
                >
                  Verify Advisor
                </Button>
              </Box>
            </Grid>
            <Grid item xs={12} md={6}>
              <Box
                sx={{
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  height: 300,
                }}
              >
                <SecurityIcon sx={{ fontSize: 200, opacity: 0.8 }} />
              </Box>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Features Section */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Typography
          variant="h3"
          component="h2"
          textAlign="center"
          fontWeight="bold"
          gutterBottom
        >
          Comprehensive Fraud Protection
        </Typography>
        <Typography
          variant="h6"
          textAlign="center"
          color="text.secondary"
          sx={{ mb: 6 }}
        >
          Multiple layers of protection to keep your investments safe
        </Typography>

        <Grid container spacing={4}>
          {features.map((feature, index) => (
            <Grid item xs={12} md={4} key={index}>
              <Card
                className="card-hover"
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  transition: 'all 0.3s ease',
                }}
              >
                <CardContent sx={{ flexGrow: 1, textAlign: 'center', pt: 4 }}>
                  <Box
                    sx={{
                      display: 'inline-flex',
                      p: 2,
                      borderRadius: '50%',
                      backgroundColor: `${feature.color}20`,
                      color: feature.color,
                      mb: 2,
                    }}
                  >
                    {feature.icon}
                  </Box>
                  <Typography variant="h5" component="h3" fontWeight="bold" gutterBottom>
                    {feature.title}
                  </Typography>
                  <Typography variant="body1" color="text.secondary">
                    {feature.description}
                  </Typography>
                </CardContent>
                <CardActions sx={{ justifyContent: 'center', pb: 3 }}>
                  <Button
                    variant="contained"
                    component={Link}
                    to={feature.link}
                    sx={{ 
                      backgroundColor: feature.color,
                      '&:hover': {
                        backgroundColor: feature.color,
                        filter: 'brightness(0.9)',
                        transform: 'translateY(-1px)',
                        boxShadow: '0 4px 8px rgba(0, 0, 0, 0.2)',
                      },
                    }}
                  >
                    Get Started
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* Stats Section */}
      <Box sx={{ backgroundColor: 'grey.50', py: 6 }}>
        <Container maxWidth="lg">
          <Typography
            variant="h4"
            component="h2"
            textAlign="center"
            fontWeight="bold"
            gutterBottom
          >
            Trusted by Thousands
          </Typography>
          <Grid container spacing={4} sx={{ mt: 2 }}>
            {stats.map((stat, index) => (
              <Grid item xs={6} md={3} key={index}>
                <Paper
                  elevation={0}
                  sx={{
                    p: 3,
                    textAlign: 'center',
                    backgroundColor: 'white',
                    borderRadius: 2,
                  }}
                >
                  <Typography
                    variant="h3"
                    component="div"
                    fontWeight="bold"
                    sx={{ color: stat.color }}
                  >
                    {stat.value}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {stat.label}
                  </Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* How It Works Section */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Typography
          variant="h3"
          component="h2"
          textAlign="center"
          fontWeight="bold"
          gutterBottom
        >
          How InvestShield Works
        </Typography>

        <Grid container spacing={6} sx={{ mt: 4 }}>
          <Grid item xs={12} md={4}>
            <Box textAlign="center">
              <Chip
                label="1"
                sx={{
                  width: 60,
                  height: 60,
                  fontSize: 20,
                  fontWeight: 'bold',
                  backgroundColor: 'primary.main',
                  color: 'white',
                  mb: 2,
                }}
              />
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Submit Content
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Paste suspicious investment content, advisor details, or URLs for analysis.
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12} md={4}>
            <Box textAlign="center">
              <Chip
                label="2"
                sx={{
                  width: 60,
                  height: 60,
                  fontSize: 20,
                  fontWeight: 'bold',
                  backgroundColor: 'secondary.main',
                  color: 'white',
                  mb: 2,
                }}
              />
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                AI Analysis
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Our AI models analyze patterns, keywords, and verify against official databases.
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12} md={4}>
            <Box textAlign="center">
              <Chip
                label="3"
                sx={{
                  width: 60,
                  height: 60,
                  fontSize: 20,
                  fontWeight: 'bold',
                  backgroundColor: 'success.main',
                  color: 'white',
                  mb: 2,
                }}
              />
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Get Results
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Receive detailed risk assessment and actionable recommendations.
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Container>

      {/* CTA Section */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, #ff6b6b 0%, #feca57 100%)',
          color: 'white',
          py: 6,
        }}
      >
        <Container maxWidth="md" textAlign="center">
          <ShieldIcon sx={{ fontSize: 60, mb: 2 }} />
          <Typography variant="h4" component="h2" fontWeight="bold" gutterBottom>
            Start Protecting Your Investments Today
          </Typography>
          <Typography variant="h6" sx={{ mb: 4, opacity: 0.9 }}>
            Join thousands of investors who trust InvestShield to keep their money safe.
          </Typography>
          <Button
            variant="contained"
            size="large"
            component={Link}
            to="/content-scanner"
            sx={{
              backgroundColor: 'white',
              color: 'text.primary',
              px: 4,
              py: 1.5,
              '&:hover': {
                backgroundColor: 'grey.100',
              },
            }}
          >
            Try InvestShield Now
          </Button>
        </Container>
      </Box>
    </Box>
  );
};

export default Home;
