
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl, Field
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import Agent
from agents.embedding_service import generate_embedding

router = APIRouter(prefix="/api/v1/agents", tags=["Agents"])


class AgentRegisterRequest(BaseModel):
    company_name: str = Field(min_length=2, max_length=255)
    industry_category: str = Field(min_length=2, max_length=100)
    webhook_url: HttpUrl
    interest_manifesto: str = Field(min_length=10)


@router.post("/register", status_code=201)
def register_agent(
    request: AgentRegisterRequest,
    db: Session = Depends(get_db),
):
    try:
        # Generate semantic embedding from agent interests
        embedding = generate_embedding(request.interest_manifesto)

        # Create agent with its embedding
        agent = Agent(
            company_name=request.company_name,
            industry_category=request.industry_category,
            webhook_url=str(request.webhook_url),
            interest_manifesto=request.interest_manifesto,
            interest_embedding=embedding,
        )

        db.add(agent)
        db.commit()
        db.refresh(agent)

        return {
            "message": "Agent registered successfully",
            "agent": {
                "id": str(agent.id),
                "company_name": agent.company_name,
                "industry_category": agent.industry_category,
                "webhook_url": agent.webhook_url,
                "interest_manifesto": agent.interest_manifesto,
                "trust_score": agent.trust_score,
                "embedding_dimensions": len(embedding),
            },
        }

    except Exception as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to register agent: {str(error)}",
        )
