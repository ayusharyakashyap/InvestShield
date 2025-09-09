import re
import json
import pickle
import numpy as np
from typing import Dict, List, Any, Tuple
from datetime import datetime
import os

class ContentAnalysisService:
    def __init__(self):
        self.fraud_keywords = self._load_fraud_keywords()
        self.risk_patterns = self._load_risk_patterns()
        self.legitimate_indicators = self._load_legitimate_indicators()
        self.trusted_domains = self._load_trusted_domains()
        self.ml_model = self._load_enhanced_model()
    
    def _load_enhanced_model(self):
        """Load the enhanced ML model"""
        try:
            # Try backend directory first
            backend_model_path = os.path.join(os.path.dirname(__file__), '../../fraud_model.pkl')
            models_path = os.path.join(os.path.dirname(__file__), '../../../models')
            model_paths = [
                backend_model_path,
                os.path.join(models_path, 'enhanced_fraud_model.pkl'),
                os.path.join(models_path, 'fraud_model.pkl')
            ]
            
            model_path = None
            for path in model_paths:
                if os.path.exists(path):
                    model_path = path
                    break
            
            
            if model_path and os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    model_data = pickle.load(f)
                    
                # Check if it's the new enhanced model format
                if isinstance(model_data, dict) and 'ensemble_model' in model_data:
                    print(f"✅ Loaded enhanced ML model from {model_path} with {model_data.get('test_accuracy', 0):.3f} accuracy")
                    return model_data
                else:
                    print(f"ℹ️  Loaded basic ML model from {model_path}")
                    return {'basic_model': model_data, 'tfidf_vectorizer': None}
            else:
                print(f"⚠️  No ML model found at any location, using keyword-based analysis only")
                return None
        except Exception as e:
            print(f"❌ Error loading ML model: {e}")
            return None
    
    def _load_fraud_keywords(self) -> Dict[str, List[str]]:
        """Load fraud keywords categorized by type"""
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
            'social_proof_manipulation': [
                'join thousands', 'everyone is buying', 'viral stock', 'trending investment',
                'celebrities investing', 'billionaire secret', 'millionaire strategy'
            ],
            'contact_pressure': [
                'whatsapp immediately', 'call now', 'message for details', 'dm for tips',
                'join telegram', 'click link', 'download app', 'register immediately'
            ],
            'unrealistic_claims': [
                'double money', 'triple returns', 'multiply wealth', '1000% returns',
                'crorepati in days', 'overnight rich', 'instant wealth', 'money multiplication'
            ]
        }
    
    def _load_risk_patterns(self) -> List[Dict[str, Any]]:
        """Load regex patterns for high-risk content"""
        return [
            {
                'pattern': r'\d+%\s*(profit|return|gain)',
                'risk_score': 30,
                'description': 'Specific percentage claims'
            },
            {
                'pattern': r'(rs|₹)\s*\d+\s*(lakh|crore)',
                'risk_score': 25,
                'description': 'Large monetary amounts mentioned'
            },
            {
                'pattern': r'(whatsapp|telegram|dm)\s*(me|for|@)',
                'risk_score': 40,
                'description': 'Solicitation through messaging apps'
            },
            {
                'pattern': r'(buy|invest|purchase)\s*(today|now|immediately)',
                'risk_score': 35,
                'description': 'Pressure to invest immediately'
            },
            {
                'pattern': r'(free|premium)\s*(tips|calls|advice)',
                'risk_score': 20,
                'description': 'Free tip schemes'
            }
        ]
    
    def _load_legitimate_indicators(self) -> List[str]:
        """Load indicators of legitimate content"""
        return [
            'sebi registered', 'mutual fund', 'systematic investment', 'diversification',
            'risk assessment', 'financial planning', 'long term investment', 'portfolio',
            'asset allocation', 'expense ratio', 'fund manager', 'prospectus',
            'regulatory compliance', 'disclosure', 'past performance',
            # Enhanced indicators for regulatory and official sites
            'securities and exchange board', 'reserve bank of india', 'bombay stock exchange',
            'national stock exchange', 'insurance regulatory', 'capital market', 'investor protection',
            'financial services', 'regulatory authority', 'government of india', 'ministry of finance',
            'public sector undertaking', 'authorized dealer', 'licensed entity', 'regulatory framework'
        ]
    
    def _load_trusted_domains(self) -> List[str]:
        """Load list of trusted financial and regulatory domains"""
        return [
            # Indian regulatory bodies
            'sebi.gov.in', 'rbi.org.in', 'irdai.gov.in', 'pfrda.org.in',
            # Stock exchanges
            'bseindia.com', 'nseindia.com', 'mcxindia.com', 'ncdex.com',
            # Government financial portals
            'investindia.gov.in', 'finmin.nic.in', 'cbdt.gov.in', 'incometax.gov.in',
            # Major banks (public sector)
            'sbi.co.in', 'bankofbaroda.in', 'pnbindia.in', 'canarabank.com',
            'bankofindia.co.in', 'unionbankofindia.co.in',
            # Mutual fund companies (major AMCs)
            'icicipruamc.com', 'hdfcfund.com', 'sbifundsoline.com', 'reliancemutual.com',
            # Insurance companies
            'licindia.in', 'newindia.co.in', 'orientalinsurance.org.in',
            # Credit rating agencies
            'crisil.com', 'icra.in', 'careratings.com',
            # Financial education and investor awareness
            'investor.gov.in', 'mfuonline.com', 'amfiindia.com'
        ]
    
    def _is_trusted_domain(self, url: str) -> bool:
        """Check if URL belongs to a trusted domain"""
        if not url:
            return False
        
        try:
            from urllib.parse import urlparse
            parsed_url = urlparse(url if url.startswith(('http://', 'https://')) else f'https://{url}')
            domain = parsed_url.netloc.lower()
            
            # Remove www prefix if present
            if domain.startswith('www.'):
                domain = domain[4:]
            
            return domain in [d.lower() for d in self.trusted_domains]
        except Exception:
            return False
    
    def analyze_text(self, text: str, source: str = "manual", source_url: str = None) -> Dict[str, Any]:
        """Analyze text content for fraud indicators using enhanced ML model"""
        if not text or len(text.strip()) < 10:
            return self._create_analysis_response(
                text, 0, 0, "insufficient_content", False, [], 
                "Content too short for analysis"
            )
        
        text_lower = text.lower()
        
        # Check if content is from a trusted domain
        is_trusted_domain = False
        domain_trust_reduction = 0
        if source_url:
            is_trusted_domain = self._is_trusted_domain(source_url)
            if is_trusted_domain:
                # Significant risk reduction for trusted domains
                domain_trust_reduction = 60  # Reduce risk score by 60 points for trusted domains
        
        # Use enhanced ML model if available
        if self.ml_model and 'ensemble_model' in self.ml_model:
            return self._analyze_with_enhanced_model(text, text_lower, source, is_trusted_domain, domain_trust_reduction)
        else:
            # Fallback to keyword-based analysis
            return self._analyze_with_keywords(text, text_lower, source, is_trusted_domain, domain_trust_reduction)
    
    def _analyze_with_enhanced_model(self, text: str, text_lower: str, source: str, is_trusted_domain: bool = False, domain_trust_reduction: float = 0) -> Dict[str, Any]:
        """Analyze text using the enhanced ML model"""
        try:
            # Validate model components exist
            if not self.ml_model or 'ensemble_model' not in self.ml_model or 'tfidf_vectorizer' not in self.ml_model:
                raise ValueError("Enhanced model components not available")
                
            ensemble_model = self.ml_model['ensemble_model']
            vectorizer = self.ml_model['tfidf_vectorizer']
            
            if ensemble_model is None or vectorizer is None:
                raise ValueError("Model components are None")
            
            # Transform text using the trained vectorizer
            text_tfidf = vectorizer.transform([text])
            
            # Get ML prediction with error handling
            ml_prediction = ensemble_model.predict(text_tfidf)[0]
            ml_probabilities = ensemble_model.predict_proba(text_tfidf)[0]
            
            # Validate probabilities array
            if len(ml_probabilities) < 2:
                raise ValueError("Invalid probability array from model")
            
            # Get fraud probability (class 1)
            fraud_probability = float(ml_probabilities[1] * 100)
            
            # Also run keyword analysis for additional context
            found_keywords = self._find_fraud_keywords(text_lower)
            
            # Validate found_keywords is a dict
            if not isinstance(found_keywords, dict):
                found_keywords = {}
            
            keyword_risk_score = self._calculate_keyword_risk_score(found_keywords)
            
            # Apply domain trust reduction to fraud probability
            adjusted_fraud_probability = max(0, fraud_probability - domain_trust_reduction)
            
            # Combine ML prediction with keyword analysis and domain trust
            final_risk_score = adjusted_fraud_probability
            is_suspicious = bool(ml_prediction == 1 and adjusted_fraud_probability > 60 and not is_trusted_domain)
            
            # For trusted domains, override fraud type to be less severe
            if is_trusted_domain:
                if adjusted_fraud_probability < 30:
                    fraud_type = "legitimate"
                    is_suspicious = False
                else:
                    fraud_type = "low_risk"
                    is_suspicious = False
            else:
                # Determine fraud type with error handling
                try:
                    fraud_type = self._determine_fraud_type_enhanced(text_lower, found_keywords, is_suspicious)
                except Exception as type_error:
                    print(f"Error determining fraud type: {type_error}")
                    fraud_type = "general_fraud" if is_suspicious else "legitimate"
            
            # Generate explanation with domain trust context
            if is_trusted_domain:
                explanation = f"Content from trusted domain. Risk assessment: {adjusted_fraud_probability:.1f}%. Domain verification provides additional security."
            elif adjusted_fraud_probability > 80:
                explanation = f"High fraud risk detected by ML model ({adjusted_fraud_probability:.1f}% confidence). Found {sum(len(kw) for kw in found_keywords.values())} fraud-related keywords."
            elif adjusted_fraud_probability > 60:
                explanation = f"Medium fraud risk detected by ML model ({adjusted_fraud_probability:.1f}% confidence). Exercise caution."
            elif adjusted_fraud_probability > 40:
                explanation = f"Some suspicious patterns detected ({adjusted_fraud_probability:.1f}% risk). Verify independently."
            else:
                explanation = "Content appears legitimate with no significant fraud indicators detected."
            
            # Generate recommendations with error handling
            try:
                recommendations = self._generate_enhanced_recommendations(adjusted_fraud_probability, found_keywords)
                if is_trusted_domain:
                    recommendations.insert(0, "Content verified from trusted regulatory domain")
            except Exception as rec_error:
                print(f"Error generating recommendations: {rec_error}")
                recommendations = ["Exercise caution and verify independently"]
            
            # Format keywords safely
            try:
                formatted_keywords = self._format_found_keywords(found_keywords)
            except Exception as format_error:
                print(f"Error formatting keywords: {format_error}")
                formatted_keywords = []
            
            return self._create_analysis_response(
                text, final_risk_score, adjusted_fraud_probability, fraud_type, 
                is_suspicious, formatted_keywords, explanation, recommendations
            )
            
        except Exception as e:
            print(f"❌ Error in enhanced ML analysis: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to keyword analysis
            return self._analyze_with_keywords(text, text_lower, source, is_trusted_domain, domain_trust_reduction)
    
    def _analyze_with_keywords(self, text: str, text_lower: str, source: str, is_trusted_domain: bool = False, domain_trust_reduction: float = 0) -> Dict[str, Any]:
        """Fallback keyword-based analysis"""
        
        # Find fraud keywords
        found_keywords = self._find_fraud_keywords(text_lower)
        
        # Calculate keyword-based risk score
        keyword_risk_score = self._calculate_keyword_risk_score(found_keywords)
        
        # Find pattern matches
        pattern_matches = self._find_pattern_matches(text_lower)
        pattern_risk_score = sum(match['risk_score'] for match in pattern_matches)
        
        # Check for legitimate indicators
        legitimate_score = self._calculate_legitimate_score(text_lower)
        
        # Apply domain trust reduction
        total_trust_reduction = legitimate_score + domain_trust_reduction
        
        # Calculate final scores with domain trust consideration
        base_risk_score = max(0, min(keyword_risk_score + pattern_risk_score - total_trust_reduction, 100))
        confidence_score = self._calculate_confidence_score(found_keywords, pattern_matches, len(text))
        
        # For trusted domains, override fraud assessment
        if is_trusted_domain:
            if base_risk_score < 40:
                fraud_type = "legitimate"
                is_suspicious = False
                base_risk_score = min(base_risk_score, 20)  # Cap at 20 for trusted domains
            else:
                fraud_type = "low_risk"
                is_suspicious = False
                base_risk_score = min(base_risk_score, 35)  # Cap at 35 for trusted domains
        else:
            # Determine fraud type
            fraud_type = self._determine_fraud_type(found_keywords, pattern_matches)
            # Determine if suspicious
            is_suspicious = base_risk_score > 50
        
        # Generate explanation and recommendations
        explanation = self._generate_explanation(
            found_keywords, pattern_matches, base_risk_score, is_suspicious
        )
        recommendations = self._generate_recommendations(fraud_type, is_suspicious, base_risk_score)
        
        return self._create_analysis_response(
            text, base_risk_score, confidence_score, fraud_type, is_suspicious,
            self._format_found_keywords(found_keywords), explanation, recommendations
        )
    
    def _find_fraud_keywords(self, text: str) -> Dict[str, List[str]]:
        """Find fraud keywords in text"""
        found_keywords = {}
        
        for category, keywords in self.fraud_keywords.items():
            found_in_category = []
            for keyword in keywords:
                if keyword in text:
                    found_in_category.append(keyword)
            
            if found_in_category:
                found_keywords[category] = found_in_category
        
        return found_keywords
    
    def _find_pattern_matches(self, text: str) -> List[Dict[str, Any]]:
        """Find regex pattern matches"""
        matches = []
        
        for pattern_info in self.risk_patterns:
            pattern = pattern_info['pattern']
            if re.search(pattern, text, re.IGNORECASE):
                matches.append({
                    'pattern': pattern,
                    'risk_score': pattern_info['risk_score'],
                    'description': pattern_info['description']
                })
        
        return matches
    
    def _calculate_keyword_risk_score(self, found_keywords: Dict[str, List[str]]) -> float:
        """Calculate risk score based on found keywords"""
        category_weights = {
            'guaranteed_returns': 25,
            'urgency_pressure': 20,
            'insider_trading': 30,
            'fake_credentials': 25,
            'social_proof_manipulation': 15,
            'contact_pressure': 20,
            'unrealistic_claims': 30
        }
        
        total_score = 0
        for category, keywords in found_keywords.items():
            weight = category_weights.get(category, 10)
            # Each keyword in category adds weight, but with diminishing returns
            category_score = weight * min(len(keywords), 3) / 3
            total_score += category_score
        
        return min(total_score, 80)  # Cap at 80 for keyword-based scoring
    
    def _calculate_legitimate_score(self, text: str) -> float:
        """Calculate score reduction for legitimate indicators"""
        legitimate_count = 0
        for indicator in self.legitimate_indicators:
            if indicator in text:
                legitimate_count += 1
        
        # Each legitimate indicator reduces risk by 5 points, max 25 points
        return min(legitimate_count * 5, 25)
    
    def _calculate_confidence_score(self, found_keywords: Dict, pattern_matches: List, text_length: int) -> float:
        """Calculate confidence score for the analysis"""
        base_confidence = 50
        
        # More keywords = higher confidence
        keyword_count = sum(len(keywords) for keywords in found_keywords.values())
        confidence_boost = min(keyword_count * 10, 30)
        
        # Pattern matches boost confidence
        pattern_boost = min(len(pattern_matches) * 5, 15)
        
        # Longer text = higher confidence (up to a point)
        length_boost = min(text_length / 100, 5)
        
        return min(base_confidence + confidence_boost + pattern_boost + length_boost, 95)
    
    def _determine_fraud_type(self, found_keywords: Dict, pattern_matches: List) -> str:
        """Determine the primary type of fraud"""
        if not found_keywords and not pattern_matches:
            return "legitimate"
        
        # Count keywords in each category
        category_scores = {}
        for category, keywords in found_keywords.items():
            category_scores[category] = len(keywords)
        
        if not category_scores:
            return "suspicious_patterns"
        
        # Return category with most keywords
        primary_category = max(category_scores.items(), key=lambda x: x[1])[0]
        
        category_mapping = {
            'guaranteed_returns': 'guaranteed_returns_scam',
            'urgency_pressure': 'pressure_tactics',
            'insider_trading': 'insider_trading_scam',
            'fake_credentials': 'fake_advisor',
            'social_proof_manipulation': 'social_manipulation',
            'contact_pressure': 'contact_scam',
            'unrealistic_claims': 'unrealistic_promises'
        }
        
        return category_mapping.get(primary_category, 'general_fraud')
    
    def _generate_explanation(self, found_keywords: Dict, pattern_matches: List, 
                            risk_score: float, is_suspicious: bool) -> str:
        """Generate human-readable explanation"""
        if not is_suspicious:
            return "Content appears legitimate with no significant fraud indicators detected."
        
        explanations = []
        
        if found_keywords:
            keyword_count = sum(len(keywords) for keywords in found_keywords.values())
            explanations.append(f"Found {keyword_count} fraud-related keywords")
        
        if pattern_matches:
            explanations.append(f"Detected {len(pattern_matches)} suspicious patterns")
        
        if risk_score > 80:
            severity = "very high"
        elif risk_score > 60:
            severity = "high"
        else:
            severity = "moderate"
        
        base_explanation = f"Content shows {severity} risk of being fraudulent"
        
        if explanations:
            return f"{base_explanation}. {', '.join(explanations)}."
        else:
            return base_explanation + "."
    
    def _extract_financial_features(self, content: str) -> Dict[str, Any]:
        """Extract financial features for enhanced model"""
        import re
        
        features = {}
        
        # Percentage mentions
        percent_pattern = r'\b\d+(?:\.\d+)?%'
        percentages = re.findall(percent_pattern, content)
        features['has_percentage'] = len(percentages) > 0
        features['high_percentages'] = any(float(p[:-1]) > 20 for p in percentages if p[:-1].replace('.', '').isdigit())
        
        # Money amounts
        money_pattern = r'\$[\d,]+(?:\.\d{2})?|\b\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:dollars?|USD|INR|rupees?)\b'
        money_mentions = re.findall(money_pattern, content, re.IGNORECASE)
        features['has_money_amounts'] = len(money_mentions) > 0
        
        # Time pressure indicators
        urgency_words = ['urgent', 'immediately', 'limited time', 'act now', 'expires', 'deadline']
        features['urgency_score'] = sum(1 for word in urgency_words if word.lower() in content.lower())
        
        # Contact information
        features['has_phone'] = bool(re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', content))
        features['has_email'] = bool(re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content))
        
        # Social proof claims
        social_proof = ['testimonial', 'success story', 'profit', 'earned', 'made money']
        features['social_proof_score'] = sum(1 for phrase in social_proof if phrase.lower() in content.lower())
        
        return features
    
    def _generate_recommendations(self, fraud_type: str, is_suspicious: bool, risk_score: float) -> List[str]:
        """Generate recommendations based on analysis"""
        if not is_suspicious:
            return [
                "Content appears legitimate, but always exercise caution",
                "Verify any investment advice independently",
                "Check advisor credentials before investing"
            ]
        
        recommendations = [
            "⚠️ High fraud risk detected - proceed with extreme caution",
            "Do not share personal or financial information",
            "Verify any claims through official channels"
        ]
        
        if fraud_type == "fake_advisor":
            recommendations.extend([
                "Verify advisor credentials on SEBI website",
                "Check for valid SEBI registration number"
            ])
        elif fraud_type == "guaranteed_returns_scam":
            recommendations.extend([
                "No investment can guarantee returns",
                "Be wary of unrealistic profit promises"
            ])
        elif fraud_type == "contact_scam":
            recommendations.extend([
                "Avoid sharing contact details",
                "Do not join unknown groups or click suspicious links"
            ])
        
        if risk_score > 80:
            recommendations.append("🚨 Consider reporting this content to authorities")
        
        return recommendations
    
    def _format_found_keywords(self, found_keywords: Dict) -> List[str]:
        """Format found keywords for response"""
        all_keywords = []
        for category, keywords in found_keywords.items():
            all_keywords.extend(keywords)
        return all_keywords
    
    def _create_analysis_response(self, text: str, risk_score: float, confidence_score: float,
                                fraud_type: str, is_suspicious: bool, keywords_found: List[str],
                                explanation: str, recommendations: List[str] = None) -> Dict[str, Any]:
        """Create standardized analysis response"""
        return {
            'text_analyzed': text[:200] + "..." if len(text) > 200 else text,
            'risk_score': round(risk_score, 1),
            'confidence_score': round(confidence_score, 1),
            'fraud_type': fraud_type,
            'is_suspicious': is_suspicious,
            'keywords_found': keywords_found,
            'explanation': explanation,
            'recommendations': recommendations or [],
            'analysis_timestamp': datetime.now().isoformat(),
            'analysis_version': '1.0'
        }
    
    def _determine_fraud_type_enhanced(self, text_lower: str, found_keywords: Dict, is_suspicious: bool) -> str:
        """Determine fraud type using enhanced logic"""
        if not is_suspicious:
            return "legitimate"
        
        # Check for specific fraud patterns
        if any(word in text_lower for word in ["500%", "1000%", "2000%", "guaranteed", "guarantee"]):
            return "guaranteed_returns_scam"
        
        if any(word in text_lower for word in ["urgent", "immediate", "limited time", "act now"]):
            return "pressure_tactics"
        
        if any(word in text_lower for word in ["insider", "exclusive", "secret", "confidential"]):
            return "insider_trading_scam"
        
        if any(word in text_lower for word in ["sebi", "certified", "licensed", "approved"]):
            return "fake_advisor"
        
        # Use keyword-based determination as fallback
        return self._determine_fraud_type(found_keywords, [])
    
    def _generate_enhanced_recommendations(self, fraud_probability: float, found_keywords: Dict) -> List[str]:
        """Generate recommendations based on ML analysis"""
        recommendations = []
        
        if fraud_probability > 80:
            recommendations.extend([
                "🚨 CRITICAL ALERT: This content shows extremely high fraud risk",
                "Do NOT provide any personal or financial information",
                "Do NOT make any payments or investments",
                "Report this content to authorities immediately"
            ])
        elif fraud_probability > 60:
            recommendations.extend([
                "⚠️ HIGH RISK: Exercise extreme caution with this content",
                "Verify all claims through official channels",
                "Do not share personal information",
                "Consult with licensed financial advisors"
            ])
        elif fraud_probability > 40:
            recommendations.extend([
                "⚠️ MEDIUM RISK: Some suspicious patterns detected",
                "Verify the source and claims independently",
                "Be cautious about sharing information",
                "Cross-check with official sources"
            ])
        else:
            recommendations.extend([
                "Content appears legitimate, but always exercise caution",
                "Verify any investment advice independently",
                "Check advisor credentials before investing"
            ])
        
        return recommendations
