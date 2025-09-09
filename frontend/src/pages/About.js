import React from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Avatar,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Paper,
  Button,
} from '@mui/material';
import {
  Security as SecurityIcon,
  Psychology as PsychologyIcon,
  VerifiedUser as VerifiedUserIcon,
  Dashboard as DashboardIcon,
  Code as CodeIcon,
  Storage as StorageIcon,
  Cloud as CloudIcon,
  Speed as SpeedIcon,
  CheckCircle as CheckCircleIcon,
  GitHub as GitHubIcon,
  Email as EmailIcon,
  LinkedIn as LinkedInIcon,
} from '@mui/icons-material';

const About = () => {
  const features = [
    {
      icon: <VerifiedUserIcon color="primary" />,
      title: 'SEBI Advisor Verification',
      description: 'Real-time verification of investment advisors against official SEBI database with risk assessment.'
    },
    {
      icon: <PsychologyIcon color="secondary" />,
      title: 'AI-Powered Fraud Detection',
      description: 'Advanced machine learning models to detect suspicious patterns and fraudulent content.'
    },
    {
      icon: <SecurityIcon color="error" />,
      title: 'Content Analysis',
      description: 'Comprehensive analysis of text and URLs for fraud indicators and manipulation tactics.'
    },
    {
      icon: <DashboardIcon color="success" />,
      title: 'Regulatory Dashboard',
      description: 'Real-time monitoring and analytics for regulatory authorities and compliance teams.'
    }
  ];

  const techStack = [
    { category: 'Backend', technologies: ['Python', 'FastAPI', 'SQLAlchemy', 'SQLite'], icon: <CodeIcon /> },
    { category: 'AI/ML', technologies: ['scikit-learn', 'spaCy', 'TF-IDF', 'Random Forest'], icon: <PsychologyIcon /> },
    { category: 'Frontend', technologies: ['React.js', 'Material-UI', 'React Router', 'Axios'], icon: <CodeIcon /> },
    { category: 'Database', technologies: ['SQLite', 'Alembic', 'ORM Models'], icon: <StorageIcon /> },
    { category: 'Deployment', technologies: ['Docker', 'Docker Compose', 'uvicorn'], icon: <CloudIcon /> },
  ];

  const capabilities = [
    'Real-time advisor verification against SEBI database',
    'ML-based fraud classification with high accuracy',
    'Keyword-based suspicious content detection',
    'Sentiment analysis and urgency pattern recognition',
    'Risk scoring algorithm with actionable insights',
    'Regulatory dashboard with trend analysis',
    'RESTful API for easy integration',
    'Scalable and modular architecture'
  ];

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box textAlign="center" mb={6}>
        <SecurityIcon sx={{ fontSize: 80, color: 'primary.main', mb: 2 }} />
        <Typography variant="h2" component="h1" fontWeight="bold" gutterBottom>
          InvestShield
        </Typography>
        <Typography variant="h5" color="text.secondary" gutterBottom>
          AI-Powered Investor Fraud Detection Tool
        </Typography>
        <Typography variant="body1" sx={{ maxWidth: 800, mx: 'auto', mt: 2 }}>
          A comprehensive solution designed to protect investors from fraudulent schemes 
          and unauthorized investment advisors using advanced artificial intelligence and 
          real-time verification systems.
        </Typography>
      </Box>

      {/* Mission Statement */}
      <Card sx={{ mb: 6, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
        <CardContent sx={{ py: 4 }}>
          <Typography variant="h4" fontWeight="bold" textAlign="center" gutterBottom>
            Our Mission
          </Typography>
          <Typography variant="h6" textAlign="center" sx={{ opacity: 0.9 }}>
            To democratize investor protection through AI-powered fraud detection, 
            making financial markets safer and more transparent for everyone.
          </Typography>
        </CardContent>
      </Card>

      {/* Key Features */}
      <Box mb={6}>
        <Typography variant="h4" fontWeight="bold" textAlign="center" gutterBottom>
          Key Features
        </Typography>
        <Grid container spacing={3} sx={{ mt: 2 }}>
          {features.map((feature, index) => (
            <Grid item xs={12} md={6} key={index}>
              <Card sx={{ height: '100%', transition: 'transform 0.2s', '&:hover': { transform: 'translateY(-4px)' } }}>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={2}>
                    <Avatar sx={{ mr: 2, bgcolor: 'background.paper' }}>
                      {feature.icon}
                    </Avatar>
                    <Typography variant="h6" fontWeight="bold">
                      {feature.title}
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    {feature.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* Technology Stack */}
      <Box mb={6}>
        <Typography variant="h4" fontWeight="bold" textAlign="center" gutterBottom>
          Technology Stack
        </Typography>
        <Grid container spacing={3} sx={{ mt: 2 }}>
          {techStack.map((tech, index) => (
            <Grid item xs={12} md={4} key={index}>
              <Paper variant="outlined" sx={{ p: 3, height: '100%' }}>
                <Box display="flex" alignItems="center" mb={2}>
                  {tech.icon}
                  <Typography variant="h6" fontWeight="bold" sx={{ ml: 1 }}>
                    {tech.category}
                  </Typography>
                </Box>
                <Box display="flex" flexWrap="wrap" gap={1}>
                  {tech.technologies.map((technology, techIndex) => (
                    <Chip
                      key={techIndex}
                      label={technology}
                      variant="outlined"
                      size="small"
                    />
                  ))}
                </Box>
              </Paper>
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* System Capabilities */}
      <Grid container spacing={4} sx={{ mb: 6 }}>
        <Grid item xs={12} md={6}>
          <Typography variant="h4" fontWeight="bold" gutterBottom>
            System Capabilities
          </Typography>
          <List>
            {capabilities.map((capability, index) => (
              <ListItem key={index} sx={{ px: 0 }}>
                <ListItemIcon>
                  <CheckCircleIcon color="success" />
                </ListItemIcon>
                <ListItemText primary={capability} />
              </ListItem>
            ))}
          </List>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Typography variant="h4" fontWeight="bold" gutterBottom>
            Performance Metrics
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Paper variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                <SpeedIcon color="primary" sx={{ fontSize: 40, mb: 1 }} />
                <Typography variant="h6" fontWeight="bold">
                  &lt; 200ms
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Average API Response Time
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={6}>
              <Paper variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h6" fontWeight="bold" color="success.main">
                  95%+
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Fraud Detection Accuracy
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={6}>
              <Paper variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h6" fontWeight="bold" color="primary.main">
                  1000+
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Daily Scans Supported
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        </Grid>
      </Grid>

      {/* Architecture Overview */}
      <Card sx={{ mb: 6 }}>
        <CardContent>
          <Typography variant="h4" fontWeight="bold" textAlign="center" gutterBottom>
            System Architecture
          </Typography>
          <Divider sx={{ my: 3 }} />
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Box textAlign="center">
                <CodeIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
                <Typography variant="h6" fontWeight="bold" gutterBottom>
                  Frontend Layer
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  React.js application with Material-UI components providing 
                  intuitive user interface for all stakeholders.
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box textAlign="center">
                <SecurityIcon sx={{ fontSize: 60, color: 'secondary.main', mb: 2 }} />
                <Typography variant="h6" fontWeight="bold" gutterBottom>
                  API Layer
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  FastAPI backend with RESTful endpoints handling 
                  authentication, verification, and analysis requests.
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box textAlign="center">
                <PsychologyIcon sx={{ fontSize: 60, color: 'error.main', mb: 2 }} />
                <Typography variant="h6" fontWeight="bold" gutterBottom>
                  AI/ML Engine
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Machine learning models for fraud detection, pattern recognition, 
                  and risk assessment with continuous learning capabilities.
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Use Cases */}
      <Box mb={6}>
        <Typography variant="h4" fontWeight="bold" textAlign="center" gutterBottom>
          Use Cases
        </Typography>
        <Grid container spacing={3} sx={{ mt: 2 }}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight="bold" gutterBottom>
                  For Individual Investors
                </Typography>
                <List dense>
                  <ListItem>
                    <ListItemText primary="Verify advisor credentials before investing" />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="Analyze suspicious investment opportunities" />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="Get risk assessments for social media content" />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="Protect against Ponzi schemes and scams" />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight="bold" gutterBottom>
                  For Regulatory Bodies
                </Typography>
                <List dense>
                  <ListItem>
                    <ListItemText primary="Monitor market fraud patterns in real-time" />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="Track unauthorized investment advisors" />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="Analyze fraud trends and generate reports" />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="Enhance market surveillance capabilities" />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>

      {/* Contact & Source */}
      <Card sx={{ textAlign: 'center' }}>
        <CardContent sx={{ py: 4 }}>
          <Typography variant="h4" fontWeight="bold" gutterBottom>
            Open Source Project
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            InvestShield is built as an open-source solution for the Securities Market Hackathon. 
            The goal is to create a scalable, modular system that can be deployed by regulatory 
            authorities and financial institutions worldwide.
          </Typography>
          
          <Box display="flex" justifyContent="center" gap={2} flexWrap="wrap">
            <Button
              variant="outlined"
              startIcon={<GitHubIcon />}
              href="https://github.com/ayusharyakashyap/InvestShield"
              target="_blank"
            >
              View on GitHub
            </Button>
            <Button
              variant="outlined"
              startIcon={<EmailIcon />}
              href="mailto:ayush06022004@gmail.com"
            >
              Contact Us
            </Button>
            <Button
              variant="outlined"
              startIcon={<LinkedInIcon />}
              href="https://www.linkedin.com/in/ayush-arya-kashyap/"
              target="_blank"
            >
              LinkedIn
            </Button>
          </Box>
          
          <Typography variant="body2" color="text.secondary" sx={{ mt: 3 }}>
            Built with ❤️ for a safer financial future
          </Typography>
        </CardContent>
      </Card>
    </Container>
  );
};

export default About;
