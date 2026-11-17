from database.models import Comment, RoutingLog
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import Agent, Post
from agents.embedding_service import generate_embedding

router = APIRouter(prefix="/api/v1/posts", tags=["Posts"])


class PostCreateRequest(BaseModel):
    author_agent_id: str
    title: str = Field(min_length=3, max_length=255)
    content: str = Field(min_length=10)


@router.post("", status_code=201)
def create_post(
    request: PostCreateRequest,
    db: Session = Depends(get_db),
):
    try:
        agent = db.query(Agent).filter(
            Agent.id == request.author_agent_id
        ).first()

        if not agent:
            raise HTTPException(
                status_code=404,
                detail="Author agent not found",
            )

        # Combine title and content for semantic understanding
        post_text = f"{request.title}\n{request.content}"

        # Generate Gemini embedding
        embedding = generate_embedding(post_text)

        # Save post and its embedding
        post = Post(
            author_agent_id=agent.id,
            title=request.title,
            content=request.content,
            post_embedding=embedding,
            created_at=datetime.now(timezone.utc),
        )

        db.add(post)
        db.commit()
        db.refresh(post)

        return {
            "message": "Post published successfully",
            "post": {
                "id": str(post.id),
                "author_agent_id": str(post.author_agent_id),
                "title": post.title,
                "content": post.content,
                "created_at": post.created_at.isoformat(),
                "embedding_dimensions": len(embedding),
            },
        }

    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to publish post",
        )



class CommentCreateRequest(BaseModel):
    author_agent_id: str
    content: str = Field(min_length=1, max_length=5000)


@router.post("/{post_id}/comments", status_code=201)
def create_comment(
    post_id: str,
    request: CommentCreateRequest,
    db: Session = Depends(get_db),
):
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    agent = db.query(Agent).filter(
        Agent.id == request.author_agent_id
    ).first()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    if agent.id == post.author_agent_id:
        raise HTTPException(
            status_code=400,
            detail="Post author cannot comment on their own post",
        )

    comment = Comment(
        post_id=post.id,
        author_agent_id=agent.id,
        content=request.content,
        created_at=datetime.now(timezone.utc),
    )

    db.add(comment)

    # Record engagement from a previously notified agent
    log = db.query(RoutingLog).filter(
        RoutingLog.post_id == post.id,
        RoutingLog.target_agent_id == agent.id,
        RoutingLog.status == "NOTIFIED",
    ).first()

    if log:
        log.status = "ENGAGED"

    db.commit()
    db.refresh(comment)

    return {
        "message": "Comment added successfully",
        "comment": {
            "id": str(comment.id),
            "post_id": str(comment.post_id),
            "author_agent_id": str(comment.author_agent_id),
            "content": comment.content,
            "created_at": comment.created_at.isoformat(),
        },
    }
