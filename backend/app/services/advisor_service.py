import pandas as pd
import os
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import json

class AdvisorVerificationService:
    def __init__(self):
        # Use absolute path to ensure we find the data file
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
        self.data_path = os.path.join(project_root, "data/advisors.csv")
        self.advisors_df = None
        self.load_advisor_data()
    
    def load_advisor_data(self):
        """Load advisor data from CSV file"""
        try:
            print(f"Looking for advisor data at: {self.data_path}")
            if os.path.exists(self.data_path):
                self.advisors_df = pd.read_csv(self.data_path)
                print(f"Loaded {len(self.advisors_df)} advisors from CSV")
            else:
                print("CSV file not found, creating sample data")
                # Create sample data if file doesn't exist
                self.create_sample_data()
        except Exception as e:
            print(f"Error loading advisor data: {e}")
            self.create_sample_data()
    
    def create_sample_data(self):
        """Create sample advisor data for testing"""
        sample_data = {
            'sebi_number': [
                'INA000001234', 'INA000001235', 'INA000001236', 'INA000001237', 'INA000001238'
            ],
            'name': [
                'Rajesh Kumar', 'Priya Sharma', 'Amit Patel', 'Sunita Singh', 'Vikram Gupta'
            ],
            'firm_name': [
                'Kumar Investment Advisory', 'Sharma Financial Services', 'Patel Wealth Management',
                'Singh Capital Advisors', 'Gupta Investment Solutions'
            ],
            'status': ['Active', 'Active', 'Suspended', 'Active', 'Active'],
            'location': ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Pune'],
            'registration_date': [
                '2020-01-15', '2019-06-20', '2021-03-10', '2018-11-05', '2020-09-25'
            ],
            'validity_date': [
                '2025-01-15', '2024-06-20', '2026-03-10', '2023-11-05', '2025-09-25'
            ],
            'contact_email': [
                'rajesh@kumar-advisory.com', 'priya@sharma-financial.com', 'amit@patel-wealth.com',
                'sunita@singh-capital.com', 'vikram@gupta-investment.com'
            ],
            'specialization': [
                'Equity Research', 'Mutual Funds', 'Portfolio Management', 'Tax Planning', 'Derivatives'
            ]
        }
        self.advisors_df = pd.DataFrame(sample_data)
    
    def verify_by_sebi_number(self, sebi_number: str) -> Dict[str, Any]:
        """Verify advisor by SEBI registration number"""
        if self.advisors_df is None:
            return self._create_error_response("Advisor database not available")
        
        advisor = self.advisors_df[self.advisors_df['sebi_number'] == sebi_number]
        
        if advisor.empty:
            return {
                'is_verified': False,
                'risk_score': 95.0,
                'status': 'Not Found',
                'message': 'SEBI registration number not found in database',
                'recommendations': [
                    'Verify the SEBI number is correct',
                    'Check SEBI official website',
                    'Do not invest without proper verification'
                ]
            }
        
        advisor_data = advisor.iloc[0]
        return self._process_advisor_verification(advisor_data)
    
    def verify_by_name(self, name: str) -> Dict[str, Any]:
        """Verify advisor by name (fuzzy matching)"""
        if self.advisors_df is None:
            return self._create_error_response("Advisor database not available")
        
        # Simple name matching (can be improved with fuzzy matching)
        advisor = self.advisors_df[
            self.advisors_df['name'].str.lower().str.contains(name.lower(), na=False)
        ]
        
        if advisor.empty:
            return {
                'is_verified': False,
                'risk_score': 85.0,
                'status': 'Not Found',
                'message': f'No advisor found with name containing "{name}"',
                'recommendations': [
                    'Check the spelling of the advisor name',
                    'Try searching with SEBI registration number',
                    'Verify credentials through official channels'
                ]
            }
        
        if len(advisor) > 1:
            return {
                'is_verified': False,
                'risk_score': 60.0,
                'status': 'Multiple Matches',
                'message': f'Multiple advisors found with similar names',
                'matches': advisor[['name', 'sebi_number', 'firm_name']].to_dict('records'),
                'recommendations': [
                    'Use SEBI registration number for exact verification',
                    'Check firm name to identify correct advisor'
                ]
            }
        
        advisor_data = advisor.iloc[0]
        return self._process_advisor_verification(advisor_data)
    
    def _process_advisor_verification(self, advisor_data) -> Dict[str, Any]:
        """Process advisor verification and calculate risk score"""
        status = advisor_data['status']
        validity_date = pd.to_datetime(advisor_data['validity_date'])
        current_date = datetime.now()
        
        # Calculate risk score based on various factors
        risk_score = 0.0
        recommendations = []
        
        if status == 'Active':
            risk_score += 10.0
        elif status == 'Suspended':
            risk_score += 80.0
            recommendations.append('Advisor is currently suspended by SEBI')
        elif status == 'Cancelled':
            risk_score += 95.0
            recommendations.append('Advisor registration has been cancelled')
        
        # Check validity date
        if validity_date < current_date:
            risk_score += 70.0
            recommendations.append('Advisor registration has expired')
        elif validity_date < current_date + timedelta(days=30):
            risk_score += 20.0
            recommendations.append('Advisor registration expires soon')
        
        is_verified = risk_score < 50.0
        
        verification_details = {
            'is_verified': is_verified,
            'risk_score': min(risk_score, 100.0),
            'advisor_details': {
                'sebi_number': advisor_data['sebi_number'],
                'name': advisor_data['name'],
                'firm_name': advisor_data['firm_name'],
                'status': status,
                'location': advisor_data['location'],
                'registration_date': advisor_data['registration_date'],
                'validity_date': advisor_data['validity_date'],
                'specialization': advisor_data['specialization'],
                'contact_email': advisor_data['contact_email']
            },
            'verification_timestamp': current_date.isoformat(),
            'recommendations': recommendations if recommendations else [
                'Advisor appears to be legitimate',
                'Always verify investment advice independently',
                'Check recent performance and reviews'
            ]
        }
        
        return verification_details
    
    def _create_error_response(self, message: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            'is_verified': False,
            'risk_score': 100.0,
            'status': 'Error',
            'message': message,
            'recommendations': [
                'Try again later',
                'Contact support if issue persists'
            ]
        }
    
    def get_all_advisors(self, limit: int = 100) -> Dict[str, Any]:
        """Get list of all advisors"""
        if self.advisors_df is None:
            return {'advisors': [], 'total': 0}
        
        advisors_list = self.advisors_df.head(limit).to_dict('records')
        return {
            'advisors': advisors_list,
            'total': len(self.advisors_df),
            'showing': len(advisors_list)
        }
    
    def get_advisor_stats(self) -> Dict[str, Any]:
        """Get advisor statistics"""
        if self.advisors_df is None:
            return {}
        
        total_advisors = len(self.advisors_df)
        active_advisors = len(self.advisors_df[self.advisors_df['status'] == 'Active'])
        suspended_advisors = len(self.advisors_df[self.advisors_df['status'] == 'Suspended'])
        
        return {
            'total_advisors': total_advisors,
            'active_advisors': active_advisors,
            'suspended_advisors': suspended_advisors,
            'verification_rate': (active_advisors / total_advisors * 100) if total_advisors > 0 else 0
        }
