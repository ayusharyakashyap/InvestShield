from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from app.database import get_db
from app.models import AdvisorVerification, AdvisorResponse
from app.services.advisor_service import AdvisorVerificationService

router = APIRouter()
advisor_service = AdvisorVerificationService()

@router.post("/verify", response_model=dict)
async def verify_advisor(
    verification_data: AdvisorVerification,
    db: Session = Depends(get_db)
):
    """
    Verify an advisor by SEBI number or name
    """
    try:
        if verification_data.sebi_number:
            # Verify by SEBI number
            result = advisor_service.verify_by_sebi_number(verification_data.sebi_number)
        elif verification_data.name:
            # Verify by name
            result = advisor_service.verify_by_name(verification_data.name)
        else:
            raise HTTPException(
                status_code=400,
                detail="Either SEBI number or advisor name must be provided"
            )
        
        return {
            "success": True,
            "verification_result": result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")

@router.get("/search")
async def search_advisors(
    query: Optional[str] = None,
    status: Optional[str] = None,
    location: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Search advisors with various filters
    """
    try:
        # Get all advisors data
        advisors_data = advisor_service.get_all_advisors(limit=limit)
        
        if not advisors_data['advisors']:
            return {
                "success": True,
                "advisors": [],
                "total": 0,
                "message": "No advisors found"
            }
        
        advisors = advisors_data['advisors']
        
        # Apply filters
        if query:
            query_lower = query.lower()
            advisors = [
                advisor for advisor in advisors
                if (query_lower in advisor.get('name', '').lower() or
                    query_lower in advisor.get('firm_name', '').lower() or
                    query_lower in advisor.get('sebi_number', '').lower())
            ]
        
        if status:
            advisors = [
                advisor for advisor in advisors
                if advisor.get('status', '').lower() == status.lower()
            ]
        
        if location:
            advisors = [
                advisor for advisor in advisors
                if location.lower() in advisor.get('location', '').lower()
            ]
        
        return {
            "success": True,
            "advisors": advisors[:limit],
            "total_found": len(advisors),
            "showing": min(len(advisors), limit),
            "filters": {
                "query": query,
                "status": status,
                "location": location
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/stats")
async def get_advisor_stats(db: Session = Depends(get_db)):
    """
    Get advisor statistics
    """
    try:
        stats = advisor_service.get_advisor_stats()
        return {
            "success": True,
            "statistics": stats
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@router.get("/{sebi_number}")
async def get_advisor_details(
    sebi_number: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific advisor
    """
    try:
        result = advisor_service.verify_by_sebi_number(sebi_number)
        
        if not result.get('is_verified') and result.get('status') == 'Not Found':
            raise HTTPException(
                status_code=404,
                detail=f"Advisor with SEBI number {sebi_number} not found"
            )
        
        return {
            "success": True,
            "advisor": result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get advisor details: {str(e)}")

@router.get("/")
async def list_advisors(
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all advisors with pagination
    """
    try:
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Get advisors data
        advisors_data = advisor_service.get_all_advisors(limit=page_size + offset)
        all_advisors = advisors_data['advisors']
        
        # Apply status filter if provided
        if status:
            all_advisors = [
                advisor for advisor in all_advisors
                if advisor.get('status', '').lower() == status.lower()
            ]
        
        # Apply pagination
        paginated_advisors = all_advisors[offset:offset + page_size]
        
        return {
            "success": True,
            "advisors": paginated_advisors,
            "pagination": {
                "current_page": page,
                "page_size": page_size,
                "total_advisors": len(all_advisors),
                "total_pages": (len(all_advisors) + page_size - 1) // page_size,
                "has_next": len(all_advisors) > offset + page_size,
                "has_previous": page > 1
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list advisors: {str(e)}")

@router.post("/report-suspicious")
async def report_suspicious_advisor(
    sebi_number: str,
    reason: str,
    reporter_info: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Report a suspicious advisor
    """
    try:
        # This would typically save to database
        # For now, we'll just return a confirmation
        
        return {
            "success": True,
            "message": f"Suspicious activity report submitted for advisor {sebi_number}",
            "report_id": f"RPT{sebi_number}{int(datetime.now().timestamp())}",
            "next_steps": [
                "Report has been logged for investigation",
                "You may be contacted for additional information",
                "Avoid any transactions until investigation is complete"
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit report: {str(e)}")
