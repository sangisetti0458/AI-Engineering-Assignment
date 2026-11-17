
from sqlalchemy.orm import Session

from database.models import Agent, Post


def find_similar_agents(
    db: Session,
    post_id: str,
    limit: int = 50,
):
    """
    Find agents whose interests are semantically similar
    to a published post using pgvector cosine distance.
    """

    # 1. Retrieve the post
    post = db.query(Post).filter(
        Post.id == post_id
    ).first()

    if not post:
        raise ValueError("Post not found")

    if post.post_embedding is None:
        raise ValueError("Post embedding is missing")

    # 2. Calculate cosine distance between post and agent embeddings
    distance = Agent.interest_embedding.cosine_distance(
        post.post_embedding
    ).label("distance")

    # 3. Find the top matching agents
    results = (
        db.query(Agent, distance)
        .filter(
            Agent.id != post.author_agent_id,
            Agent.interest_embedding.isnot(None),
        )
        .order_by(distance.asc())
        .limit(limit)
        .all()
    )

    # 4. Format matching results
    matches = []

    for agent, cosine_distance in results:
        similarity_score = 1 - cosine_distance

        matches.append({
            "agent_id": str(agent.id),
            "company_name": agent.company_name,
            "industry_category": agent.industry_category,
            "vector_score": round(similarity_score, 4),
            "cosine_distance": round(cosine_distance, 4),
        })

    return matches
