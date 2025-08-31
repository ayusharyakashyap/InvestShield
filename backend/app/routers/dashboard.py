from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta
from app.database import get_db
from app.services.dashboard_service import DashboardService
from app.services.advisor_service import AdvisorVerificationService

router = APIRouter()
dashboard_service = DashboardService()
advisor_service = AdvisorVerificationService()

@router.get("/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Get comprehensive dashboard statistics
    """
    try:
        # Get fraud detection stats with database session
        fraud_stats = dashboard_service.get_dashboard_stats(db=db)
        
        # Get advisor stats
        advisor_stats = advisor_service.get_advisor_stats()
        
        # Combine statistics
        combined_stats = {
            "fraud_detection": fraud_stats,
            "advisor_verification": advisor_stats,
            "summary": {
                "total_advisors": advisor_stats.get('total_advisors', 0),
                "verified_advisors": advisor_stats.get('active_advisors', 0),
                "flagged_content_today": fraud_stats.get('flagged_content_today', 0),
                "flagged_content_week": fraud_stats.get('flagged_content_week', 0),
                "avg_risk_score": fraud_stats.get('average_risk_score', 0),
                "high_risk_alerts": fraud_stats.get('high_risk_content', 0)
            },
            "updated_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "dashboard_stats": combined_stats
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard stats: {str(e)}")

@router.get("/flagged-content")
async def get_flagged_content(
    limit: int = Query(50, ge=1, le=200),
    fraud_type: Optional[str] = None,
    min_risk_score: Optional[float] = Query(None, ge=0, le=100),
    source: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get flagged content with filtering options
    """
    try:
        result = dashboard_service.get_flagged_content(
            limit=limit,
            fraud_type=fraud_type,
            min_risk_score=min_risk_score,
            db=db
        )
        
        # Apply source filter if provided
        if source:
            filtered_content = [
                content for content in result['flagged_content']
                if source.lower() in content['source'].lower()
            ]
            result['flagged_content'] = filtered_content
            result['total_found'] = len(filtered_content)
            result['showing'] = len(filtered_content)
            result['filters_applied']['source'] = source
        
        return {
            "success": True,
            "flagged_content_data": result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get flagged content: {str(e)}")

@router.get("/trends")
async def get_trends(
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """
    Get fraud trend analysis
    """
    try:
        trends = dashboard_service.get_trend_analysis(days=days, db=db)
        
        return {
            "success": True,
            "trend_analysis": trends
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trends: {str(e)}")

@router.get("/alerts")
async def get_recent_alerts(
    limit: int = Query(10, ge=1, le=50),
    min_risk_score: float = Query(80.0, ge=0, le=100),
    db: Session = Depends(get_db)
):
    """
    Get recent high-risk alerts
    """
    try:
        flagged_data = dashboard_service.get_flagged_content(
            limit=limit,
            min_risk_score=min_risk_score
        )
        
        # Format alerts with additional metadata
        alerts = []
        for content in flagged_data['flagged_content']:
            alert = {
                "id": content['id'],
                "content_preview": content['content_text'][:150] + "..." if len(content['content_text']) > 150 else content['content_text'],
                "source": content['source'],
                "fraud_type": content['fraud_type'],
                "risk_score": content['risk_score'],
                "confidence_score": content['confidence_score'],
                "created_at": content['created_at'],
                "time_ago": content['time_ago'],
                "keywords_found": content['keywords_found'][:5],  # Limit to 5 keywords
                "severity": _get_severity_level(content['risk_score']),
                "action_required": _get_action_required(content['risk_score'], content['fraud_type'])
            }
            alerts.append(alert)
        
        return {
            "success": True,
            "recent_alerts": {
                "alerts": alerts,
                "total_alerts": len(alerts),
                "criteria": {
                    "min_risk_score": min_risk_score,
                    "limit": limit
                },
                "generated_at": datetime.now().isoformat()
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alerts: {str(e)}")

def _get_severity_level(risk_score: float) -> str:
    """Get severity level based on risk score"""
    if risk_score >= 90:
        return "CRITICAL"
    elif risk_score >= 80:
        return "HIGH"
    elif risk_score >= 60:
        return "MEDIUM"
    elif risk_score >= 40:
        return "LOW"
    else:
        return "MINIMAL"

def _get_action_required(risk_score: float, fraud_type: str) -> List[str]:
    """Get recommended actions based on risk score and fraud type"""
    actions = []
    
    if risk_score >= 90:
        actions.extend([
            "IMMEDIATE INVESTIGATION REQUIRED",
            "Block/Remove content if possible",
            "Alert relevant authorities"
        ])
    elif risk_score >= 80:
        actions.extend([
            "Review content within 24 hours",
            "Consider content removal",
            "Monitor for similar patterns"
        ])
    elif risk_score >= 60:
        actions.extend([
            "Schedule review within 48 hours",
            "Add to monitoring list"
        ])
    
    # Fraud type specific actions
    if fraud_type == "fake_advisor":
        actions.append("Verify advisor credentials with SEBI")
    elif fraud_type == "insider_trading_scam":
        actions.append("Report to market surveillance")
    elif fraud_type == "guaranteed_returns_scam":
        actions.append("Issue public warning about unrealistic promises")
    
    return actions

@router.get("/export")
async def export_data(
    format_type: str = Query("json", regex="^(json|csv)$"),
    days: int = Query(30, ge=1, le=365),
    min_risk_score: Optional[float] = Query(None, ge=0, le=100),
    db: Session = Depends(get_db)
):
    """
    Export flagged content data
    """
    try:
        export_data = dashboard_service.get_export_data(format_type=format_type)
        
        # Filter by days if needed
        if days < 365:
            cutoff_date = datetime.now() - timedelta(days=days)
            filtered_data = [
                item for item in export_data['data']
                if datetime.fromisoformat(item['created_at']) >= cutoff_date
            ]
            export_data['data'] = filtered_data
            export_data['total_records'] = len(filtered_data)
        
        # Filter by risk score if needed
        if min_risk_score is not None:
            filtered_data = [
                item for item in export_data['data']
                if item['risk_score'] >= min_risk_score
            ]
            export_data['data'] = filtered_data
            export_data['total_records'] = len(filtered_data)
        
        return {
            "success": True,
            "export_data": export_data,
            "filters_applied": {
                "days": days,
                "min_risk_score": min_risk_score,
                "format": format_type
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@router.get("/charts/fraud-types")
async def get_fraud_types_chart_data(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get data for fraud types chart
    """
    try:
        stats = dashboard_service.get_dashboard_stats()
        
        # Prepare chart data
        chart_data = {
            "labels": [item['type'] for item in stats['top_fraud_types']],
            "data": [item['count'] for item in stats['top_fraud_types']],
            "total": sum(item['count'] for item in stats['top_fraud_types']),
            "chart_type": "pie",
            "title": f"Top Fraud Types (Last {days} days)"
        }
        
        return {
            "success": True,
            "chart_data": chart_data
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get chart data: {str(e)}")

@router.get("/charts/risk-distribution")
async def get_risk_distribution_chart_data(db: Session = Depends(get_db)):
    """
    Get data for risk score distribution chart
    """
    try:
        stats = dashboard_service.get_dashboard_stats()
        
        chart_data = {
            "labels": [item['label'] for item in stats['risk_score_distribution']],
            "data": [item['count'] for item in stats['risk_score_distribution']],
            "ranges": [item['range'] for item in stats['risk_score_distribution']],
            "total": sum(item['count'] for item in stats['risk_score_distribution']),
            "chart_type": "bar",
            "title": "Risk Score Distribution"
        }
        
        return {
            "success": True,
            "chart_data": chart_data
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get risk distribution: {str(e)}")

@router.get("/summary")
async def get_summary_metrics(db: Session = Depends(get_db)):
    """
    Get key summary metrics for dashboard widgets
    """
    try:
        stats = dashboard_service.get_dashboard_stats()
        advisor_stats = advisor_service.get_advisor_stats()
        
        summary = {
            "key_metrics": {
                "total_flagged_content": stats.get('total_flagged_content', 0),
                "high_risk_content": stats.get('high_risk_content', 0),
                "content_flagged_today": stats.get('flagged_content_today', 0),
                "content_flagged_this_week": stats.get('flagged_content_week', 0),
                "average_risk_score": stats.get('average_risk_score', 0),
                "total_advisors": advisor_stats.get('total_advisors', 0),
                "active_advisors": advisor_stats.get('active_advisors', 0),
                "suspended_advisors": advisor_stats.get('suspended_advisors', 0)
            },
            "fraud_types_summary": stats.get('top_fraud_types', [])[:3],  # Top 3
            "recent_alerts_count": len([
                alert for alert in stats.get('recent_high_risk_alerts', [])
                if alert.get('risk_score', 0) > 85
            ]),
            "detection_efficiency": {
                "total_content_analyzed": stats.get('total_flagged_content', 0),
                "high_confidence_detections": len([
                    content for content in stats.get('recent_high_risk_alerts', [])
                    if content.get('risk_score', 0) > 80
                ])
            },
            "last_updated": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "summary_metrics": summary
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")
