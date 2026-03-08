from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse
from typing import List, Dict
import logging
import os

from models import ReportRequest, ReportResponse
from services.report_service import ReportService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reports", tags=["reports"])
report_service = ReportService()

@router.post("/generate", response_model=ReportResponse)
async def generate_report(request: ReportRequest):
    """Generate procurement report for a session"""
    try:
        result = report_service.generate_procurement_report(request.session_id)
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        
        return ReportResponse(
            message=result["message"],
            download_url=result.get("download_url")
        )
        
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{filename}")
async def download_report(filename: str):
    """Download a generated report"""
    try:
        filepath = report_service.get_report_file(filename)
        
        if not filepath:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list", response_model=List[Dict])
async def list_reports():
    """List all available reports"""
    try:
        reports = report_service.list_reports()
        return reports
        
    except Exception as e:
        logger.error(f"Error listing reports: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{filename}")
async def delete_report(filename: str):
    """Delete a report"""
    try:
        filepath = report_service.get_report_file(filename)
        
        if not filepath:
            raise HTTPException(status_code=404, detail="Report not found")
        
        os.remove(filepath)
        
        return {"status": "success", "message": f"Report {filename} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Report service is running"}
