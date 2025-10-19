"""
Hypothesis generation API routes
Handles hypothesis creation, retrieval, and management
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, status
from loguru import logger
from typing import List, Any, Dict
import uuid
from datetime import datetime

from medical_discovery.api.schemas.hypothesis import (
    HypothesisRequest,
    HypothesisCreateResponse,
    HypothesisResponse,
    HypothesisStatus,
    ErrorResponse
)
from medical_discovery.services.orchestrator import HypothesisOrchestrator
from medical_discovery.config import settings
from medical_discovery.data.mongo.hypothesis_repository import hypothesis_repository
from medical_discovery.data.mongo.client import mongodb_client


router = APIRouter()

# Initialize orchestrator
orchestrator = HypothesisOrchestrator()

# In-memory fallback storage (used if MongoDB is not available)
hypothesis_store = {}


def sanitize_for_response(data: Any) -> Any:
    """
    Sanitize data for JSON response, ensuring all fields are serializable
    Recursively handles nested structures and maps agent outputs to schema format
    """
    if data is None:
        return None
    elif isinstance(data, datetime):
        return data.isoformat()
    elif isinstance(data, dict):
        # Remove MongoDB _id
        cleaned = {k: sanitize_for_response(v) for k, v in data.items() if k != "_id"}
        
        # MAP AGENT OUTPUTS TO SCHEMA FORMAT
        # Fix hypothesis_document: ensure clinical_rationale exists
        if "mechanism_of_action" in cleaned and "clinical_rationale" not in cleaned:
            # Generate clinical_rationale from available fields
            mechanism = cleaned.get("mechanism_of_action", "")
            outcomes = cleaned.get("expected_outcomes", "")
            targets = cleaned.get("molecular_targets", [])
            
            rationale_parts = []
            if mechanism:
                rationale_parts.append(f"This approach is justified by its {mechanism[:100]}...")
            if targets:
                rationale_parts.append(f"Targeting {', '.join(targets[:2])} provides a rational therapeutic strategy.")
            if outcomes:
                rationale_parts.append(f"Expected outcomes include {outcomes[:100]}...")
            
            cleaned["clinical_rationale"] = " ".join(rationale_parts) if rationale_parts else "Clinical validation required to establish therapeutic rationale."
        
        # Fix cross_domain transfers: map concept_transferred -> concept, add potential_impact
        if "source_domain" in cleaned and "target_domain" in cleaned:
            # This is a cross-domain transfer object
            if "concept" not in cleaned:
                cleaned["concept"] = cleaned.get("concept_transferred") or cleaned.get("proposed_application") or f"Innovation from {cleaned.get('source_domain', 'source')}"
            
            if "potential_impact" not in cleaned:
                rationale = cleaned.get("rationale", "")
                cleaned["potential_impact"] = cleaned.get("proposed_application") or f"Cross-domain transfer with therapeutic potential. {rationale[:100]}" if rationale else "Requires validation to assess clinical impact."
        
        return cleaned
    elif isinstance(data, list):
        return [sanitize_for_response(item) for item in data]
    elif isinstance(data, (str, int, float, bool)):
        return data
    elif hasattr(data, "model_dump"):  # Pydantic model
        return sanitize_for_response(data.model_dump())
    elif hasattr(data, "__dict__"):  # Object with __dict__
        return sanitize_for_response(data.__dict__)
    else:
        # Fallback: convert to string
        return str(data)


async def generate_hypothesis_async(hypothesis_id: str, request: HypothesisRequest):
    """
    Background task to generate hypothesis
    This will be executed asynchronously
    """
    try:
        logger.info(f"Starting hypothesis generation for ID: {hypothesis_id}")
        
        # Update status to running
        update_data = {
            "status": HypothesisStatus.RUNNING.value,
            "updated_at": datetime.utcnow()
        }
        
        # Try MongoDB first, fallback to in-memory
        if await mongodb_client.is_connected():
            await hypothesis_repository.update(hypothesis_id, update_data)
        elif hypothesis_id in hypothesis_store:
            hypothesis_store[hypothesis_id].update(update_data)
        
        # Run orchestrator to generate hypothesis
        result = await orchestrator.generate_hypothesis(hypothesis_id, request)
        
        # Prepare update data
        update_data = {
            "status": HypothesisStatus.COMPLETED.value,
            "summary": result.get("summary"),
            "concept_map": result.get("concept_map"),
            "hypothesis_document": result.get("hypothesis_document"),
            "evidence_packs": result.get("evidence_packs", []),
            "cross_domain_transfers": result.get("cross_domain_transfers", []),
            "simulation_scorecard": result.get("simulation_scorecard"),
            "ethics_report": result.get("ethics_report"),
            "provenance": result.get("provenance", []),
            # Nobel Phase 2: Executive Summary
            "executive_summary": result.get("executive_summary"),
            # Nobel Phase 1: Transparent Reasoning
            "reasoning_steps": result.get("reasoning_steps", []),
            "reasoning_narrative": result.get("reasoning_narrative"),
            "reasoning_narrative_json": result.get("reasoning_narrative_json"),  # Structured format
            "reasoning_flowchart": result.get("reasoning_flowchart"),
            "completed_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Update storage
        if await mongodb_client.is_connected():
            await hypothesis_repository.update(hypothesis_id, update_data)
        elif hypothesis_id in hypothesis_store:
            hypothesis_store[hypothesis_id].update(update_data)
        
        logger.success(f"Hypothesis {hypothesis_id} generated successfully")
        
    except Exception as e:
        logger.exception(f"Error generating hypothesis {hypothesis_id}: {str(e)}")
        
        # Update status to failed
        update_data = {
            "status": HypothesisStatus.FAILED.value,
            "error_message": str(e),
            "updated_at": datetime.utcnow()
        }
        
        if await mongodb_client.is_connected():
            await hypothesis_repository.update(hypothesis_id, update_data)
        elif hypothesis_id in hypothesis_store:
            hypothesis_store[hypothesis_id].update(update_data)


@router.post(
    "/hypotheses",
    response_model=HypothesisCreateResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Create a new hypothesis",
    description="Initiates hypothesis generation process. Returns immediately with hypothesis ID while processing continues in background."
)
async def create_hypothesis(
    request: HypothesisRequest,
    background_tasks: BackgroundTasks
):
    """
    Create a new hypothesis generation request
    
    The hypothesis generation is an asynchronous process that:
    1. Generates initial ideas (Visioner Agent)
    2. Creates concept map (Concept Learner)
    3. Gathers evidence (Evidence Miners)
    4. Finds cross-domain transfers (Cross-Domain Mapper)
    5. Synthesizes hypothesis (Synthesizer)
    6. Runs simulations (Simulation Agent)
    7. Validates ethics (Ethics Validator)
    
    Use the returned ID to poll the status endpoint.
    """
    try:
        # Generate unique hypothesis ID
        hypothesis_id = f"hyp_{uuid.uuid4().hex[:12]}"
        
        logger.info(f"Creating hypothesis {hypothesis_id} for domain: {request.domain}")
        logger.debug(f"Request: {request.model_dump()}")
        
        # Initialize hypothesis record
        hypothesis_data = {
            "id": hypothesis_id,
            "status": HypothesisStatus.PENDING.value,
            "domain": request.domain.value,
            "goal": request.goal,
            "constraints": request.constraints.model_dump() if request.constraints else None,
            "cross_domains": request.cross_domains,
            "max_runtime_minutes": request.max_runtime_minutes,
            "user_id": request.user_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "completed_at": None,
            "error_message": None,
            "summary": None,
            "concept_map": None,
            "hypothesis_document": None,
            "evidence_packs": [],
            "cross_domain_transfers": [],
            "simulation_scorecard": None,
            "ethics_report": None,
            "provenance": []
        }
        
        # Save to database (MongoDB or in-memory fallback)
        if await mongodb_client.is_connected():
            await hypothesis_repository.create(hypothesis_data)
        else:
            hypothesis_store[hypothesis_id] = hypothesis_data
        
        # Add background task for hypothesis generation
        background_tasks.add_task(generate_hypothesis_async, hypothesis_id, request)
        
        logger.info(f"Hypothesis {hypothesis_id} queued for processing")
        
        return HypothesisCreateResponse(
            id=hypothesis_id,
            status=HypothesisStatus.PENDING,
            message=f"Hypothesis generation started. Use GET /v1/hypotheses/{hypothesis_id} to check status."
        )
        
    except Exception as e:
        logger.exception(f"Error creating hypothesis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create hypothesis: {str(e)}"
        )


@router.get(
    "/hypotheses/{hypothesis_id}",
    response_model=HypothesisResponse,
    summary="Get hypothesis by ID",
    description="Retrieve hypothesis details including status and results (if completed)"
)
async def get_hypothesis(hypothesis_id: str):
    """
    Get hypothesis by ID
    
    Returns the complete hypothesis data including:
    - Current status (pending/running/completed/failed)
    - Concept map
    - Hypothesis document
    - Evidence packs
    - Cross-domain transfers
    - Simulation scorecard
    - Ethics report
    - Provenance information
    """
    try:
        # Try MongoDB first, fallback to in-memory
        hypothesis_data = None
        
        if await mongodb_client.is_connected():
            hypothesis_data = await hypothesis_repository.get_by_id(hypothesis_id)
        elif hypothesis_id in hypothesis_store:
            hypothesis_data = hypothesis_store[hypothesis_id]
        
        if not hypothesis_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Hypothesis {hypothesis_id} not found"
            )
        
        logger.info(f"Retrieved hypothesis {hypothesis_id}, status: {hypothesis_data['status']}")
        
        # Sanitize data to ensure JSON serializability before Pydantic validation
        sanitized_data = sanitize_for_response(hypothesis_data)
        
        return HypothesisResponse(**sanitized_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error retrieving hypothesis {hypothesis_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve hypothesis: {str(e)}"
        )


@router.get(
    "/hypotheses",
    response_model=List[HypothesisResponse],
    summary="List all hypotheses",
    description="Get a list of all hypotheses with optional filtering"
)
async def list_hypotheses(
    status: HypothesisStatus = None,
    domain: str = None,
    user_id: str = None,
    limit: int = 50,
    offset: int = 0
):
    """
    List all hypotheses with optional filters
    
    Filters:
    - status: Filter by hypothesis status
    - domain: Filter by medical domain
    - user_id: Filter by user ID
    - limit: Maximum number of results (default: 50)
    - offset: Number of results to skip (default: 0)
    """
    try:
        # Try MongoDB first, fallback to in-memory
        if await mongodb_client.is_connected():
            # Build filters for MongoDB
            filters = {}
            if status:
                filters["status"] = status
            if domain:
                filters["domain"] = domain
            if user_id:
                filters["user_id"] = user_id
            
            # Get hypotheses from repository (already sorted by created_at descending)
            paginated = await hypothesis_repository.list(
                filters=filters,
                skip=offset,
                limit=limit
            )
            
            # Get total count for logging
            total_count = await hypothesis_repository.count(filters=filters)
            
        else:
            # Fallback to in-memory filtering
            filtered = list(hypothesis_store.values())
            
            if status:
                filtered = [h for h in filtered if h["status"] == status]
            
            if domain:
                filtered = [h for h in filtered if h["domain"] == domain]
            
            if user_id:
                filtered = [h for h in filtered if h.get("user_id") == user_id]
            
            # Sort by created_at descending
            filtered.sort(key=lambda x: x["created_at"], reverse=True)
            
            # Apply pagination
            total_count = len(filtered)
            paginated = filtered[offset:offset + limit]
        
        logger.info(f"Retrieved {len(paginated)} hypotheses (total: {total_count})")
        
        return [HypothesisResponse(**h) for h in paginated]
        
    except Exception as e:
        logger.exception(f"Error listing hypotheses: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list hypotheses: {str(e)}"
        )


@router.delete(
    "/hypotheses/{hypothesis_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete hypothesis",
    description="Delete a hypothesis by ID"
)
async def delete_hypothesis(hypothesis_id: str):
    """
    Delete a hypothesis
    
    This will remove the hypothesis and all associated data.
    """
    try:
        deleted = False
        
        # Try MongoDB first, fallback to in-memory
        if await mongodb_client.is_connected():
            deleted = await hypothesis_repository.delete(hypothesis_id)
        elif hypothesis_id in hypothesis_store:
            del hypothesis_store[hypothesis_id]
            deleted = True
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Hypothesis {hypothesis_id} not found"
            )
        
        logger.info(f"Deleted hypothesis {hypothesis_id}")
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error deleting hypothesis {hypothesis_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete hypothesis: {str(e)}"
        )
