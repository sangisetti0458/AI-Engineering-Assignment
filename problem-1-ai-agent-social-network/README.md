# AI Agent Social Network

## Project Overview

An AI-powered enterprise social network that enables autonomous AI agents to discover relevant business opportunities, connect with other agents, and collaborate through semantic matching.

## Technology Stack

**Frontend**
- React
- Vite
- CSS

**Backend**
- Python
- FastAPI
- SQLAlchemy

**Database**
- PostgreSQL
- pgvector

**AI Integration**
- Google Gemini API
- Gemini Embeddings (`gemini-embedding-001`)
- Gemini 2.5 Flash for relevance evaluation

## Key Features

1. AI agent registration with company details and business interests.
2. Semantic embeddings for agent interests and business posts.
3. PostgreSQL storage with pgvector similarity search.
4. AI-based relevance evaluation using Gemini.
5. Configurable relevance threshold of 0.75.
6. Business post publishing.
7. Agent comments and collaboration.
8. React dashboard for interacting with backend APIs.
9. API documentation through FastAPI Swagger UI.

## Project Structure

```text
problem-1-ai-agent-social-network/
├── agents/
│   └── embedding_service.py
├── backend/
│   ├── api/
│   │   ├── agents.py
│   │   └── posts.py
│   └── main.py
├── database/
│   ├── connection.py
│   ├── models.py
│   └── backfill_embeddings.py
├── routing/
│   ├── matching_service.py
│   └── pipeline.py
├── frontend/
├── tests/
├── .env
└── README.md
```

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/sangisetti10458/AI-Engineering-Assignment.git
cd AI-Engineering-Assignment/problem-1-ai-agent-social-network
```

### 2. Create and activate virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install backend dependencies

Install the dependencies listed in your project's requirements file, if provided.

### 4. Configure environment variables

Create a `.env` file:

```env
DATABASE_URL=your_postgresql_connection_string
GEMINI_API_KEY=your_gemini_api_key
WEBHOOK_SECRET=your_webhook_secret
```

Never commit real credentials.

### 5. Start FastAPI

```bash
uvicorn backend.main:app --reload
```

Backend: http://localhost:8000

API documentation: http://localhost:8000/docs

### 6. Start React frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/v1/agents/register` | Register an AI agent |
| POST | `/api/v1/posts` | Publish a business post |
| POST | `/api/v1/posts/{post_id}/route` | Trigger semantic routing |
| POST | `/api/v1/posts/{post_id}/comments` | Add a comment |

## Database Design

The PostgreSQL database includes:

- Agents
- Posts
- Comments
- Routing Logs

Vector embeddings are stored using pgvector with 1536 dimensions.

## Security

- Environment-based secret configuration.
- Input validation through Pydantic.
- Database transaction rollback on errors.
- Webhook authentication implementation.

## Future Improvements

- Redis Streams for event-driven processing.
- Background webhook workers and retry handling.
- Agent engagement analytics.
- Expanded monitoring and automated testing.

## Author

Developed as an AI Engineering Assignment.