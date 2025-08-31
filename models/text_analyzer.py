"""
Advanced Text Analysis for Investment Fraud Detection
Includes sentiment analysis, entity extraction, and pattern recognition
"""

import re
import spacy
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from collections import Counter
import string
from datetime import datetime

class TextAnalyzer:
    def __init__(self):
        # Try to load spaCy model, fallback if not available
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Warning: spaCy model 'en_core_web_sm' not found. Using basic analysis.")
            self.nlp = None
        
        self.fraud_indicators = self._load_fraud_indicators()
        self.sentiment_words = self._load_sentiment_words()
        self.financial_entities = self._load_financial_entities()
    
    def _load_fraud_indicators(self) -> Dict[str, Dict[str, Any]]:
        """Load fraud indicator patterns with weights"""
        return {
            'urgency_indicators': {
                'patterns': [
                    r'urgent(?:ly)?|immediate(?:ly)?|asap|right now|hurry',
                    r'limited time|expires? (?:soon|today)|last chance',
                    r'act fast|quick(?:ly)?|rush|don\'t wait',
                    r'only \d+ (?:left|remaining|spots?|slots?)'
                ],
                'weight': 25,
                'description': 'Creates false urgency'
            },
            'guarantee_indicators': {
                'patterns': [
                    r'guarantee(?:d)?|assured|certain|sure(?:ly)?',
                    r'100% (?:profit|return|safe|secure)',
                    r'risk[- ]?free|no risk|zero risk',
                    r'confirmed (?:profit|return)'
                ],
                'weight': 30,
                'description': 'False guarantees in investments'
            },
            'authority_claims': {
                'patterns': [
                    r'sebi (?:approved|registered|certified)',
                    r'government (?:approved|backed|endorsed)',
                    r'rbi (?:certified|approved|licensed)',
                    r'official(?:ly)? (?:approved|endorsed)'
                ],
                'weight': 25,
                'description': 'False authority claims'
            },
            'insider_trading': {
                'patterns': [
                    r'insider (?:tip|info|information|knowledge)',
                    r'secret (?:tip|info|strategy)',
                    r'confidential (?:tip|info|data)',
                    r'exclusive (?:tip|info|offer)'
                ],
                'weight': 35,
                'description': 'Illegal insider trading claims'
            },
            'unrealistic_returns': {
                'patterns': [
                    r'\d+00% (?:profit|return|gain)',
                    r'(?:double|triple|multiply) (?:your )?money',
                    r'(?:crorepati|millionaire) (?:in|within) \d+',
                    r'\d+x (?:return|profit|gain)'
                ],
                'weight': 35,
                'description': 'Unrealistic profit promises'
            },
            'contact_pressure': {
                'patterns': [
                    r'call (?:now|immediately)|whatsapp (?:now|\+?\d+)',
                    r'message (?:me|us) (?:now|immediately)',
                    r'dm (?:for|me)|inbox (?:me|us)',
                    r'telegram @?\w+|join (?:telegram|whatsapp)'
                ],
                'weight': 20,
                'description': 'Pressure to make immediate contact'
            },
            'payment_requests': {
                'patterns': [
                    r'transfer (?:money|amount|\u20b9\d+)',
                    r'pay (?:now|immediately|\u20b9\d+)',
                    r'send (?:money|payment|\u20b9\d+)',
                    r'deposit (?:\u20b9\d+|money|amount)'
                ],
                'weight': 40,
                'description': 'Direct payment requests'
            }
        }
    
    def _load_sentiment_words(self) -> Dict[str, List[str]]:
        """Load sentiment indicator words"""
        return {
            'positive_manipulation': [
                'amazing', 'incredible', 'fantastic', 'unbelievable',
                'extraordinary', 'miraculous', 'revolutionary',
                'life-changing', 'game-changer', 'breakthrough'
            ],
            'fear_words': [
                'crash', 'collapse', 'lose', 'risk', 'danger',
                'warning', 'alert', 'crisis', 'emergency', 'panic'
            ],
            'greed_words': [
                'rich', 'wealthy', 'fortune', 'jackpot', 'treasure',
                'gold mine', 'cash cow', 'money maker', 'profit machine'
            ]
        }
    
    def _load_financial_entities(self) -> List[str]:
        """Load financial entity patterns"""
        return [
            'sebi', 'rbi', 'nse', 'bse', 'mutual fund', 'sip',
            'ipo', 'share', 'stock', 'equity', 'bond', 'derivative',
            'portfolio', 'investment', 'trading', 'forex', 'crypto',
            'bitcoin', 'rupee', 'dollar', 'return', 'profit', 'dividend'
        ]
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Comprehensive text analysis for fraud detection"""
        if not text or len(text.strip()) < 5:
            return self._create_empty_analysis()
        
        # Basic preprocessing
        text_clean = self._preprocess_text(text)
        
        # Perform various analyses
        fraud_patterns = self._detect_fraud_patterns(text_clean)
        sentiment_analysis = self._analyze_sentiment(text_clean)
        entity_analysis = self._analyze_entities(text)
        linguistic_features = self._extract_linguistic_features(text)
        financial_context = self._analyze_financial_context(text_clean)
        
        # Calculate overall risk score
        risk_score = self._calculate_risk_score(
            fraud_patterns, sentiment_analysis, linguistic_features, financial_context
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(fraud_patterns, risk_score)
        
        return {
            'risk_score': risk_score,
            'fraud_patterns': fraud_patterns,
            'sentiment_analysis': sentiment_analysis,
            'entity_analysis': entity_analysis,
            'linguistic_features': linguistic_features,
            'financial_context': financial_context,
            'recommendations': recommendations,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for analysis"""
        # Convert to lowercase
        text_clean = text.lower()
        
        # Remove excessive whitespace
        text_clean = re.sub(r'\s+', ' ', text_clean).strip()
        
        # Normalize currency symbols
        text_clean = re.sub(r'[₹\$€£¥]', '₹', text_clean)
        
        return text_clean
    
    def _detect_fraud_patterns(self, text: str) -> Dict[str, Any]:
        """Detect fraud patterns in text"""
        detected_patterns = {}
        total_weight = 0
        
        for category, info in self.fraud_indicators.items():
            matches = []
            for pattern in info['patterns']:
                found_matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in found_matches:
                    matches.append({
                        'text': match.group(),
                        'start': match.start(),
                        'end': match.end()
                    })
            
            if matches:
                detected_patterns[category] = {
                    'matches': matches,
                    'count': len(matches),
                    'weight': info['weight'],
                    'description': info['description']
                }
                total_weight += info['weight'] * min(len(matches), 3)  # Diminishing returns
        
        return {
            'detected_patterns': detected_patterns,
            'total_pattern_score': min(total_weight, 100),
            'pattern_categories': list(detected_patterns.keys())
        }
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment indicators"""
        sentiment_scores = {}
        
        for sentiment_type, words in self.sentiment_words.items():
            count = sum(1 for word in words if word in text)
            sentiment_scores[sentiment_type] = count
        
        # Calculate manipulation score
        manipulation_score = (
            sentiment_scores.get('positive_manipulation', 0) * 10 +
            sentiment_scores.get('fear_words', 0) * 8 +
            sentiment_scores.get('greed_words', 0) * 12
        )
        
        return {
            'sentiment_scores': sentiment_scores,
            'manipulation_score': min(manipulation_score, 50),
            'dominant_sentiment': max(sentiment_scores.items(), key=lambda x: x[1])[0] if sentiment_scores else 'neutral'
        }
    
    def _analyze_entities(self, text: str) -> Dict[str, Any]:
        """Extract and analyze named entities"""
        entities = {
            'financial_terms': [],
            'organizations': [],
            'monetary_amounts': [],
            'percentages': [],
            'phone_numbers': [],
            'email_addresses': [],
            'urls': []
        }
        
        # Extract monetary amounts
        money_pattern = r'₹\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:lakh|crore|thousand|k)?'
        entities['monetary_amounts'] = re.findall(money_pattern, text, re.IGNORECASE)
        
        # Extract percentages
        percent_pattern = r'(\d+(?:\.\d+)?)\s*%'
        entities['percentages'] = re.findall(percent_pattern, text)
        
        # Extract phone numbers
        phone_pattern = r'(?:\+91|91)?[-.\s]?[6-9]\d{9}'
        entities['phone_numbers'] = re.findall(phone_pattern, text)
        
        # Extract email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        entities['email_addresses'] = re.findall(email_pattern, text)
        
        # Extract URLs
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        entities['urls'] = re.findall(url_pattern, text)
        
        # Extract financial terms
        text_lower = text.lower()
        entities['financial_terms'] = [term for term in self.financial_entities if term in text_lower]
        
        # Use spaCy if available
        if self.nlp:
            try:
                doc = self.nlp(text)
                entities['organizations'] = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
            except Exception:
                pass
        
        return entities
    
    def _extract_linguistic_features(self, text: str) -> Dict[str, Any]:
        """Extract linguistic features"""
        features = {
            'text_length': len(text),
            'word_count': len(text.split()),
            'sentence_count': len(re.split(r'[.!?]+', text)),
            'exclamation_count': text.count('!'),
            'question_count': text.count('?'),
            'caps_word_count': len(re.findall(r'\b[A-Z]{2,}\b', text)),
            'emoji_count': len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', text)),
            'punctuation_density': sum(1 for char in text if char in string.punctuation) / len(text) if text else 0
        }
        
        # Calculate readability features
        avg_word_length = sum(len(word) for word in text.split()) / len(text.split()) if text.split() else 0
        avg_sentence_length = features['word_count'] / features['sentence_count'] if features['sentence_count'] > 0 else 0
        
        features.update({
            'avg_word_length': avg_word_length,
            'avg_sentence_length': avg_sentence_length,
            'complexity_score': avg_word_length + avg_sentence_length / 10
        })
        
        return features
    
    def _analyze_financial_context(self, text: str) -> Dict[str, Any]:
        """Analyze financial context and claims"""
        context = {
            'investment_mentions': len(re.findall(r'invest(?:ment)?|trading|portfolio', text)),
            'return_claims': len(re.findall(r'return|profit|gain|income', text)),
            'risk_mentions': len(re.findall(r'risk|safe|secure|guaranteed', text)),
            'authority_references': len(re.findall(r'sebi|rbi|government|official', text)),
            'urgency_indicators': len(re.findall(r'urgent|immediate|hurry|fast|now', text)),
            'contact_methods': len(re.findall(r'call|whatsapp|telegram|email|message', text))
        }
        
        # Calculate financial legitimacy score
        legitimacy_indicators = [
            'diversification', 'risk assessment', 'financial planning',
            'long term', 'systematic', 'regulated', 'compliance'
        ]
        
        legitimacy_score = sum(5 for indicator in legitimacy_indicators if indicator in text)
        context['legitimacy_score'] = min(legitimacy_score, 35)
        
        return context
    
    def _calculate_risk_score(self, fraud_patterns: Dict, sentiment_analysis: Dict,
                            linguistic_features: Dict, financial_context: Dict) -> float:
        """Calculate overall risk score"""
        # Base score from fraud patterns
        pattern_score = fraud_patterns.get('total_pattern_score', 0)
        
        # Sentiment manipulation score
        sentiment_score = sentiment_analysis.get('manipulation_score', 0)
        
        # Linguistic suspicion score
        linguistic_score = 0
        if linguistic_features['exclamation_count'] > 3:
            linguistic_score += 10
        if linguistic_features['caps_word_count'] > 2:
            linguistic_score += 15
        if linguistic_features['punctuation_density'] > 0.15:
            linguistic_score += 10
        
        # Financial context score
        context_score = 0
        if financial_context['urgency_indicators'] > 2:
            context_score += 20
        if financial_context['contact_methods'] > 1:
            context_score += 15
        if financial_context['authority_references'] > 0:
            context_score += 10
        
        # Reduce score for legitimacy indicators
        legitimacy_reduction = financial_context.get('legitimacy_score', 0)
        
        # Calculate final score
        total_score = pattern_score + sentiment_score + linguistic_score + context_score - legitimacy_reduction
        
        return max(0, min(total_score, 100))  # Clamp between 0 and 100
    
    def _generate_recommendations(self, fraud_patterns: Dict, risk_score: float) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        if risk_score > 80:
            recommendations.append("🚨 HIGH RISK: This content shows strong indicators of fraud")
            recommendations.append("Do not share personal or financial information")
            recommendations.append("Report this content to authorities")
        elif risk_score > 60:
            recommendations.append("⚠️ MEDIUM RISK: Exercise extreme caution")
            recommendations.append("Verify all claims through official sources")
        elif risk_score > 30:
            recommendations.append("⚠️ LOW-MEDIUM RISK: Some suspicious elements detected")
            recommendations.append("Research thoroughly before taking any action")
        else:
            recommendations.append("✅ Content appears relatively safe")
            recommendations.append("Still exercise normal caution with financial advice")
        
        # Pattern-specific recommendations
        detected_patterns = fraud_patterns.get('detected_patterns', {})
        
        if 'authority_claims' in detected_patterns:
            recommendations.append("Verify regulatory claims on official websites")
        
        if 'guarantee_indicators' in detected_patterns:
            recommendations.append("Remember: No investment can guarantee returns")
        
        if 'insider_trading' in detected_patterns:
            recommendations.append("Insider trading is illegal - avoid such 'tips'")
        
        if 'payment_requests' in detected_patterns:
            recommendations.append("Never transfer money based on unsolicited advice")
        
        return recommendations
    
    def _create_empty_analysis(self) -> Dict[str, Any]:
        """Create empty analysis for invalid input"""
        return {
            'risk_score': 0,
            'fraud_patterns': {'detected_patterns': {}, 'total_pattern_score': 0},
            'sentiment_analysis': {'sentiment_scores': {}, 'manipulation_score': 0},
            'entity_analysis': {},
            'linguistic_features': {},
            'financial_context': {},
            'recommendations': ['Input too short for meaningful analysis'],
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def batch_analyze(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Analyze multiple texts in batch"""
        results = []
        for i, text in enumerate(texts):
            try:
                analysis = self.analyze_text(text)
                analysis['batch_index'] = i
                results.append(analysis)
            except Exception as e:
                results.append({
                    'batch_index': i,
                    'error': str(e),
                    'risk_score': 0,
                    'analysis_timestamp': datetime.now().isoformat()
                })
        
        return results
    
    def get_analysis_summary(self, analysis_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get summary of batch analysis results"""
        if not analysis_results:
            return {}
        
        valid_results = [r for r in analysis_results if 'error' not in r]
        
        if not valid_results:
            return {'error': 'No valid analyses found'}
        
        risk_scores = [r['risk_score'] for r in valid_results]
        high_risk_count = len([r for r in valid_results if r['risk_score'] > 80])
        medium_risk_count = len([r for r in valid_results if 60 <= r['risk_score'] <= 80])
        
        return {
            'total_analyzed': len(valid_results),
            'average_risk_score': sum(risk_scores) / len(risk_scores),
            'max_risk_score': max(risk_scores),
            'min_risk_score': min(risk_scores),
            'high_risk_count': high_risk_count,
            'medium_risk_count': medium_risk_count,
            'low_risk_count': len(valid_results) - high_risk_count - medium_risk_count,
            'analysis_timestamp': datetime.now().isoformat()
        }

# Example usage
if __name__ == "__main__":
    analyzer = TextAnalyzer()
    
    # Test analysis
    test_text = "Guaranteed 100% returns in 30 days! Join our WhatsApp group for secret insider tips! Call +91-9876543210 now!"
    
    result = analyzer.analyze_text(test_text)
    print(f"Risk Score: {result['risk_score']}")
    print(f"Detected Patterns: {list(result['fraud_patterns']['detected_patterns'].keys())}")
    print(f"Recommendations: {result['recommendations']}")
