from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
import requests
from bs4 import BeautifulSoup
from app.database import get_db
from app.models import ContentAnalysis, ContentAnalysisResponse, UrlAnalysis
from app.services.content_analysis_service import ContentAnalysisService
from app.services.dashboard_service import DashboardService

router = APIRouter()
content_service = ContentAnalysisService()
dashboard_service = DashboardService()

@router.post("/analyze-text", response_model=dict)
async def analyze_text(
    content_data: ContentAnalysis,
    db: Session = Depends(get_db)
):
    """
    Analyze text content for fraud indicators
    """
    try:
        if not content_data.text or len(content_data.text.strip()) < 5:
            raise HTTPException(
                status_code=400,
                detail="Text content is required and must be at least 5 characters long"
            )
        
        # Analyze the content
        analysis_result = content_service.analyze_text(
            content_data.text,
            content_data.source or "manual"
        )
        
        # If content has any risk detected, add to flagged content for monitoring
        if analysis_result['risk_score'] > 30:  # Flag content with medium+ risk for monitoring
            dashboard_service.add_flagged_content({
                'content': content_data.text,
                'source': content_data.source or 'manual',
                'fraud_type': analysis_result['fraud_type'],
                'risk_score': analysis_result['risk_score'],
                'confidence_score': analysis_result['confidence_score'],
                'keywords_found': analysis_result['keywords_found']
            }, db=db)
        
        return {
            "success": True,
            "analysis": analysis_result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/analyze-url")
async def analyze_url(
    url_data: UrlAnalysis,
    db: Session = Depends(get_db)
):
    """
    Analyze content from a URL for fraud indicators
    """
    try:
        if not url_data.url:
            raise HTTPException(status_code=400, detail="URL is required")
        
        url = url_data.url
        source = url_data.source
        
        # Extract text content from URL
        try:
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text_content = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text_content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            clean_text = ' '.join(chunk for chunk in chunks if chunk)
            
            if len(clean_text) < 50:
                raise HTTPException(
                    status_code=400,
                    detail="Unable to extract sufficient text content from URL"
                )
            
        except requests.RequestException as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to fetch content from URL: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to parse content from URL: {str(e)}"
            )
        
        # Analyze the extracted content with URL context
        analysis_result = content_service.analyze_text(clean_text[:2000], source, source_url=url)
        
        # Add URL information to the result
        analysis_result['source_url'] = url
        analysis_result['content_length'] = len(clean_text)
        
        # If content has any risk detected, add to flagged content for monitoring
        if analysis_result['risk_score'] > 30:  # Flag content with medium+ risk for monitoring
            dashboard_service.add_flagged_content({
                'content': clean_text[:500],  # Store first 500 chars
                'source': f"{source}_url",
                'fraud_type': analysis_result['fraud_type'],
                'risk_score': analysis_result['risk_score'],
                'confidence_score': analysis_result['confidence_score'],
                'keywords_found': analysis_result['keywords_found']
            }, db=db)
        
        return {
            "success": True,
            "url_analyzed": url,
            "analysis": analysis_result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"URL analysis failed: {str(e)}")

@router.post("/batch-analyze")
async def batch_analyze_texts(
    texts: list[str],
    source: Optional[str] = "batch",
    db: Session = Depends(get_db)
):
    """
    Analyze multiple texts in batch
    """
    try:
        if not texts or len(texts) == 0:
            raise HTTPException(status_code=400, detail="At least one text is required")
        
        if len(texts) > 50:  # Limit batch size
            raise HTTPException(status_code=400, detail="Maximum 50 texts allowed per batch")
        
        results = []
        suspicious_count = 0
        
        for i, text in enumerate(texts):
            if not text or len(text.strip()) < 5:
                results.append({
                    "index": i,
                    "error": "Text too short or empty",
                    "analysis": None
                })
                continue
            
            try:
                analysis_result = content_service.analyze_text(text, source)
                
                if analysis_result['is_suspicious']:
                    suspicious_count += 1
                    
                    # Add to flagged content if medium+ risk for monitoring
                    if analysis_result['risk_score'] > 30:
                        dashboard_service.add_flagged_content({
                            'content': text,
                            'source': f"{source}_batch",
                            'fraud_type': analysis_result['fraud_type'],
                            'risk_score': analysis_result['risk_score'],
                            'confidence_score': analysis_result['confidence_score'],
                            'keywords_found': analysis_result['keywords_found']
                        }, db=db)
                
                results.append({
                    "index": i,
                    "text_preview": text[:100] + "..." if len(text) > 100 else text,
                    "analysis": analysis_result,
                    "error": None
                })
                
            except Exception as e:
                results.append({
                    "index": i,
                    "error": f"Analysis failed: {str(e)}",
                    "analysis": None
                })
        
        return {
            "success": True,
            "batch_summary": {
                "total_analyzed": len(texts),
                "successful_analyses": len([r for r in results if r["error"] is None]),
                "failed_analyses": len([r for r in results if r["error"] is not None]),
                "suspicious_content_found": suspicious_count,
                "high_risk_content": len([
                    r for r in results 
                    if r["analysis"] and r["analysis"]["risk_score"] > 80
                ])
            },
            "results": results
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")

@router.get("/fraud-keywords")
async def get_fraud_keywords():
    """
    Get list of fraud keywords used in detection
    """
    try:
        return {
            "success": True,
            "fraud_keywords": content_service.fraud_keywords,
            "risk_patterns_count": len(content_service.risk_patterns),
            "legitimate_indicators_count": len(content_service.legitimate_indicators)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get keywords: {str(e)}")

@router.post("/test-detection")
async def test_detection_capability():
    """
    Test the fraud detection capability with sample texts
    """
    try:
        sample_texts = [
            "Guaranteed 100% returns in 30 days! Join our WhatsApp group now!",
            "Mutual fund investments are subject to market risks. Please read all scheme related documents carefully.",
            "Insider tip: Buy this stock immediately for huge profits! Limited time offer!",
            "Our SEBI registered advisors provide personalized investment advice based on your risk profile.",
            "Transfer money now to secure your IPO allotment. Act fast before slots fill up!"
        ]
        
        results = []
        for i, text in enumerate(sample_texts):
            analysis = content_service.analyze_text(text, "test")
            results.append({
                "sample_number": i + 1,
                "text": text,
                "is_suspicious": analysis['is_suspicious'],
                "risk_score": analysis['risk_score'],
                "fraud_type": analysis['fraud_type'],
                "keywords_found": analysis['keywords_found']
            })
        
        return {
            "success": True,
            "test_results": results,
            "detection_summary": {
                "total_samples": len(sample_texts),
                "detected_as_suspicious": len([r for r in results if r["is_suspicious"]]),
                "average_risk_score": round(sum(r["risk_score"] for r in results) / len(results), 1)
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")

@router.get("/detection-stats")
async def get_detection_stats():
    """
    Get fraud detection model statistics
    """
    try:
        return {
            "success": True,
            "model_info": {
                "version": "1.0",
                "detection_categories": list(content_service.fraud_keywords.keys()),
                "total_fraud_keywords": sum(len(keywords) for keywords in content_service.fraud_keywords.values()),
                "risk_patterns": len(content_service.risk_patterns),
                "legitimate_indicators": len(content_service.legitimate_indicators)
            },
            "detection_thresholds": {
                "suspicious_threshold": 50,
                "high_risk_threshold": 80,
                "flagging_threshold": 60
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")
