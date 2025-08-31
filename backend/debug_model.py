#!/usr/bin/env python3
"""Debug script to test model loading"""

import os
import sys
import pickle

# Add the app directory to the path
sys.path.append('app')

from app.services.content_analysis_service import ContentAnalysisService

def main():
    print("🔍 Testing Enhanced Model Loading...")
    
    # Create service instance
    service = ContentAnalysisService()
    
    # Check if model is loaded
    print(f"Model loaded: {service.ml_model is not None}")
    
    if service.ml_model:
        print(f"Model type: {type(service.ml_model)}")
        if isinstance(service.ml_model, dict):
            print(f"Model keys: {list(service.ml_model.keys())}")
            
            if 'ensemble_model' in service.ml_model:
                print("✅ Enhanced ML model is loaded!")
                print(f"Test accuracy: {service.ml_model.get('test_accuracy', 'N/A')}")
                
                # Test the fraudulent text
                test_text = "URGENT: Fake Corp announces 500% bonus shares and ₹1000 dividend per share. Immediate effect. Contact for verification."
                result = service.analyze_text(test_text)
                
                print(f"\n📊 Test Results:")
                print(f"Risk Score: {result['risk_score']}")
                print(f"Is Suspicious: {result['is_suspicious']}")
                print(f"Fraud Type: {result['fraud_type']}")
                print(f"Confidence: {result['confidence_score']}")
                
            else:
                print("❌ Basic model only")
    else:
        print("❌ No model loaded")

if __name__ == "__main__":
    main()
