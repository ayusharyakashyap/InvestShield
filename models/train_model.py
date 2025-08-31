"""
Training Script for InvestShield Fraud Detection Models
Combines multiple approaches: keyword-based, ML, and advanced NLP
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
import json
import warnings
warnings.filterwarnings('ignore')

# Add models directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fraud_classifier import FraudClassifier
from text_analyzer import TextAnalyzer

class ModelTrainer:
    def __init__(self):
        self.data_path = os.path.join(os.path.dirname(__file__), '../data')
        self.models_path = os.path.dirname(__file__)
        self.results = {}
        
    def load_training_data(self):
        """Load training data from CSV files"""
        try:
            # Load suspicious posts data
            suspicious_posts_path = os.path.join(self.data_path, 'suspicious_posts.csv')
            if os.path.exists(suspicious_posts_path):
                self.suspicious_posts = pd.read_csv(suspicious_posts_path)
                print(f"Loaded {len(self.suspicious_posts)} suspicious posts")
            else:
                print("Creating sample suspicious posts data...")
                self.create_sample_suspicious_posts()
            
            return True
            
        except Exception as e:
            print(f"Error loading training data: {e}")
            return False
    
    def create_sample_suspicious_posts(self):
        """Create sample training data if files don't exist"""
        sample_data = {
            'id': range(1, 31),
            'content': [
                # High-risk fraudulent content
                "Guaranteed 100% returns in 30 days! Join our WhatsApp group for insider tips!",
                "SEBI registered advisor offering risk-free investments with 200% profit guarantee!",
                "Secret stock tip from company insider! Buy immediately for huge profits!",
                "Join thousands who became crorepatis overnight! Download our app now!",
                "Exclusive IPO allotment confirmed. Transfer money to secure your shares.",
                "Government approved investment scheme! Invest ₹10000 and get ₹50000 in 60 days.",
                "Urgent: Market will crash tomorrow! Sell everything and buy our recommended stocks.",
                "Free trading course worth ₹50000! Learn secret strategies used by billionaires.",
                "Multibagger stock alert! This stock will give 1000% returns in 3 months.",
                "Bitcoin investment opportunity! Invest ₹1 lakh and get ₹5 lakhs in 90 days.",
                "Last chance! IPO subscription closing in 2 hours. Guaranteed 300% listing gains.",
                "Forex trading robot makes ₹1 lakh daily! Fully automated system.",
                "Share market crash warning! Protect your money with our gold investment scheme.",
                "Penny stock millionaire secret! Turn ₹10000 into ₹10 lakhs in 6 months.",
                "Breaking: New cryptocurrency will make you rich! Early investors getting 500% returns.",
                
                # Legitimate investment content
                "Mutual fund investments are subject to market risks. Please read all scheme related documents carefully.",
                "Our SEBI registered advisors provide personalized investment advice based on your risk profile.",
                "Diversification across asset classes can help reduce portfolio risk over the long term.",
                "Systematic Investment Plans (SIPs) allow you to invest regularly in mutual funds.",
                "Past performance does not guarantee future returns. Please invest based on your financial goals.",
                "Fixed deposits offer stable returns but may not beat inflation in the long run.",
                "Equity investments may be suitable for investors with high risk tolerance and long investment horizon.",
                "Insurance planning is essential to protect your family's financial future.",
                "Tax-saving investments under Section 80C can help reduce your taxable income.",
                "Asset allocation should be based on your age, income, and investment goals.",
                "Regular portfolio review and rebalancing is important for optimal returns.",
                "Emergency fund covering 6-12 months of expenses should be maintained in liquid instruments.",
                "Real estate investment trusts (REITs) provide exposure to real estate without direct property ownership.",
                "Corporate bonds may offer higher yields than government securities but carry credit risk.",
                "Gold can be considered as a hedge against inflation and currency fluctuation."
            ],
            'source': ['WhatsApp', 'Telegram', 'Twitter', 'Facebook', 'Email'] * 6,
            'fraud_type': [
                'guaranteed_returns_scam', 'fake_advisor', 'insider_trading_scam', 'unrealistic_promises',
                'fake_ipo_scam', 'fake_credentials', 'market_manipulation', 'fake_course_scam',
                'guaranteed_returns_scam', 'crypto_scam', 'fake_ipo_scam', 'forex_robot_scam',
                'fear_mongering_scam', 'penny_stock_scam', 'crypto_scam'
            ] + ['legitimate'] * 15,
            'risk_score': [95.5, 87.3, 92.1, 89.7, 94.2, 88.4, 90.8, 75.6, 93.7, 89.3,
                          92.8, 87.6, 79.5, 88.2, 86.9] + [15.2, 12.8, 18.5, 16.7, 14.3,
                          19.8, 17.9, 21.4, 20.1, 16.5, 18.8, 15.9, 19.3, 22.7, 25.1],
            'is_verified_fraud': [True] * 15 + [False] * 15,
            'created_at': [f"2024-08-{25 + i//10} {10 + i%12}:{30 + i%30}:00" for i in range(30)]
        }
        
        self.suspicious_posts = pd.DataFrame(sample_data)
        
        # Save to CSV
        suspicious_posts_path = os.path.join(self.data_path, 'suspicious_posts.csv')
        self.suspicious_posts.to_csv(suspicious_posts_path, index=False)
        print(f"Created sample suspicious posts data with {len(self.suspicious_posts)} entries")
    
    def train_fraud_classifier(self):
        """Train the ML-based fraud classifier"""
        print("\n" + "="*60)
        print("Training ML-based Fraud Classifier")
        print("="*60)
        
        try:
            classifier = FraudClassifier()
            training_results = classifier.train_model()
            
            self.results['fraud_classifier'] = {
                'status': 'success',
                'train_accuracy': training_results['train_accuracy'],
                'test_accuracy': training_results['test_accuracy'],
                'feature_count': training_results['feature_count'],
                'classification_report': training_results['classification_report'],
                'confusion_matrix': training_results['confusion_matrix']
            }
            
            print(f"✅ Training completed successfully!")
            print(f"   Train Accuracy: {training_results['train_accuracy']:.3f}")
            print(f"   Test Accuracy: {training_results['test_accuracy']:.3f}")
            print(f"   Features Used: {training_results['feature_count']}")
            
            # Test the classifier with sample data
            print("\n📊 Testing classifier with sample posts...")
            test_accuracy = self.test_classifier_with_data(classifier)
            self.results['fraud_classifier']['sample_test_accuracy'] = test_accuracy
            
            return classifier
            
        except Exception as e:
            print(f"❌ Training failed: {e}")
            self.results['fraud_classifier'] = {'status': 'failed', 'error': str(e)}
            return None
    
    def test_classifier_with_data(self, classifier):
        """Test classifier with loaded data"""
        if not hasattr(self, 'suspicious_posts'):
            return 0.0
        
        correct_predictions = 0
        total_predictions = 0
        
        for _, row in self.suspicious_posts.iterrows():
            text = row['content']
            actual_is_fraud = row['is_verified_fraud']
            
            prediction = classifier.predict(text)
            predicted_is_fraud = prediction['is_fraudulent']
            
            if predicted_is_fraud == actual_is_fraud:
                correct_predictions += 1
            total_predictions += 1
        
        accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
        print(f"   Sample Data Accuracy: {accuracy:.3f} ({correct_predictions}/{total_predictions})")
        
        return accuracy
    
    def train_text_analyzer(self):
        """Initialize and test the text analyzer"""
        print("\n" + "="*60)
        print("Initializing Advanced Text Analyzer")
        print("="*60)
        
        try:
            analyzer = TextAnalyzer()
            
            # Test with sample texts
            test_texts = [
                "Guaranteed 100% returns! Call now for insider tips!",
                "Mutual fund investments are subject to market risks.",
                "Secret stock tip from company insider! Huge profits!",
                "Our SEBI registered advisors provide investment advice."
            ]
            
            print("🧪 Testing text analyzer...")
            analysis_results = []
            
            for i, text in enumerate(test_texts):
                result = analyzer.analyze_text(text)
                analysis_results.append(result)
                
                print(f"   Test {i+1}: Risk Score = {result['risk_score']:.1f}")
                print(f"          Patterns: {len(result['fraud_patterns']['detected_patterns'])}")
                print(f"          Recommendations: {len(result['recommendations'])}")
            
            # Get batch analysis summary
            summary = analyzer.get_analysis_summary(analysis_results)
            
            self.results['text_analyzer'] = {
                'status': 'success',
                'test_results': {
                    'total_tested': len(test_texts),
                    'average_risk_score': summary.get('average_risk_score', 0),
                    'max_risk_score': summary.get('max_risk_score', 0),
                    'high_risk_count': summary.get('high_risk_count', 0)
                }
            }
            
            print(f"✅ Text analyzer initialized successfully!")
            print(f"   Average Risk Score: {summary.get('average_risk_score', 0):.1f}")
            print(f"   High Risk Detections: {summary.get('high_risk_count', 0)}")
            
            return analyzer
            
        except Exception as e:
            print(f"❌ Text analyzer initialization failed: {e}")
            self.results['text_analyzer'] = {'status': 'failed', 'error': str(e)}
            return None
    
    def evaluate_combined_system(self):
        """Evaluate the combined fraud detection system"""
        print("\n" + "="*60)
        print("Evaluating Combined Fraud Detection System")
        print("="*60)
        
        try:
            # Initialize both models
            classifier = FraudClassifier()
            analyzer = TextAnalyzer()
            
            # Load existing model if available
            classifier.load_model()
            
            if not hasattr(self, 'suspicious_posts'):
                self.load_training_data()
            
            # Test combined system
            ml_correct = 0
            analyzer_correct = 0
            combined_correct = 0
            total_tests = 0
            
            print("🔍 Testing combined system...")
            
            for _, row in self.suspicious_posts.iterrows():
                text = row['content']
                actual_is_fraud = row['is_verified_fraud']
                
                # ML classifier prediction
                ml_result = classifier.predict(text)
                ml_prediction = ml_result['is_fraudulent']
                
                # Text analyzer prediction
                analyzer_result = analyzer.analyze_text(text)
                analyzer_prediction = analyzer_result['risk_score'] > 50
                
                # Combined prediction (weighted voting)
                ml_confidence = ml_result.get('fraud_score', 50) / 100
                analyzer_confidence = analyzer_result['risk_score'] / 100
                
                combined_score = (0.6 * ml_confidence + 0.4 * analyzer_confidence) * 100
                combined_prediction = combined_score > 50
                
                # Check accuracy
                if ml_prediction == actual_is_fraud:
                    ml_correct += 1
                if analyzer_prediction == actual_is_fraud:
                    analyzer_correct += 1
                if combined_prediction == actual_is_fraud:
                    combined_correct += 1
                
                total_tests += 1
            
            # Calculate accuracies
            ml_accuracy = ml_correct / total_tests if total_tests > 0 else 0
            analyzer_accuracy = analyzer_correct / total_tests if total_tests > 0 else 0
            combined_accuracy = combined_correct / total_tests if total_tests > 0 else 0
            
            self.results['combined_system'] = {
                'status': 'success',
                'ml_accuracy': ml_accuracy,
                'analyzer_accuracy': analyzer_accuracy,
                'combined_accuracy': combined_accuracy,
                'total_tests': total_tests
            }
            
            print(f"✅ Combined system evaluation completed!")
            print(f"   ML Classifier Accuracy: {ml_accuracy:.3f}")
            print(f"   Text Analyzer Accuracy: {analyzer_accuracy:.3f}")
            print(f"   Combined System Accuracy: {combined_accuracy:.3f}")
            print(f"   Total Tests: {total_tests}")
            
        except Exception as e:
            print(f"❌ Combined system evaluation failed: {e}")
            self.results['combined_system'] = {'status': 'failed', 'error': str(e)}
    
    def generate_training_report(self):
        """Generate comprehensive training report"""
        print("\n" + "="*60)
        print("TRAINING REPORT")
        print("="*60)
        
        report = {
            'training_timestamp': datetime.now().isoformat(),
            'training_data_size': len(self.suspicious_posts) if hasattr(self, 'suspicious_posts') else 0,
            'models_trained': self.results
        }
        
        # Print summary
        print(f"📊 Training Summary:")
        print(f"   Training Data Size: {report['training_data_size']}")
        print(f"   Training Timestamp: {report['training_timestamp']}")
        
        for model_name, result in self.results.items():
            status = result.get('status', 'unknown')
            print(f"   {model_name.replace('_', ' ').title()}: {status.upper()}")
            
            if status == 'success':
                if 'test_accuracy' in result:
                    print(f"      Test Accuracy: {result['test_accuracy']:.3f}")
                if 'combined_accuracy' in result:
                    print(f"      Combined Accuracy: {result['combined_accuracy']:.3f}")
        
        # Save report
        report_path = os.path.join(self.models_path, 'training_report.json')
        try:
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"\n💾 Training report saved to: {report_path}")
        except Exception as e:
            print(f"❌ Failed to save training report: {e}")
        
        return report
    
    def run_full_training(self):
        """Run complete training pipeline"""
        print("🚀 Starting InvestShield Model Training Pipeline")
        print("=" * 80)
        
        # Load training data
        print("📥 Loading training data...")
        if not self.load_training_data():
            print("❌ Failed to load training data. Aborting.")
            return False
        
        # Train fraud classifier
        classifier = self.train_fraud_classifier()
        
        # Initialize text analyzer
        analyzer = self.train_text_analyzer()
        
        # Evaluate combined system
        self.evaluate_combined_system()
        
        # Generate report
        report = self.generate_training_report()
        
        print("\n🎉 Training pipeline completed!")
        return True

def main():
    """Main training function"""
    trainer = ModelTrainer()
    success = trainer.run_full_training()
    
    if success:
        print("\n✅ All models trained successfully!")
        print("🔧 You can now start the InvestShield API server.")
    else:
        print("\n❌ Training completed with errors.")
        print("🔧 Check the error messages and fix any issues.")

if __name__ == "__main__":
    main()
