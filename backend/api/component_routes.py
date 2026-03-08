from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict
import uuid
import logging

from database import get_db
from models import (
    ComponentListRequest, ProductRankingRequest, ProductSelectionRequest,
    ProductRankingResponse, ComponentSelectionResponse
)
from services.component_service import ComponentService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/components", tags=["components"])
component_service = ComponentService()

@router.post("/", response_model=Dict)
async def submit_components(request: ComponentListRequest):
    """Submit a list of components for processing"""
    try:
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Process components
        result = component_service.process_components(request.components, session_id)
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        
        return result
        
    except Exception as e:
        logger.error(f"Error submitting components: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products/{component_name}", response_model=ProductRankingResponse)
async def get_ranked_products(component_name: str, session_id: str):
    """Get top ranked products for a specific component"""
    try:
        result = component_service.get_ranked_products(component_name, session_id)
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        
        if result["status"] == "no_products":
            return ProductRankingResponse(
                component_name=component_name,
                top_products=[]
            )
        
        return ProductRankingResponse(
            component_name=component_name,
            top_products=result["top_products"]
        )
        
    except Exception as e:
        logger.error(f"Error getting ranked products: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/select", response_model=Dict)
async def select_product(request: ProductSelectionRequest):
    """Save user's product selection"""
    try:
        result = component_service.select_product(
            request.component_name,
            request.product_id,
            request.session_id
        )
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        
        return result
        
    except Exception as e:
        logger.error(f"Error selecting product: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/selections/{session_id}", response_model=List[Dict])
async def get_session_selections(session_id: str):
    """Get all selections for a session"""
    try:
        selections = component_service.get_session_selections(session_id)
        return selections
        
    except Exception as e:
        logger.error(f"Error getting session selections: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Component service is running"}
