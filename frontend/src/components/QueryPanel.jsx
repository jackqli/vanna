import { useState } from 'react'
import axios from 'axios'
import ResultsDisplay from './ResultsDisplay'

function QueryPanel() {
  const [question, setQuestion] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleAskQuestion = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await axios.post('/api/ask', { question })
      setResult(response.data)
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to process question')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="query-panel">
      <div className="section">
        <h2>Ask a Question</h2>
        <p className="section-description">
          Ask questions about your data in natural language, and Vanna will generate and execute the SQL query.
        </p>
        <form onSubmit={handleAskQuestion}>
          <div className="form-group">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="e.g., How many users are there?"
              className="question-input"
              required
            />
          </div>
          <button type="submit" disabled={loading}>
            {loading ? 'Processing...' : 'Ask Question'}
          </button>
        </form>
      </div>

      {error && (
        <div className="message error">
          {error}
        </div>
      )}

      {result && (
        <div className="results-section">
          <div className="section">
            <h3>Generated SQL</h3>
            <pre className="sql-display">{result.sql}</pre>
          </div>

          {result.results && result.results.length > 0 && (
            <div className="section">
              <h3>Query Results</h3>
              <ResultsDisplay results={result.results} columns={result.columns} />
            </div>
          )}

          {result.results && result.results.length === 0 && (
            <div className="message info">
              Query executed successfully but returned no results.
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default QueryPanel
