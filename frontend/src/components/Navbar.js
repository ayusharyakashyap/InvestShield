import React, { useState } from 'react';
import { 
  AppBar, 
  Toolbar, 
  Typography, 
  Button, 
  Box, 
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  useTheme,
  useMediaQuery
} from '@mui/material';
import {
  Menu as MenuIcon,
  Security as SecurityIcon,
  VerifiedUser as VerifiedUserIcon,
  Scanner as ScannerIcon,
  Dashboard as DashboardIcon,
  Info as InfoIcon,
  Home as HomeIcon
} from '@mui/icons-material';
import { Link, useLocation } from 'react-router-dom';

const navItems = [
  { name: 'Home', path: '/', icon: <HomeIcon /> },
  { name: 'Advisor Verification', path: '/advisor-verification', icon: <VerifiedUserIcon /> },
  { name: 'Content Scanner', path: '/content-scanner', icon: <ScannerIcon /> },
  { name: 'Dashboard', path: '/dashboard', icon: <DashboardIcon /> },
  { name: 'About', path: '/about', icon: <InfoIcon /> },
];

const Navbar = () => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const location = useLocation();

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const drawer = (
    <Box onClick={handleDrawerToggle} sx={{ textAlign: 'center' }}>
      <Typography variant="h6" sx={{ my: 2, color: 'primary.main', fontWeight: 'bold' }}>
        <SecurityIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        InvestShield
      </Typography>
      <List>
        {navItems.map((item) => (
          <ListItem 
            key={item.name} 
            component={Link} 
            to={item.path}
            sx={{
              color: location.pathname === item.path ? 'primary.main' : 'text.primary',
              backgroundColor: location.pathname === item.path ? 'rgba(59, 130, 246, 0.1)' : 'transparent',
              '&:hover': {
                backgroundColor: 'rgba(59, 130, 246, 0.08)',
                color: 'primary.main',
              },
            }}
          >
            <ListItemIcon sx={{ color: 'inherit', minWidth: 40 }}>
              {item.icon}
            </ListItemIcon>
            <ListItemText primary={item.name} />
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <>
      <AppBar 
        position="sticky" 
        elevation={1}
        sx={{ 
          backgroundColor: 'background.paper',
          color: 'text.primary',
          borderBottom: '1px solid',
          borderColor: 'divider'
        }}
      >
        <Toolbar>
          {/* Mobile menu button */}
          {isMobile && (
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
          )}

          {/* Logo */}
          <Box
            component={Link}
            to="/"
            sx={{
              display: 'flex',
              alignItems: 'center',
              textDecoration: 'none',
              color: 'inherit',
              mr: 4,
            }}
          >
            <SecurityIcon 
              sx={{ 
                mr: 1, 
                fontSize: 32,
                color: 'primary.main'
              }} 
            />
            <Typography 
              variant="h6" 
              component="div" 
              sx={{ 
                fontWeight: 'bold',
                background: 'linear-gradient(45deg, #3b82f6, #8b5cf6)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              InvestShield
            </Typography>
          </Box>

          {/* Desktop navigation */}
          {!isMobile && (
            <Box sx={{ flexGrow: 1, display: 'flex', justifyContent: 'center' }}>
              {navItems.map((item) => (
                <Button
                  key={item.name}
                  component={Link}
                  to={item.path}
                  startIcon={item.icon}
                  sx={{
                    mx: 1,
                    color: location.pathname === item.path ? 'primary.main' : 'text.primary',
                    backgroundColor: location.pathname === item.path ? 'rgba(59, 130, 246, 0.1)' : 'transparent',
                    '&:hover': {
                      backgroundColor: 'rgba(59, 130, 246, 0.08)',
                      color: 'primary.main',
                    },
                    fontWeight: location.pathname === item.path ? 600 : 400,
                    borderRadius: 2,
                    px: 2,
                  }}
                >
                  {item.name}
                </Button>
              ))}
            </Box>
          )}

          {/* Right side content */}
          <Box sx={{ flexGrow: isMobile ? 1 : 0 }} />
          
          {/* Status indicator */}
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              px: 2,
              py: 0.5,
              borderRadius: 1,
              backgroundColor: 'success.light',
              color: 'success.dark',
              fontSize: '0.875rem',
              fontWeight: 500,
            }}
          >
            <Box
              sx={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                backgroundColor: 'success.main',
                mr: 1,
                animation: 'pulse 2s infinite',
              }}
            />
            {isMobile ? 'Active' : 'System Active'}
          </Box>
        </Toolbar>
      </AppBar>

      {/* Mobile drawer */}
      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={handleDrawerToggle}
        ModalProps={{
          keepMounted: true, // Better open performance on mobile
        }}
        sx={{
          display: { xs: 'block', md: 'none' },
          '& .MuiDrawer-paper': { boxSizing: 'border-box', width: 280 },
        }}
      >
        {drawer}
      </Drawer>
    </>
  );
};

export default Navbar;
