import { useState, useRef, useEffect } from "react";

const FLASK_URL = import.meta.env.VITE_API_URL || "http://localhost:5000/ask";
import "./App.css";

function App() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [refOpen, setRefOpen] = useState(false);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  async function handleAsk() {
    const q = question.trim();
    if (!q) return;

    setLoading(true);
    setError(null);
    setResult(null);
    setRefOpen(false);

    try {
      const res = await fetch(FLASK_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q }),
      });
      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleAsk();
    }
  }

  return (
    <>
      <div className="wrap">
        {/* header */}
        <div className="header">
          <h1>
            HARMAN <span>HR</span> Assistant
          </h1>
          <p>Ask anything about the employee handbook</p>
        </div>

        {/* input */}
        <div className="input-row">
          <textarea
            ref={inputRef}
            rows={1}
            placeholder="e.g. How many casual leaves do I get?"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <button
            className="ask-btn"
            onClick={handleAsk}
            disabled={loading || !question.trim()}
          >
            {loading ? "Asking…" : "Ask →"}
          </button>
        </div>

        {/* loading */}
        {loading && (
          <div className="loading">
            <div className="dot-pulse">
              <span />
              <span />
              <span />
            </div>
            Searching handbook…
          </div>
        )}

        {/* error */}
        {error && <div className="error-box">⚠ {error}</div>}

        {/* result */}
        {result && (
          <div className="result-card">
            {/* answer */}
            <div className="answer-body">
              <div className="answer-label">Answer</div>
              <div className="answer-text">{result.answer}</div>
            </div>

            {/* references toggle */}
            {result.references?.length > 0 && (
              <>
                <div
                  className="ref-toggle"
                  onClick={() => setRefOpen((o) => !o)}
                >
                  <span className="ref-toggle-label">
                    References
                    <span className="ref-count">
                      {result.references.length}
                    </span>
                  </span>
                  <span className={`chevron ${refOpen ? "open" : ""}`}>▼</span>
                </div>

                {refOpen && (
                  <div className="ref-panel">
                    {result.references.map((ref, i) => (
                      <div className="ref-item" key={i}>
                        <span className="ref-section">{ref.section}</span>
                        <div className="ref-meta">
                          <span className="ref-page">p. {ref.page}</span>
                          <span className="ref-score">{ref.relevance}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </div>
    </>
  );
}

export default App;
