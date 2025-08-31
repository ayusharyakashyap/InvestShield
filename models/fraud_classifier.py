"""
Fraud Classification Model for Investment Content
Combines keyword-based detection with ML classification
"""

import re
import json
import pickle
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.pipeline import Pipeline
import os

class FraudClassifier:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.pipeline = None
        self.feature_names = []
        self.fraud_keywords = self._load_fraud_keywords()
        self.model_path = os.path.join(os.path.dirname(__file__), 'fraud_model.pkl')
        
    def _load_fraud_keywords(self) -> Dict[str, List[str]]:
        """Load categorized fraud keywords"""
        return {
            'guaranteed_returns': [
                'guaranteed', 'guarantee', '100% profit', '100% returns', 'assured returns',
                'risk-free', 'no risk', 'sure shot', 'confirmed profit', 'guaranteed profit'
            ],
            'urgency_pressure': [
                'limited time', 'hurry up', 'act fast', 'only today', 'last chance',
                'urgent', 'immediate', 'expires soon', 'limited slots', 'book now'
            ],
            'insider_trading': [
                'insider tip', 'insider information', 'confidential info', 'secret tip',
                'inside news', 'exclusive tip', 'company insider', 'private information'
            ],
            'fake_credentials': [
                'sebi registered', 'government approved', 'rbi certified', 'official advisor',
                'licensed by sebi', 'authorized dealer', 'certified analyst'
            ],
            'unrealistic_claims': [
                'double money', 'triple returns', 'multiply wealth', '1000% returns',
                'crorepati in days', 'overnight rich', 'instant wealth', 'money multiplication'
            ],
            'contact_pressure': [
                'whatsapp immediately', 'call now', 'message for details', 'dm for tips',
                'join telegram', 'click link', 'download app', 'register immediately'
            ]
        }
    
    def prepare_training_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data from sample dataset"""
        # Sample training data
        training_texts = [
            # Fraudulent examples
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
            
            # Legitimate examples
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
        ]
        
        # Labels: 1 for fraudulent, 0 for legitimate
        labels = [1] * 15 + [0] * 15  # First 15 are fraudulent, next 15 are legitimate
        
        return np.array(training_texts), np.array(labels)
    
    def extract_features(self, texts: List[str]) -> np.ndarray:
        """Extract features from texts"""
        # Keyword-based features
        keyword_features = []
        
        for text in texts:
            text_lower = text.lower()
            features = []
            
            # Count keywords in each category
            for category, keywords in self.fraud_keywords.items():
                count = sum(1 for keyword in keywords if keyword in text_lower)
                features.append(count)
            
            # Text-based features
            features.extend([
                len(text),  # Text length
                len(text.split()),  # Word count
                text.count('!'),  # Exclamation marks
                text.count('₹'),  # Currency symbols
                text.count('%'),  # Percentage symbols
                len(re.findall(r'\d+', text)),  # Number count
                1 if any(word in text_lower for word in ['call', 'whatsapp', 'telegram']) else 0,  # Contact methods
                1 if any(word in text_lower for word in ['download', 'app', 'link']) else 0,  # App/link mentions
                1 if re.search(r'\d+%', text) else 0,  # Percentage returns mentioned
                1 if any(word in text_lower for word in ['transfer', 'pay', 'send money']) else 0  # Payment requests
            ])
            
            keyword_features.append(features)
        
        return np.array(keyword_features)
    
    def train_model(self) -> Dict[str, Any]:
        """Train the fraud classification model"""
        # Get training data
        texts, labels = self.prepare_training_data()
        
        # Create pipeline with TF-IDF and Random Forest
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 2),
                stop_words='english',
                min_df=1,
                max_df=0.95
            )),
            ('classifier', RandomForestClassifier(
                n_estimators=100,
                random_state=42,
                max_depth=10,
                min_samples_split=5
            ))
        ])
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=0.3, random_state=42, stratify=labels
        )
        
        # Train model
        self.pipeline.fit(X_train, y_train)
        
        # Evaluate model
        y_pred = self.pipeline.predict(X_test)
        train_score = self.pipeline.score(X_train, y_train)
        test_score = self.pipeline.score(X_test, y_test)
        
        # Save model
        self.save_model()
        
        return {
            'train_accuracy': train_score,
            'test_accuracy': test_score,
            'classification_report': classification_report(y_test, y_pred, output_dict=True),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
            'feature_count': len(self.pipeline.named_steps['tfidf'].get_feature_names_out())
        }
    
    def predict(self, text: str) -> Dict[str, Any]:
        """Predict if text is fraudulent"""
        if self.pipeline is None:
            self.load_model()
        
        if self.pipeline is None:
            # Fallback to keyword-based classification
            return self._keyword_based_prediction(text)
        
        # ML-based prediction
        try:
            prediction = self.pipeline.predict([text])[0]
            probability = self.pipeline.predict_proba([text])[0]
            fraud_probability = probability[1] if len(probability) > 1 else 0.5
            
            # Combine with keyword analysis
            keyword_result = self._keyword_based_prediction(text)
            
            # Weighted combination
            ml_weight = 0.7
            keyword_weight = 0.3
            
            final_fraud_score = (
                ml_weight * fraud_probability * 100 + 
                keyword_weight * keyword_result['fraud_score']
            )
            
            return {
                'is_fraudulent': prediction == 1 or final_fraud_score > 60,
                'fraud_score': min(final_fraud_score, 100),
                'ml_prediction': int(prediction),
                'ml_confidence': float(fraud_probability),
                'keyword_indicators': keyword_result['keyword_indicators'],
                'model_used': 'ml_hybrid'
            }
            
        except Exception as e:
            # Fallback to keyword-based prediction
            print(f"ML prediction failed: {e}")
            return self._keyword_based_prediction(text)
    
    def _keyword_based_prediction(self, text: str) -> Dict[str, Any]:
        """Fallback keyword-based prediction"""
        text_lower = text.lower()
        fraud_score = 0
        found_indicators = []
        
        # Check for fraud keywords
        for category, keywords in self.fraud_keywords.items():
            found_keywords = [kw for kw in keywords if kw in text_lower]
            if found_keywords:
                category_score = len(found_keywords) * 15  # 15 points per keyword
                fraud_score += category_score
                found_indicators.extend(found_keywords)
        
        # Additional pattern checks
        if re.search(r'\d+%.*return', text_lower):
            fraud_score += 25
            found_indicators.append('percentage_return_claim')
        
        if re.search(r'transfer.*money|pay.*now', text_lower):
            fraud_score += 30
            found_indicators.append('payment_request')
        
        if re.search(r'call.*now|whatsapp.*\d+', text_lower):
            fraud_score += 20
            found_indicators.append('urgent_contact')
        
        fraud_score = min(fraud_score, 100)  # Cap at 100
        
        return {
            'is_fraudulent': fraud_score > 50,
            'fraud_score': fraud_score,
            'keyword_indicators': found_indicators,
            'model_used': 'keyword_based'
        }
    
    def save_model(self):
        """Save trained model to disk"""
        try:
            with open(self.model_path, 'wb') as f:
                pickle.dump(self.pipeline, f)
            print(f"Model saved to {self.model_path}")
        except Exception as e:
            print(f"Failed to save model: {e}")
    
    def load_model(self):
        """Load trained model from disk"""
        try:
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    self.pipeline = pickle.load(f)
                print(f"Model loaded from {self.model_path}")
            else:
                print("No saved model found. Training new model...")
                self.train_model()
        except Exception as e:
            print(f"Failed to load model: {e}")
            self.pipeline = None
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from trained model"""
        if self.pipeline is None:
            return {}
        
        try:
            # Get TF-IDF feature names
            feature_names = self.pipeline.named_steps['tfidf'].get_feature_names_out()
            
            # Get Random Forest feature importance
            importance_scores = self.pipeline.named_steps['classifier'].feature_importances_
            
            # Create feature importance dictionary
            feature_importance = dict(zip(feature_names, importance_scores))
            
            # Sort by importance
            sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
            
            return dict(sorted_features[:20])  # Return top 20 features
            
        except Exception as e:
            print(f"Failed to get feature importance: {e}")
            return {}
    
    def update_keywords(self, new_keywords: Dict[str, List[str]]):
        """Update fraud keywords"""
        for category, keywords in new_keywords.items():
            if category in self.fraud_keywords:
                self.fraud_keywords[category].extend(keywords)
            else:
                self.fraud_keywords[category] = keywords
        
        print("Keywords updated. Consider retraining the model for better performance.")

# Example usage and testing
if __name__ == "__main__":
    classifier = FraudClassifier()
    
    # Train model
    print("Training fraud classification model...")
    results = classifier.train_model()
    print(f"Training completed. Test accuracy: {results['test_accuracy']:.2f}")
    
    # Test predictions
    test_texts = [
        "Guaranteed 100% returns in 30 days! Call now!",
        "Mutual fund investments are subject to market risks.",
        "Secret insider tip! Buy this stock for huge profits!",
        "Our SEBI registered advisors provide investment advice."
    ]
    
    print("\nTesting predictions:")
    for text in test_texts:
        result = classifier.predict(text)
        print(f"Text: {text[:50]}...")
        print(f"Fraudulent: {result['is_fraudulent']}, Score: {result['fraud_score']:.1f}")
        print(f"Indicators: {result['keyword_indicators']}")
        print("-" * 60)
