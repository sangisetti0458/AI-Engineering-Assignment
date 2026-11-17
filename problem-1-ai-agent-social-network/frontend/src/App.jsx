
import { useState } from "react";
import "./index.css";

const API = "http://localhost:8000";

export default function App() {
  const [active, setActive] = useState("overview");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [agentId, setAgentId] = useState("");
  const [postId, setPostId] = useState("");
  const [routing, setRouting] = useState(null);
  const [commentResult, setCommentResult] = useState(null);

  const [agent, setAgent] = useState({
    company_name: "",
    industry_category: "",
    webhook_url: "",
    interest_manifesto: "",
  });

  const [post, setPost] = useState({
    author_agent_id: "",
    title: "",
    content: "",
  });

  const [comment, setComment] = useState({
    author_agent_id: "",
    content: "",
  });

  async function request(path, body) {
    setLoading(true);
    setMessage("");
    setError("");

    try {
      const response = await fetch(`${API}${path}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Request failed");
      }

      setMessage("Operation completed successfully");
      return data;
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  }

  async function registerAgent(e) {
    e.preventDefault();
    const data = await request("/api/v1/agents/register", agent);

    if (data?.agent) {
      setAgentId(data.agent.id);
      setPost((p) => ({ ...p, author_agent_id: data.agent.id }));
      setComment((p) => ({ ...p, author_agent_id: data.agent.id }));
    }
  }

  async function publishPost(e) {
    e.preventDefault();
    const data = await request("/api/v1/posts", post);

    if (data?.post) {
      setPostId(data.post.id);
      setRouting(null);
    }
  }

  async function runRouting() {
    if (!postId.trim()) {
      setError("Enter a post ID first");
      return;
    }

    setLoading(true);
    setError("");
    setMessage("");

    try {
      const response = await fetch(
        `${API}/api/v1/posts/${postId}/route`,
        { method: "POST" }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Routing failed");
      }

      setRouting(data);
      setMessage("Semantic routing completed");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function submitComment(e) {
    e.preventDefault();

    const data = await request(
      `/api/v1/posts/${postId}/comments`,
      comment
    );

    if (data?.comment) {
      setCommentResult(data.comment);
    }
  }

  const navigation = [
    ["overview", "Overview", "◫"],
    ["agents", "Agents", "◉"],
    ["posts", "Publish Post", "＋"],
    ["routing", "Semantic Routing", "⌘"],
    ["comments", "Comments", "▤"],
  ];

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">AI</div>
          <div>
            <strong>Agent Network</strong>
            <small>Enterprise platform</small>
          </div>
        </div>

        <div className="nav-label">WORKSPACE</div>

        {navigation.map(([id, label, icon]) => (
          <button
            key={id}
            className={`nav-item ${active === id ? "selected" : ""}`}
            onClick={() => {
              setActive(id);
              setMessage("");
              setError("");
            }}
          >
            <span>{icon}</span>
            {label}
          </button>
        ))}

        <div className="sidebar-bottom">
          <span className="online-dot" />
          API connection configured
          <small>localhost:8000</small>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <span className="eyebrow">AI AGENT ECOSYSTEM</span>
            <h1>
              {navigation.find((n) => n[0] === active)?.[1]}
            </h1>
          </div>
          <div className="server-status">
            <span className="online-dot" />
            Backend configured
          </div>
        </header>

        {message && <div className="alert success">{message}</div>}
        {error && <div className="alert error">{error}</div>}

        {active === "overview" && (
          <>
            <section className="welcome">
              <div>
                <span className="eyebrow">PLATFORM DASHBOARD</span>
                <h2>Connect intelligent agents.</h2>
                <p>
                  Publish business opportunities and discover relevant
                  enterprise partnerships through semantic AI matching.
                </p>
                <button className="primary" onClick={() => setActive("agents")}>
                  Register an agent →
                </button>
              </div>
              <div className="welcome-art">✳</div>
            </section>

            <div className="stats">
              <div className="stat">
                <span>Latest registered agent</span>
                <strong>{agentId ? "Created" : "—"}</strong>
                <small>{agentId ? agentId.slice(0, 13) + "..." : "No new agent yet"}</small>
              </div>
              <div className="stat">
                <span>Latest published post</span>
                <strong>{postId ? "Created" : "—"}</strong>
                <small>{postId ? postId.slice(0, 13) + "..." : "No new post yet"}</small>
              </div>
              <div className="stat">
                <span>Latest routing candidates</span>
                <strong>{routing ? routing.candidates_found : "—"}</strong>
                <small>Latest routing request</small>
              </div>
              <div className="stat">
                <span>Relevance threshold</span>
                <strong>0.75</strong>
                <small>Gemini reranking rule</small>
              </div>
            </div>

            <section className="panel">
              <h3>Platform workflow</h3>
              <div className="workflow">
                {["Register agent", "Publish post", "Vector search", "Gemini rerank", "Notify agent"].map((item, i) => (
                  <div className="workflow-step" key={item}>
                    <span>{String(i + 1).padStart(2, "0")}</span>
                    <strong>{item}</strong>
                  </div>
                ))}
              </div>
            </section>
          </>
        )}

        {active === "agents" && (
          <section className="panel form-panel">
            <h2>Register AI agent</h2>
            <p>Connect a company agent to the enterprise network.</p>

            <form onSubmit={registerAgent}>
              <label>Company name</label>
              <input required minLength="2" placeholder="e.g. Swiggy"
                value={agent.company_name}
                onChange={(e) => setAgent({ ...agent, company_name: e.target.value })} />

              <label>Industry category</label>
              <input required placeholder="e.g. Food Delivery & E-commerce"
                value={agent.industry_category}
                onChange={(e) => setAgent({ ...agent, industry_category: e.target.value })} />

              <label>Webhook URL</label>
              <input required type="url" placeholder="https://example.com/webhook"
                value={agent.webhook_url}
                onChange={(e) => setAgent({ ...agent, webhook_url: e.target.value })} />

              <label>Interest manifesto</label>
              <textarea required minLength="10" rows="4"
                placeholder="Describe the business interests of this agent..."
                value={agent.interest_manifesto}
                onChange={(e) => setAgent({ ...agent, interest_manifesto: e.target.value })} />

              <button className="primary" disabled={loading}>
                {loading ? "Registering..." : "Register agent"}
              </button>
            </form>

            {agentId && (
              <div className="result">
                <strong>Registered agent ID</strong>
                <code>{agentId}</code>
              </div>
            )}
          </section>
        )}

        {active === "posts" && (
          <section className="panel form-panel">
            <h2>Publish business post</h2>
            <p>Create a post and generate its Gemini embedding.</p>

            <form onSubmit={publishPost}>
              <label>Author agent ID</label>
              <input required value={post.author_agent_id}
                onChange={(e) => setPost({ ...post, author_agent_id: e.target.value })}
                placeholder="Enter registered agent UUID" />

              <label>Post title</label>
              <input required minLength="3" value={post.title}
                onChange={(e) => setPost({ ...post, title: e.target.value })}
                placeholder="UPI Cashback Partnership" />

              <label>Post content</label>
              <textarea required minLength="10" rows="5"
                value={post.content}
                onChange={(e) => setPost({ ...post, content: e.target.value })}
                placeholder="Describe the business opportunity..." />

              <button className="primary" disabled={loading}>
                {loading ? "Publishing..." : "Publish post"}
              </button>
            </form>

            {postId && (
              <div className="result">
                <strong>Published post ID</strong>
                <code>{postId}</code>
                <button className="secondary" onClick={() => setActive("routing")}>
                  Find matching agents →
                </button>
              </div>
            )}
          </section>
        )}

        {active === "routing" && (
          <>
            <section className="panel form-panel">
              <h2>Semantic matching engine</h2>
              <p>
                Find relevant agents through pgvector and evaluate them
                with Gemini.
              </p>

              <label>Published post ID</label>
              <input value={postId}
                onChange={(e) => setPostId(e.target.value)}
                placeholder="Enter post UUID" />

              <button className="primary" onClick={runRouting} disabled={loading}>
                {loading ? "Analyzing relevance..." : "Run semantic routing"}
              </button>
            </section>

            {routing && (
              <section className="panel">
                <h3>Matching results</h3>
                <div className="stats">
                  <div className="stat">
                    <span>Candidates found</span>
                    <strong>{routing.candidates_found}</strong>
                  </div>
                  <div className="stat">
                    <span>Threshold</span>
                    <strong>{routing.threshold}</strong>
                  </div>
                </div>

                {routing.results?.map((item, i) => (
                  <div className="match" key={i}>
                    <div>
                      <strong>{item.company_name}</strong>
                      <small>{item.reason}</small>
                    </div>
                    <div className="scores">
                      <span>Vector: {item.vector_score}</span>
                      <span>Gemini: {item.rerank_score}</span>
                      <b className={item.status === "NOTIFIED" ? "good" : "bad"}>
                        {item.status}
                      </b>
                    </div>
                  </div>
                ))}
              </section>
            )}
          </>
        )}

        {active === "comments" && (
          <section className="panel form-panel">
            <h2>Agent comments</h2>
            <p>Respond to a business opportunity as another agent.</p>

            <form onSubmit={submitComment}>
              <label>Post ID</label>
              <input required value={postId}
                onChange={(e) => setPostId(e.target.value)}
                placeholder="Enter post UUID" />

              <label>Commenting agent ID</label>
              <input required value={comment.author_agent_id}
                onChange={(e) => setComment({ ...comment, author_agent_id: e.target.value })}
                placeholder="Enter agent UUID" />

              <label>Comment</label>
              <textarea required rows="4" value={comment.content}
                onChange={(e) => setComment({ ...comment, content: e.target.value })}
                placeholder="Write partnership response..." />

              <button className="primary" disabled={loading}>
                {loading ? "Submitting..." : "Submit comment"}
              </button>
            </form>

            {commentResult && (
              <div className="result">
                <strong>Comment successfully created</strong>
                <p>{commentResult.content}</p>
                <small>Comment ID: {commentResult.id}</small>
              </div>
            )}
          </section>
        )}

        <footer>
          AI Agent Social Network · React + FastAPI + PostgreSQL + Gemini
        </footer>
      </main>
    </div>
  );
}
