
from database.connection import SessionLocal
from database.models import Agent
from agents.embedding_service import generate_embedding


def backfill_agent_embeddings():
    db = SessionLocal()

    try:
        # Find agents whose embeddings are missing
        agents = db.query(Agent).filter(
            Agent.interest_embedding.is_(None)
        ).all()

        print(f"Found {len(agents)} agents without embeddings.")

        for agent in agents:
            print(f"Generating embedding for {agent.company_name}...")

            embedding = generate_embedding(agent.interest_manifesto)

            agent.interest_embedding = embedding

        db.commit()

        print("Agent embedding backfill completed successfully.")

    except Exception as error:
        db.rollback()
        print(f"Backfill failed: {error}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    backfill_agent_embeddings()
